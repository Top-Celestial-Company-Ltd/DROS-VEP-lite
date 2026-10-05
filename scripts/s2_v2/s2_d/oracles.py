#!/usr/bin/env python3
"""Deterministic oracles for Milestone M1.1-S2-D evaluation.

Evaluates normalized evidence strictly according to the S2-D Test Contract.
"""
from __future__ import annotations

from typing import List, Tuple

from .models import NormalizedEvidence, OracleEvaluation, Verdict


def evaluate_oracle_a(evidence: NormalizedEvidence) -> OracleEvaluation:
    """Oracle A: Network Enforcement Evidence.

    Verifies that host perimeter rules registered packet drops for target bypass ports.
    """
    net = evidence.network_enforcement
    if not net or "per_port_drops" not in net:
        return OracleEvaluation(
            oracle_name="Oracle A: Network Enforcement Evidence",
            verdict=Verdict.INDETERMINATE,
            rationale="No network enforcement counter evidence present",
            metrics=net,
        )

    per_port = net["per_port_drops"]
    total_drops = net.get("total_drops", 0)
    all_hit = net.get("all_target_ports_hit", False)

    if total_drops == 0:
        return OracleEvaluation(
            oracle_name="Oracle A: Network Enforcement Evidence",
            verdict=Verdict.FAIL,
            rationale="Zero packet drops recorded by host perimeter filter under probe stimulation",
            metrics=net,
        )

    if not all_hit:
        return OracleEvaluation(
            oracle_name="Oracle A: Network Enforcement Evidence",
            verdict=Verdict.INDETERMINATE,
            rationale=f"Not all target bypass ports registered drop counters: {per_port}",
            metrics=net,
        )

    return OracleEvaluation(
        oracle_name="Oracle A: Network Enforcement Evidence",
        verdict=Verdict.PASS,
        rationale=f"Host perimeter rules successfully dropped probe packets across all target ports (Total drops: {total_drops})",
        metrics=net,
    )


def evaluate_oracle_b(evidence: NormalizedEvidence) -> OracleEvaluation:
    """Oracle B: Target State Integrity (Execution Oracle).

    Verifies that target parameter state remained invariant across mutation probe injection.
    """
    state = evidence.state_integrity
    if not state or "parameters" not in state:
        return OracleEvaluation(
            oracle_name="Oracle B: Target State Integrity",
            verdict=Verdict.INDETERMINATE,
            rationale="No target parameter readback evidence present",
            metrics=state,
        )

    params = state["parameters"]
    if not params:
        return OracleEvaluation(
            oracle_name="Oracle B: Target State Integrity",
            verdict=Verdict.INDETERMINATE,
            rationale="Empty parameter dataset; cannot evaluate state invariance",
            metrics=state,
        )

    any_mutated = state.get("any_parameter_mutated", False)
    if any_mutated:
        mutated_items = {k: v for k, v in params.items() if v.get("mutated")}
        return OracleEvaluation(
            oracle_name="Oracle B: Target State Integrity",
            verdict=Verdict.FAIL,
            rationale=f"Containment breach: Target parameter state mutated under probe: {mutated_items}",
            metrics=state,
        )

    return OracleEvaluation(
        oracle_name="Oracle B: Target State Integrity",
        verdict=Verdict.PASS,
        rationale="Target parameter state remained completely invariant across all probe stimulations (Pre == Post, Delta = 0)",
        metrics=state,
    )


def evaluate_oracle_c(evidence: NormalizedEvidence) -> OracleEvaluation:
    """Oracle C: Control Path Preservation (Health / Negative Control).

    Verifies that the designated DROS-mediated control path remains operational
    and that the PX4 flight control process was not restarted or crashed.
    """
    ctrl = evidence.control_path_preservation
    if not ctrl:
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.INDETERMINATE,
            rationale="No control path preservation evidence present",
            metrics=ctrl,
        )

    # 1. Process continuity
    if ctrl.get("px4_restarted", False):
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.FAIL,
            rationale="PX4 flight-control process crashed or restarted during containment testing",
            metrics=ctrl,
        )

    if not ctrl.get("px4_pid_unchanged", True):
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.FAIL,
            rationale="PX4 PID changed across test execution",
            metrics=ctrl,
        )

    if not ctrl.get("px4_binary_unchanged", True):
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.FAIL,
            rationale="PX4 binary executable was modified during testing",
            metrics=ctrl,
        )

    # 2. PEP path operationality
    if not ctrl.get("pep_operational", False):
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.FAIL,
            rationale="DROS PEP designated control path is not operational",
            metrics=ctrl,
        )

    if not ctrl.get("authorized_request_admitted", False):
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.FAIL,
            rationale="Authorized control request on mediated path (14540) failed to reach execution target",
            metrics=ctrl,
        )

    if not ctrl.get("unauthorized_request_blocked", False):
        return OracleEvaluation(
            oracle_name="Oracle C: Control Path Preservation",
            verdict=Verdict.FAIL,
            rationale="Unauthorized request on mediated path was not blocked at PEP boundary",
            metrics=ctrl,
        )

    return OracleEvaluation(
        oracle_name="Oracle C: Control Path Preservation",
        verdict=Verdict.PASS,
        rationale="Designated PEP-mediated control path preserved (14540 operational, authorized admitted, unauthorized blocked) and PX4 runtime continuity maintained",
        metrics=ctrl,
    )


def derive_composite_verdict(
    eval_a: OracleEvaluation,
    eval_b: OracleEvaluation,
    eval_c: OracleEvaluation,
) -> Tuple[Verdict, str, List[OracleEvaluation]]:
    """Derive composite S2-D verdict according to four-state contract schema."""
    evaluations = [eval_a, eval_b, eval_c]

    # Check for any FAIL
    fails = [e for e in evaluations if e.verdict == Verdict.FAIL]
    if fails:
        reasons = [f"{e.oracle_name}: {e.rationale}" for e in fails]
        return Verdict.FAIL, f"Containment verification failed: {'; '.join(reasons)}", evaluations

    # Check for any ABORTED
    aborted = [e for e in evaluations if e.verdict == Verdict.ABORTED]
    if aborted:
        reasons = [f"{e.oracle_name}: {e.rationale}" for e in aborted]
        return Verdict.ABORTED, f"Testing aborted: {'; '.join(reasons)}", evaluations

    # Check for any INDETERMINATE
    indeterminate = [e for e in evaluations if e.verdict == Verdict.INDETERMINATE]
    if indeterminate:
        reasons = [f"{e.oracle_name}: {e.rationale}" for e in indeterminate]
        return Verdict.INDETERMINATE, f"Inconclusive observation: {'; '.join(reasons)}", evaluations

    # All must be PASS
    return Verdict.PASS, "All mandatory Oracles (A, B, C) strictly satisfied", evaluations
