#!/usr/bin/env python3
"""DROS Drone M1.1-S2-C Canonical v2.1 Rev 2 Runner - Reconciliation Artifact Generator

Consumes canonical Git snapshots of S1 topology and S2-B authority evidence.
Ingests BOTH s2_v2_b_authority_summary.json and s2_v2_b_authority.json.
Produces:
  1. s2_v2_c_reconciliation.json
  2. s2_v2_c_reconciliation_summary.json
  3. s2_v2_c_reconciliation.exit_code
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Ensure scripts directory is importable
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from canonical_git_snapshot import (
    _resolve_repo_path,
    build_authority_index,
    canonical_endpoint_key,
    endpoint_surface_digest,
    extract_normalized_endpoint_surface,
    extract_route_identity,
    match_route_identity,
    verify_canonical_git_snapshot,
)


def _candidate_s1_routes(
    s1_routes: List[Dict[str, Any]],
    target_port: int,
) -> List[Dict[str, Any]]:
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
    candidates = _candidate_s1_routes(
        s1_routes,
        target_port,
    )

    return [
        route
        for route in candidates
        if match_route_identity(
            authority_path_identity,
            route,
        )
    ]


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


def run_reconciliation(
    s1_anchor_path: Path,
    s2_b_anchor_path: Path,
    output_dir: Path,
) -> int:
    """Execute S2-C reconciliation."""
    print("=" * 80)
    print("DROS DRONE M1.1-S2-C CANONICAL RECONCILIATION RUNNER (REV 2)")
    print("=" * 80)

    # 1. Verify S1 Git Snapshot
    print(f"[*] Verifying S1 Canonical Git Snapshot: {s1_anchor_path}")
    s1_ok, s1_reason, s1_audit = verify_canonical_git_snapshot(s1_anchor_path)
    if not s1_ok:
        print(f"[-] S1 Git Snapshot Verification FAILED: {s1_reason}")
        return 1
    print("    [+] S1 Git Snapshot Verified Identical to Commit")

    s1_anchor_data = json.loads(s1_anchor_path.read_text(encoding="utf-8"))
    s1_manifest_rel = [
        k for k in s1_anchor_data["tracked_artifacts"] if "manifest" in k
    ][0]
    s1_audit_rel = [
        k for k in s1_anchor_data["tracked_artifacts"] if "audit_evidence" in k
    ][0]

    git_root = s1_anchor_path.resolve()
    for parent in [git_root] + list(git_root.parents):
        if (parent / ".git").exists():
            git_root = parent
            break

    s1_manifest_path, _ = _resolve_repo_path(git_root, s1_manifest_rel)
    s1_audit_path, _ = _resolve_repo_path(git_root, s1_audit_rel)
    s1_manifest = json.loads(s1_manifest_path.read_text(encoding="utf-8"))
    s1_audit_data = json.loads(s1_audit_path.read_text(encoding="utf-8"))
    s1_routes = s1_manifest.get("governed_routes", [])

    # Anti-contamination: Cross-verify manifest against raw S1 machine observation
    s1_obs = s1_audit_data.get("instrumented_observation_point", {})
    raw_tap_port = s1_obs.get("port")
    raw_fwd_port = s1_obs.get("fwd_port")
    if raw_tap_port is None or raw_fwd_port is None:
        print("[-] Raw S1 audit evidence missing observation ports")
        return 1
    for r in s1_routes:
        if r.get("downstream_tap_port") != raw_tap_port or r.get("target_port") != raw_fwd_port:
            print(
                f"[-] Manifest route mismatch with raw S1 evidence: "
                f"tap={r.get('downstream_tap_port')} vs {raw_tap_port}, "
                f"tgt={r.get('target_port')} vs {raw_fwd_port}"
            )
            return 1

    # 2. Verify S2-B Git Snapshot
    print(f"[*] Verifying S2-B Canonical Git Snapshot: {s2_b_anchor_path}")
    s2_b_ok, s2_b_reason, s2_b_audit = verify_canonical_git_snapshot(s2_b_anchor_path)
    if not s2_b_ok:
        print(f"[-] S2-B Git Snapshot Verification FAILED: {s2_b_reason}")
        return 1
    print("    [+] S2-B Git Snapshot Verified Identical to Commit")

    s2_b_anchor_data = json.loads(s2_b_anchor_path.read_text(encoding="utf-8"))
    s2_b_summary_rel = [
        k for k in s2_b_anchor_data["tracked_artifacts"] if "summary" in k
    ][0]
    s2_b_authority_rel = [
        k
        for k in s2_b_anchor_data["tracked_artifacts"]
        if "authority.json" in k
    ][0]

    s2_b_summary_path, _ = _resolve_repo_path(git_root, s2_b_summary_rel)
    s2_b_authority_path, _ = _resolve_repo_path(git_root, s2_b_authority_rel)
    s2_b_summary = json.loads(s2_b_summary_path.read_text(encoding="utf-8"))
    s2_b_authority = json.loads(s2_b_authority_path.read_text(encoding="utf-8"))

    # 3. Assert S2-B Surface Invariance
    surface = extract_normalized_endpoint_surface(s2_b_summary, s2_b_authority)
    expected_surface_sha = s2_b_anchor_data.get("endpoint_surface_sha256")
    actual_surface_sha = endpoint_surface_digest(surface)
    if actual_surface_sha != expected_surface_sha:
        print(
            f"[-] S2-B Surface SHA mismatch: {actual_surface_sha} != {expected_surface_sha}"
        )
        return 1
    print("    [+] S2-B Endpoint Surface Digest Verified")

    # 4. Perform Path-Level Reconciliation with Full Endpoint Identity
    print("[*] Reconciling empirical endpoints against S1 governance topology...")
    reconciled_endpoints = []
    set_g: Set[str] = set()
    set_b: Set[str] = set()
    set_i: Set[str] = set()
    set_u: Set[str] = set()
    set_n: Set[str] = set()

    category_counts = {
        "DROS_GOVERNED_PATH": 0,
        "UNMEDIATED_ACTIVE_BYPASS": 0,
        "INDETERMINATE_BOUNDARY": 0,
        "UNREACHABLE_PROBE_BOUNDARY": 0,
        "NON_EXECUTION_SURFACE": 0,
    }

    for ep in surface:
        target_port = int(ep["target_port"])
        reachability = ep["reachability_classification"]
        authority_cat = ep["authority_classification"]
        auth_path = ep.get("authority_path_identity")
        cid = ep["canonical_endpoint_id"]

        matches: List[Dict[str, Any]] = []

        if reachability == "UNREACHABLE" or authority_cat == "UNREACHABLE":
            reconciled_cat = "UNREACHABLE_PROBE_BOUNDARY"
            reconciliation_reason = (
                "Endpoint probe failed; target is outside active attack surface"
            )
            set_u.add(cid)
        elif authority_cat == "NON_EXECUTION":
            reconciled_cat = "NON_EXECUTION_SURFACE"
            reconciliation_reason = (
                "Endpoint demonstrated zero state execution authority"
            )
            set_n.add(cid)
        elif authority_cat == "EXECUTION_CAPABLE":
            candidates = _candidate_s1_routes(
                s1_routes,
                target_port,
            )

            if not candidates:
                reconciled_cat = "UNMEDIATED_ACTIVE_BYPASS"
                reconciliation_reason = (
                    f"Active target reachable without DROS S1 proxy mediation "
                    f"(authority: {authority_cat})"
                )
                set_b.add(cid)

            else:
                matches = _matching_s1_routes(
                    s1_routes,
                    target_port,
                    auth_path,
                )

                if len(matches) == 1:
                    reconciled_cat = "DROS_GOVERNED_PATH"
                    reconciliation_reason = (
                        "Authority path identity exactly matched one frozen "
                        f"S1 governed route: {auth_path}"
                    )
                    set_g.add(cid)

                elif len(matches) == 0:
                    reconciled_cat = "INDETERMINATE_BOUNDARY"
                    reconciliation_reason = (
                        f"Target port {target_port} overlaps the frozen S1 target set, "
                        "but no exact S1 route identity matched the S2-B authority path"
                    )
                    set_i.add(cid)

                else:
                    reconciled_cat = "INDETERMINATE_BOUNDARY"
                    reconciliation_reason = (
                        f"Target port {target_port} matched multiple frozen S1 routes; "
                        "governance attribution is ambiguous"
                    )
                    set_i.add(cid)
        else:
            reconciled_cat = "INDETERMINATE_BOUNDARY"
            reconciliation_reason = f"Unrecognized authority classification: {authority_cat}"
            set_i.add(cid)

        category_counts[reconciled_cat] += 1
        rec_entry = {
            "canonical_endpoint_id": cid,
            "target_port": target_port,
            "target_ip": ep.get("target_ip", "127.0.0.1"),
            "original_reachability": reachability,
            "original_authority": authority_cat,
            "authority_path_identity": auth_path,
            "reconciled_category": reconciled_cat,
            "reconciliation_reason": reconciliation_reason,
            "matched_s1_routes": matches if authority_cat == "EXECUTION_CAPABLE" else [],
        }
        reconciled_endpoints.append(rec_entry)
        print(f"    - [{cid}] -> {reconciled_cat:28s} | {reconciliation_reason[:50]}...")

    # 5. Evaluate Whole-Vehicle Governance (Fail-Closed)
    if len(set_b) > 0 or len(set_i) > 0:
        wvg_status = "NOT_PROVEN"
    elif len(set_g) > 0 and len(set_b) == 0 and len(set_i) == 0:
        wvg_status = "PROVEN"
    else:
        wvg_status = "NOT_PROVEN"

    wvg_coverage = derive_coverage_label(
        len(set_g), len(set_b), len(set_i), len(set_u), len(set_n)
    )

    print(f"[*] Whole-Vehicle Governance Status: {wvg_status} ({wvg_coverage})")

    # 6. Build Artifacts with Precise Epistemic Wording
    now_iso = datetime.now(timezone.utc).isoformat()
    reconciliation_artifact = {
        "schema_version": "2.1",
        "timestamp_utc": now_iso,
        "reconciliation_computation_status": "COMPLETED",
        "canonical_snapshot_verified": s1_ok and s2_b_ok,
        "inputs": {
            "s1_frozen_commit": s1_anchor_data["frozen_commit"],
            "s1_manifest_rel": s1_manifest_rel,
            "s1_audit_rel": s1_audit_rel,
            "s2_b_frozen_commit": s2_b_anchor_data["frozen_commit"],
            "s2_b_summary_rel": s2_b_summary_rel,
            "s2_b_authority_rel": s2_b_authority_rel,
            "endpoint_surface_sha256": actual_surface_sha,
        },
        "reconciled_endpoints": reconciled_endpoints,
        "summary": {
            "total_endpoints": len(reconciled_endpoints),
            "partition_counts": {
                "S": len(reconciled_endpoints),
                "G_governed": len(set_g),
                "B_bypass": len(set_b),
                "I_indeterminate": len(set_i),
                "U_unreachable": len(set_u),
                "N_non_execution": len(set_n),
            },
            "whole_vehicle_governance": {
                "status": wvg_status,
                "coverage_assessment": wvg_coverage,
                "governed_ports_verified": len(set_g),
                "active_bypass_ports_detected": len(set_b),
                "indeterminate_boundary_ports": len(set_i),
                "unreachable_ports": len(set_u),
                "non_execution_ports": len(set_n),
            },
        },
    }

    reconciliation_summary_artifact = {
        "schema_version": "2.1",
        "timestamp_utc": now_iso,
        "reconciliation_computation_status": "COMPLETED",
        "canonical_snapshot_verified": s1_ok and s2_b_ok,
        "s2_b_frozen_commit": s2_b_anchor_data["frozen_commit"],
        "endpoint_surface_sha256": actual_surface_sha,
        "partition_counts": {
            "S": len(reconciled_endpoints),
            "G": len(set_g),
            "B": len(set_b),
            "I": len(set_i),
            "U": len(set_u),
            "N": len(set_n),
        },
        "whole_vehicle_governance": {
            "status": wvg_status,
            "coverage_assessment": wvg_coverage,
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    rec_json_path = output_dir / "s2_v2_c_reconciliation.json"
    rec_sum_path = output_dir / "s2_v2_c_reconciliation_summary.json"
    rec_exit_path = output_dir / "s2_v2_c_reconciliation.exit_code"

    rec_json_path.write_bytes(
        (json.dumps(reconciliation_artifact, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )
    rec_sum_path.write_bytes(
        (json.dumps(reconciliation_summary_artifact, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )
    rec_exit_path.write_bytes(b"0\n")

    print(f"[+] Written: {rec_json_path}")
    print(f"[+] Written: {rec_sum_path}")
    print(f"[+] Written: {rec_exit_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run S2-C reconciliation")
    s1_base = Path(__file__).resolve().parents[2] / "reports" / "evidence" / "drone" / "m1_1" / "s1"
    s1_default = (s1_base / "s1_freeze_anchor_v2.json") if (s1_base / "s1_freeze_anchor_v2.json").exists() else (s1_base / "s1_freeze_anchor.json")
    parser.add_argument(
        "--s1-anchor",
        type=Path,
        default=s1_default,
    )
    parser.add_argument(
        "--s2-b-anchor",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "reports"
        / "evidence"
        / "drone"
        / "m1_1"
        / "s2_v2"
        / "s2_b_freeze_anchor.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "reports"
        / "evidence"
        / "drone"
        / "m1_1"
        / "s2_v2",
    )
    args = parser.parse_args()
    return run_reconciliation(args.s1_anchor, args.s2_b_anchor, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
