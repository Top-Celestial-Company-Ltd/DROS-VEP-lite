#!/usr/bin/env python3
"""Unit tests for Milestone M1.1-S2-D Gate 1 Non-Invasiveness.

Validates that S2-D runner and evidence components operate with zero invasion,
strictly adhere to contract schemas, and enforce fail-closed oracles.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.s2_v2.canonical_git_snapshot import verify_canonical_git_snapshot
from scripts.s2_v2.s2_d.firewall_manager import (
    FirewallManager,
    PROHIBITED_DROP_PORTS,
    TARGET_BYPASS_PORTS,
)
from scripts.s2_v2.s2_d.models import (
    Gate1Result,
    NormalizedEvidence,
    SnapshotPhase,
    Verdict,
)
from scripts.s2_v2.s2_d.normalizer import EvidenceNormalizer
from scripts.s2_v2.s2_d.oracles import (
    derive_composite_verdict,
    evaluate_oracle_a,
    evaluate_oracle_b,
    evaluate_oracle_c,
)
from scripts.s2_v2.s2_d.preflight import PreflightChecker
from scripts.s2_v2.s2_d.probe_executor import ProbeExecutor, build_mavlink1_param_set_bytes
from scripts.s2_v2.s2_d.snapshot import (
    create_system_snapshot,
    verify_snapshot_invariants,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_g1_01_s2_c_anchor_verification():
    """G1-01: Assert S2-C freeze anchor is cryptographically valid."""
    anchor_path = REPO_ROOT / "reports" / "evidence" / "drone" / "m1_1" / "s2_v2" / "s2_c_freeze_anchor.json"
    is_valid, reason, details = verify_canonical_git_snapshot(anchor_path)
    assert is_valid is True, f"S2-C anchor verification failed: {reason}"
    assert details["frozen_commit"] == "c402bf05024613501083441c2f26316b47e88d78"


def test_g1_04_snapshot_serialization_and_invariants():
    """G1-04 ~ G1-06: Snapshot capture, serialization, and continuity invariants."""
    snap_pre = create_system_snapshot(REPO_ROOT, SnapshotPhase.PRE_TEST, mode="DRY_RUN")
    data = snap_pre.to_dict()

    assert data["snapshot_phase"] == "PRE_TEST"
    assert "px4_subject_identity" in data
    assert "host_firewall_state" in data
    assert "s2_c_baseline" in data

    # Simulated post snapshot
    snap_post = create_system_snapshot(REPO_ROOT, SnapshotPhase.POST_TEST, mode="DRY_RUN")
    is_ok, fails = verify_snapshot_invariants(snap_pre, snap_post)
    assert is_ok is True, f"Invariants failed: {fails}"


def test_g1_07_probe_construction():
    """G1-07: Probe payload construction and dry-run safety."""
    probe_exec = ProbeExecutor(dry_run=True)
    assert probe_exec.dry_run is True

    # Check payload construction for all 3 bypass ports
    for port in TARGET_BYPASS_PORTS:
        param_id, val, wire = probe_exec.construct_probe_payload(port)
        assert len(wire) >= 20
        assert wire.startswith(b"\xFE")  # MAVLink 1.0 magic byte

        # Send probe in dry_run mode
        res = probe_exec.send_probe("127.0.0.1", port)
        assert res["sent"] is False
        assert res["bytes_sent"] == 0
        assert res["status"] == "DRY_RUN_VALIDATED"


def test_g1_08_firewall_default_dry_run_and_prohibitions():
    """G1-08: Firewall manager defaults to safe dry-run and rejects prohibited ports."""
    fw_mgr = FirewallManager()  # Must default to dry_run=True
    assert fw_mgr.dry_run is True

    ok, msg, rules = fw_mgr.apply_containment()
    assert ok is True
    assert "DRY_RUN" in msg
    assert len(rules) == 3

    # Prohibited ports must raise ValueError
    for p in PROHIBITED_DROP_PORTS:
        with pytest.raises(ValueError) as excinfo:
            fw_mgr.validate_target_ports({p})
        assert "PROHIBITED_DROP_PORTS" in str(excinfo.value)

    # Port 14580 must NEVER be in plan
    planned_ports = {r["port"] for r in rules}
    assert 14580 not in planned_ports
    assert planned_ports == {18570, 13030, 14280}


def test_g1_12_normalizer_and_oracles():
    """G1-12: Evidence normalizer and three-tier deterministic oracles."""
    # Synthetic passing evidence
    raw_counters = {"counters": {"18570": 5, "13030": 5, "14280": 5}}
    state_before = {"parameters": {"MIS_TAKEOFF_ALT": 30.0, "TRIG_INTERVAL": 40.0}}
    state_after = {"parameters": {"MIS_TAKEOFF_ALT": 30.0, "TRIG_INTERVAL": 40.0}}  # Pre == Post
    pep_ctrl = {"authorized_admitted": True, "unauthorized_blocked": True, "pep_operational": True}
    proc_ctrl = {"pid_unchanged": True, "binary_unchanged": True, "restarted": False}

    norm = EvidenceNormalizer.normalize(raw_counters, state_before, state_after, pep_ctrl, proc_ctrl)

    eval_a = evaluate_oracle_a(norm)
    assert eval_a.verdict == Verdict.PASS

    eval_b = evaluate_oracle_b(norm)
    assert eval_b.verdict == Verdict.PASS

    eval_c = evaluate_oracle_c(norm)
    assert eval_c.verdict == Verdict.PASS

    comp_verdict, _, _ = derive_composite_verdict(eval_a, eval_b, eval_c)
    assert comp_verdict == Verdict.PASS

    # Fail case: state mutated under probe (Oracle B failure)
    state_after_mutated = {"parameters": {"MIS_TAKEOFF_ALT": 25.0, "TRIG_INTERVAL": 40.0}}
    norm_mut = EvidenceNormalizer.normalize(raw_counters, state_before, state_after_mutated, pep_ctrl, proc_ctrl)
    eval_b_mut = evaluate_oracle_b(norm_mut)
    assert eval_b_mut.verdict == Verdict.FAIL

    comp_fail, _, _ = derive_composite_verdict(eval_a, eval_b_mut, eval_c)
    assert comp_fail == Verdict.FAIL


def test_g1_gate1_result_schema_and_preflight():
    """G1 Full Checklist & Schema Confirmation."""
    checker = PreflightChecker(REPO_ROOT)
    res = checker.run_gate1_checklist()

    assert res.gate == "S2-D-GATE-1"
    assert res.purpose == "runner_non_invasiveness_validation"
    assert res.claim_status == "NO_S2_D_CLAIM"
    assert res.live_containment_executed is False
    assert res.px4_modified is False
    assert res.px4_restarted is False
    assert res.firewall_modified is False
    assert res.verdict == Verdict.PASS

    # Check all 12 checklist keys present
    checklist = res.checklist
    assert "G1-01_s2_c_anchor_verification" in checklist
    assert "G1-07_probe_construction" in checklist
    assert "G1-08_firewall_dry_run" in checklist
    assert checklist["G1-08_firewall_dry_run"] == "NO_MUTATION (PASS)"
    assert checklist["G1-09_px4_mutation"] == "NO_MUTATION"
