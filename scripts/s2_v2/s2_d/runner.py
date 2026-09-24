#!/usr/bin/env python3
"""Main runner CLI for Milestone M1.1-S2-D.

Supports Gate 1 Non-Invasive Verification and future live execution.
DEFAULT EXECUTION MODE IS STRICTLY DRY_RUN / NON-INVASIVE.
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path

from .models import Gate1Result, SnapshotPhase, Verdict
from .preflight import PreflightChecker
from .report_generator import emit_gate1_artifacts
from .snapshot import create_system_snapshot, verify_snapshot_invariants

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("s2_d.runner")


def run_gate1(repo_root: Path, output_dir: Path, pid: Any = None) -> int:
    """Execute Gate 1 Non-Invasiveness Checklist and emit artifacts."""
    logger.info("=================================================================")
    logger.info("Milestone M1.1-S2-D Gate 1: Runner Non-Invasiveness Verification")
    logger.info("=================================================================")

    # 1. Pre-test Snapshot
    logger.info("[1/4] Capturing pre-test system snapshot (Dry-run mode)...")
    snap_pre = create_system_snapshot(repo_root, SnapshotPhase.PRE_TEST, pid=pid, mode="DRY_RUN")
    pre_snap_path = output_dir / "pre_test_snapshot.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    pre_snap_path.write_bytes(json.dumps(snap_pre.to_dict(), indent=2).encode("utf-8") + b"\n")

    # 2. Execute Preflight Checklist
    logger.info("[2/4] Executing 12-point Gate 1 non-invasiveness checklist...")
    checker = PreflightChecker(repo_root)
    result = checker.run_gate1_checklist(pid=pid)
    result.timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result.runner_commit = snap_pre.git_state.get("head_commit", "UNKNOWN")

    # 3. Post-test Snapshot & Invariant Check
    logger.info("[3/4] Capturing post-test system snapshot and verifying invariants...")
    snap_post = create_system_snapshot(repo_root, SnapshotPhase.POST_TEST, pid=pid, mode="DRY_RUN")
    post_snap_path = output_dir / "post_test_snapshot.json"
    post_snap_path.write_bytes(json.dumps(snap_post.to_dict(), indent=2).encode("utf-8") + b"\n")

    invariants_ok, failures = verify_snapshot_invariants(snap_pre, snap_post)
    if not invariants_ok:
        logger.error(f"Snapshot invariants failed: {failures}")
        result.verdict = Verdict.FAIL
        result.checklist["snapshot_continuity_invariants"] = f"FAIL: {failures}"
    else:
        result.checklist["snapshot_continuity_invariants"] = "PASS"

    # 4. Emit Gate 1 Results
    logger.info("[4/4] Emitting GATE1_RESULT.json and audit report...")
    json_path = emit_gate1_artifacts(result, output_dir)
    logger.info(f"Gate 1 artifacts emitted to {output_dir}")

    for k, v in result.checklist.items():
        logger.info(f"  {k}: {v}")

    logger.info("=================================================================")
    logger.info(f"Gate 1 Final Verdict: {result.verdict.value} (Claim Status: {result.claim_status})")
    logger.info("=================================================================")

    return 0 if result.verdict == Verdict.PASS else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="DROS Drone Milestone M1.1-S2-D Runner")
    parser.add_argument(
        "--gate1",
        action="store_true",
        default=True,
        help="Execute Gate 1 non-invasiveness verification (DEFAULT)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=False,
        help="Opt-in to live firewall containment execution (BLOCKED IN GATE 1)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Custom output directory for artifacts",
    )
    parser.add_argument(
        "--pid",
        type=int,
        default=None,
        help="Optional PX4 process PID to inspect",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = repo_root / "reports" / "evidence" / "drone" / "m1_1" / "s2_v2" / "s2_d_gate1"

    if args.live:
        logger.error("Live execution requested, but Gate 1 requires strict non-invasiveness. Aborting live execution.")
        sys.exit(2)

    exit_code = run_gate1(repo_root, output_dir, pid=args.pid)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
