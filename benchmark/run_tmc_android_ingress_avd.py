"""Verify deterministic app-side ingress accounting for two concurrent requests."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(1, str(REPO_ROOT))

from benchmark.android_ingress import verify_ingress_records
from vep.android_baseline import AndroidBaselineController


def build_requests() -> list[dict[str, object]]:
    return [
        {
            "request_id": f"ANDROID-INGRESS-{index:06d}",
            "principal": "concurrency-agent",
            "action": "READ_CONTACTS",
            "capability": "CAP_CAMERA",
            "policy_version": "android-baseline-policy-v1",
            "revocation_epoch": 0,
            "arguments_hash": "sha256:android-ingress-args",
        }
        for index in (11, 12)
    ]


def run(args: argparse.Namespace) -> int:
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    controller = AndroidBaselineController(
        effect_marker_path=artifact_dir / "unused-effects.jsonl",
        adb_path=Path(args.adb_path),
        package_name=args.package_name,
        activity_name=args.activity_name,
        device_id=args.device_id,
    )
    requests = build_requests()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(controller.submit_ingress, request) for request in requests]
        submissions = [future.result() for future in futures]

    raw_records = controller.collect_ingress_records()
    records = [json.loads(line) for line in raw_records.splitlines() if line.strip()]
    accounting = verify_ingress_records(
        [str(request["request_id"]) for request in requests], records
    )
    (artifact_dir / "submitted.json").write_text(json.dumps(submissions, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "ingress_records.jsonl").write_text(raw_records, encoding="utf-8")
    adb_version = subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True)
    (artifact_dir / "adb_version.txt").write_text(adb_version.stdout, encoding="utf-8")
    summary = {
        "run_id": "ANDROID-INGRESS-C1",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
        "submitted_request_ids": [request["request_id"] for request in requests],
        "accounting": accounting,
        "measurement_scope": "app-side ingress accounting only; no authorization, execution, latency, throughput, or energy claim",
    }
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if accounting["complete"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb-path", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--package-name", default="io.dros.tmc.baseline")
    parser.add_argument("--activity-name", default="io.dros.tmc.baseline.MainActivity")
    parser.add_argument("--artifact-dir", required=True)
    raise SystemExit(run(parser.parse_args()))
