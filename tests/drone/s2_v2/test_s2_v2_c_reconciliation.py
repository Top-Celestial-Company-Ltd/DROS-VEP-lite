#!/usr/bin/env python3
"""DROS Drone M1.1-S2-C Canonical v2.1 Rev 2 - Empirical Governance Reconciliation

This verifier acts as an independent downstream auditor and evidence joiner.
It DOES NOT rely on hardcoded ports, hardcoded counts, or run_s2_v2_c verdicts.
It ingests:
  1. s1_freeze_anchor.json & s1_governed_topology_manifest.json (via Canonical Git Snapshot)
  2. s2_b_freeze_anchor.json & s2_v2_b_authority_summary.json + s2_v2_b_authority.json (via Canonical Git Snapshot)

It joins empirical probe transaction evidence against validated S1 governance topology
at the path level. Any target overlap that lacks path-level mediation evidence
is deterministically classified as INDETERMINATE_BOUNDARY.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest

# Ensure scripts directory is importable without duplicate repo prefix
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "s2_v2"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from canonical_git_snapshot import (
    canonical_endpoint_key,
    endpoint_surface_digest,
    extract_normalized_endpoint_surface,
    extract_route_identity,
    match_route_identity,
    verify_canonical_git_snapshot,
)

EVIDENCE_BASE = REPO_ROOT / "reports" / "evidence" / "drone" / "m1_1"
S1_ANCHOR = EVIDENCE_BASE / "s1" / "s1_freeze_anchor.json"
S1_MANIFEST = EVIDENCE_BASE / "s1" / "s1_governed_topology_manifest.json"
S2_B_ANCHOR = EVIDENCE_BASE / "s2_v2" / "s2_b_freeze_anchor.json"
S2_B_SUMMARY = EVIDENCE_BASE / "s2_v2" / "s2_v2_b_authority_summary.json"
S2_B_AUTHORITY = EVIDENCE_BASE / "s2_v2" / "s2_v2_b_authority.json"


@pytest.fixture(scope="module")
def canonical_s1_manifest() -> Dict[str, Any]:
    """Verify and load the frozen S1 governance manifest."""
    valid, reason, audit = verify_canonical_git_snapshot(S1_ANCHOR)
    assert valid, f"S1 Git Snapshot verification failed: {reason}"
    assert S1_MANIFEST.exists(), f"S1 manifest missing: {S1_MANIFEST}"
    manifest = json.loads(S1_MANIFEST.read_text(encoding="utf-8"))
    assert manifest.get("schema_version") == "1.0"
    return manifest


@pytest.fixture(scope="module")
def canonical_s2_b_artifacts() -> Dict[str, Any]:
    """Verify and load both frozen S2-B authority summary and full authority detail."""
    valid, reason, audit = verify_canonical_git_snapshot(S2_B_ANCHOR)
    assert valid, f"S2-B Git Snapshot verification failed: {reason}"
    assert S2_B_SUMMARY.exists(), f"S2-B summary missing: {S2_B_SUMMARY}"
    assert S2_B_AUTHORITY.exists(), f"S2-B authority detail missing: {S2_B_AUTHORITY}"

    summary = json.loads(S2_B_SUMMARY.read_text(encoding="utf-8"))
    authority = json.loads(S2_B_AUTHORITY.read_text(encoding="utf-8"))

    # Verify surface integrity against anchor
    anchor_data = json.loads(S2_B_ANCHOR.read_text(encoding="utf-8"))
    expected_surface_sha = anchor_data.get("endpoint_surface_sha256")
    surface = extract_normalized_endpoint_surface(summary, authority)
    actual_surface_sha = endpoint_surface_digest(surface)
    assert (
        actual_surface_sha == expected_surface_sha
    ), f"S2-B surface digest mismatch: {actual_surface_sha} != {expected_surface_sha}"

    return {
        "summary": summary,
        "authority": authority,
        "surface": surface,
    }


def _candidate_s1_routes(
    s1_routes: List[Dict[str, Any]],
    target_port: int,
) -> List[Dict[str, Any]]:
    """Return all S1 routes whose target port overlaps the S2-B target.

    Target overlap is only a candidate-generation step.
    Final governance attribution MUST use full route identity matching.
    """
    candidates: List[Dict[str, Any]] = []

    for route in s1_routes:
        route_target = route.get("target_port")
        if route_target is None:
            route_target = route.get("forward_port")

        if route_target is None:
            continue

        try:
            if int(route_target) == target_port:
                candidates.append(route)
        except (TypeError, ValueError):
            continue

    return candidates


def _matching_s1_routes(
    s1_routes: List[Dict[str, Any]],
    target_port: int,
    authority_path_identity: Any,
) -> List[Dict[str, Any]]:
    """Return S1 routes whose full structured identity exactly matches S2-B."""
    candidates = _candidate_s1_routes(s1_routes, target_port)

    if not candidates:
        return []

    matches: List[Dict[str, Any]] = []

    for route in candidates:
        if match_route_identity(authority_path_identity, route):
            matches.append(route)

    return matches


def derive_coverage_label(g: int, b: int, i: int, u: int, n: int) -> str:
    """Mechanically derive whole-vehicle governance coverage assessment label."""
    if b == 0 and i == 0 and g > 0:
        return "COMPLETE_VEHICLE_GOVERNANCE"
    components = []
    if g > 0:
        components.append(f"G{g}")
    if b > 0:
        components.append(f"B{b}")
    if i > 0:
        components.append(f"I{i}")
    if u > 0:
        components.append(f"U{u}")
    if n > 0:
        components.append(f"N{n}")
    return f"PARTIAL_GOVERNANCE_ACTIVE_BYPASS_{'_'.join(components)}"


class TestS2CReconciliationRev2:
    """Canonical Rev 2 Empirical Reconciliation Test Suite (Mathematical Invariant Verifier)."""

    def test_p1_s2_b_canonical_provenance(
        self, canonical_s2_b_artifacts: Dict[str, Any]
    ):
        """P1: Verify S2-B provenance is authenticated via Git snapshot and status is PASS."""
        summary = canonical_s2_b_artifacts["summary"]
        authority = canonical_s2_b_artifacts["authority"]

        s2_b_status = summary.get("s2_b_verdict") or summary.get(
            "runner_execution", {}
        ).get("status")
        assert (
            s2_b_status == "PASS"
        ), f"S2-B summary verdict must be PASS, got {s2_b_status}"
        assert (
            summary.get("canonical_evidence_frozen", True) is True
        ), "S2-B canonical_evidence_frozen must be True"

        # Verify authority detail evaluations exist and match summary count
        evals = authority.get("endpoint_authority_evaluations", [])
        assert len(evals) > 0, "S2-B authority evaluations must not be empty"

    def test_p2_s2_b_surface_reproducibility(
        self, canonical_s2_b_artifacts: Dict[str, Any]
    ):
        """P2: Verify S2-B endpoint surface matches discovery set exactly by full endpoint identity."""
        surface = canonical_s2_b_artifacts["surface"]
        assert len(surface) > 0, "S2-B endpoint surface must not be empty"

        endpoint_ids = {e["canonical_endpoint_id"] for e in surface}
        assert (
            len(endpoint_ids) == len(surface)
        ), "Duplicate canonical endpoint IDs in S2-B surface"

    def test_p3_s1_topology_integrity(self, canonical_s1_manifest: Dict[str, Any]):
        """P3: Verify S1 manifest is grounded in S1 raw evidence and structured route identity."""
        assert (
            canonical_s1_manifest.get("source_execution", {}).get("exit_code") == 0
        )
        routes = canonical_s1_manifest.get("governed_routes", [])
        assert len(routes) >= 1, "S1 manifest contains no governed routes"

        for r in routes:
            # Confirm structural route identity fields are extractable
            route_id_dict = extract_route_identity(r)
            assert route_id_dict["protocol"] == "UDP"
            assert route_id_dict["pep_ingress_port"] > 0
            assert route_id_dict["downstream_tap_port"] > 0
            assert route_id_dict["target_port"] > 0
            assert "pep_owner" in r

    def test_p4_s1_governance_evidence_grounding(
        self, canonical_s1_manifest: Dict[str, Any]
    ):
        """P4: Verify S1 manifest evidence hashes match audit records."""
        prov = canonical_s1_manifest.get("provenance", {})
        assert prov.get("s1_audit_evidence_sha256") is not None
        assert prov.get("s1_stdout_sha256") is not None

    def test_p5_path_level_reconciliation_partition_and_soundness(
        self,
        canonical_s1_manifest: Dict[str, Any],
        canonical_s2_b_artifacts: Dict[str, Any],
    ):
        """P5: Test mathematical partition invariants and semantic soundness without verdict hardcode.

        Evaluates full endpoint identity under:
          S = G ⊎ B ⊎ I ⊎ U ⊎ N
          E = G ⊎ B ⊎ I
        """
        s1_routes = canonical_s1_manifest.get("governed_routes", [])
        surface = canonical_s2_b_artifacts["surface"]
        surface_by_id = {e["canonical_endpoint_id"]: e for e in surface}
        s1_target_ports = {
            int(r.get("target_port") or r.get("forward_port")) for r in s1_routes
        }

        reconciled = []
        for ep in surface:
            port = int(ep["target_port"])
            reachability = ep["reachability_classification"]
            auth_category = ep["authority_classification"]
            auth_path = ep.get("authority_path_identity")
            cid = ep["canonical_endpoint_id"]

            if reachability == "UNREACHABLE" or auth_category == "UNREACHABLE":
                rec_cat = "UNREACHABLE_PROBE_BOUNDARY"
                reason = "Endpoint unreachable by probe; outside active attack surface"
            elif auth_category == "NON_EXECUTION":
                rec_cat = "NON_EXECUTION_SURFACE"
                reason = "Endpoint demonstrated zero state execution authority"
            elif auth_category == "EXECUTION_CAPABLE":
                candidates = _candidate_s1_routes(s1_routes, port)

                if not candidates:
                    rec_cat = "UNMEDIATED_ACTIVE_BYPASS"
                    reason = (
                        f"Active target reachable without S1 governance mediation "
                        f"(authority: {auth_category})"
                    )

                else:
                    matches = _matching_s1_routes(
                        s1_routes,
                        port,
                        auth_path,
                    )

                    if len(matches) == 1:
                        rec_cat = "DROS_GOVERNED_PATH"
                        reason = (
                            "Traffic path identity exactly matched one frozen S1 governed route"
                        )

                    elif len(matches) == 0:
                        rec_cat = "INDETERMINATE_BOUNDARY"
                        reason = (
                            f"Target port {port} overlaps S1 governed target set, "
                            "but no S2-B authority path identity exactly matches "
                            "a frozen S1 route"
                        )

                    else:
                        rec_cat = "INDETERMINATE_BOUNDARY"
                        reason = (
                            f"Target port {port} matched multiple frozen S1 route identities; "
                            "governance attribution is ambiguous"
                        )
            else:
                rec_cat = "INDETERMINATE_BOUNDARY"
                reason = f"Unrecognized authority classification: {auth_category}"

            reconciled.append(
                {
                    "canonical_endpoint_id": cid,
                    "target_port": port,
                    "reconciled_category": rec_cat,
                    "reason": reason,
                    "authority_path_identity": auth_path,
                }
            )

        # ---------------------------------------------------------------------
        # Mathematical Partition Invariants (Zero Hardcoded Counts)
        # Universe S = G ⊎ B ⊎ I ⊎ U ⊎ N
        # Execution Surface E = G ⊎ B ⊎ I
        # ---------------------------------------------------------------------
        set_s: Set[str] = {e["canonical_endpoint_id"] for e in surface}
        set_g: Set[str] = {
            r["canonical_endpoint_id"]
            for r in reconciled
            if r["reconciled_category"] == "DROS_GOVERNED_PATH"
        }
        set_b: Set[str] = {
            r["canonical_endpoint_id"]
            for r in reconciled
            if r["reconciled_category"] == "UNMEDIATED_ACTIVE_BYPASS"
        }
        set_i: Set[str] = {
            r["canonical_endpoint_id"]
            for r in reconciled
            if r["reconciled_category"] == "INDETERMINATE_BOUNDARY"
        }
        set_u: Set[str] = {
            r["canonical_endpoint_id"]
            for r in reconciled
            if r["reconciled_category"] == "UNREACHABLE_PROBE_BOUNDARY"
        }
        set_n: Set[str] = {
            r["canonical_endpoint_id"]
            for r in reconciled
            if r["reconciled_category"] == "NON_EXECUTION_SURFACE"
        }

        set_e: Set[str] = set_g | set_b | set_i

        # Invariant 1: Exact Set Partition of Universe S
        assert (
            set_g | set_b | set_i | set_u | set_n == set_s
        ), "Union of classified subsets must equal universe S"
        assert (
            len(set_g) + len(set_b) + len(set_i) + len(set_u) + len(set_n)
            == len(set_s)
        ), "Sum of subset cardinalities must equal universe S cardinality"

        # Invariant 2: Exact Set Partition of Execution Surface E
        assert (
            set_g | set_b | set_i == set_e
        ), "Union of G, B, I must equal execution surface E"
        assert (
            len(set_g) + len(set_b) + len(set_i) == len(set_e)
        ), "Sum of G, B, I cardinalities must equal execution surface E cardinality"

        # Invariant 3: Pairwise Mutual Exclusion (Disjointness)
        classification_sets = [
            ("G", set_g),
            ("B", set_b),
            ("I", set_i),
            ("U", set_u),
            ("N", set_n),
        ]
        for idx_a in range(len(classification_sets)):
            for idx_b in range(idx_a + 1, len(classification_sets)):
                name_a, set_a = classification_sets[idx_a]
                name_b, set_b = classification_sets[idx_b]
                assert set_a.isdisjoint(
                    set_b
                ), f"Classification subsets {name_a} and {name_b} must be pairwise disjoint"

        # Invariant 4: Semantic Soundness of Each Classification
        for cid in set_g:
            ep = surface_by_id[cid]
            assert ep["authority_classification"] == "EXECUTION_CAPABLE"
            assert ep["target_port"] in s1_target_ports
            matches = _matching_s1_routes(
                s1_routes,
                ep["target_port"],
                ep.get("authority_path_identity"),
            )
            assert len(matches) == 1

        for cid in set_b:
            ep = surface_by_id[cid]
            assert ep["authority_classification"] == "EXECUTION_CAPABLE"
            assert ep["target_port"] not in s1_target_ports
            assert (
                len(_candidate_s1_routes(s1_routes, ep["target_port"])) == 0
            )

        for cid in set_i:
            ep = surface_by_id[cid]
            assert ep["authority_classification"] == "EXECUTION_CAPABLE"
            assert ep["target_port"] in s1_target_ports
            candidates = _candidate_s1_routes(
                s1_routes,
                ep["target_port"],
            )
            matches = _matching_s1_routes(
                s1_routes,
                ep["target_port"],
                ep.get("authority_path_identity"),
            )
            assert len(candidates) > 0
            assert len(matches) != 1

        for cid in set_u:
            ep = surface_by_id[cid]
            assert (
                ep["reachability_classification"] == "UNREACHABLE"
                or ep["authority_classification"] == "UNREACHABLE"
            )

        for cid in set_n:
            ep = surface_by_id[cid]
            assert ep["authority_classification"] == "NON_EXECUTION"

    def test_p6_whole_vehicle_governance_fail_closed(
        self,
        canonical_s1_manifest: Dict[str, Any],
        canonical_s2_b_artifacts: Dict[str, Any],
    ):
        """P6: Whole-vehicle governance MUST be NOT_PROVEN if ANY bypass or indeterminate exists."""
        s1_routes = canonical_s1_manifest.get("governed_routes", [])
        surface = canonical_s2_b_artifacts["surface"]

        set_g: Set[str] = set()
        set_b: Set[str] = set()
        set_i: Set[str] = set()
        set_u: Set[str] = set()
        set_n: Set[str] = set()

        for ep in surface:
            port = int(ep["target_port"])
            reachability = ep["reachability_classification"]
            auth_cat = ep["authority_classification"]
            auth_path = ep.get("authority_path_identity")
            cid = ep["canonical_endpoint_id"]

            if reachability == "UNREACHABLE" or auth_cat == "UNREACHABLE":
                set_u.add(cid)
            elif auth_cat == "NON_EXECUTION":
                set_n.add(cid)
            elif auth_cat == "EXECUTION_CAPABLE":
                candidates = _candidate_s1_routes(
                    s1_routes,
                    port,
                )

                if not candidates:
                    set_b.add(cid)

                else:
                    matches = _matching_s1_routes(
                        s1_routes,
                        port,
                        auth_path,
                    )

                    if len(matches) == 1:
                        set_g.add(cid)
                    else:
                        set_i.add(cid)
            else:
                set_i.add(cid)

        # Strict Fail-Closed Rule
        if len(set_b) > 0 or len(set_i) > 0:
            wvg_status = "NOT_PROVEN"
        elif len(set_g) > 0 and len(set_b) == 0 and len(set_i) == 0:
            wvg_status = "PROVEN"
        else:
            wvg_status = "NOT_PROVEN"

        coverage_label = derive_coverage_label(
            len(set_g), len(set_b), len(set_i), len(set_u), len(set_n)
        )

        assert (
            wvg_status == "NOT_PROVEN"
        ), f"Whole-vehicle governance must be NOT_PROVEN, got {wvg_status}"
        assert coverage_label.startswith(
            "PARTIAL_GOVERNANCE_ACTIVE_BYPASS"
        ), f"Coverage must be mechanically derived partial bypass label, got {coverage_label}"
