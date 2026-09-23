"""Verify the first C1 pipeline: RECEIVED -> DISPATCHED -> RESULT."""

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

from benchmark.android_ingress import verify_pipeline_records
from vep.android_baseline import AndroidBaselineController


def build_requests() -> list[dict[str, object]]:
    return [
        {
            "request_id": f"ANDROID-C1-{index:06d}",
            "principal": "concurrency-agent",
            "action": "READ_CONTACTS",
            "capability": "CAP_CAMERA",
            "policy_version": "android-baseline-policy-v1",
            "revocation_epoch": 0,
            "arguments_hash": "sha256:android-c1-args",
        }
        for index in (11, 12)
    ]


def records(raw: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


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

    ingress_raw = controller.collect_app_records("ingress_records.jsonl")
    dispatched_raw = controller.collect_app_records("dispatch_records.jsonl")
    result_raw = controller.collect_app_records("result_records.jsonl")
    request_ids = [str(request["request_id"]) for request in requests]
    accounting = verify_pipeline_records(
        request_ids,
        records(ingress_raw),
        records(dispatched_raw),
        records(result_raw),
    )
    result_values = records(result_raw)
    result_invariant = all(
        result.get("decision") == "DENY"
        and result.get("execution_started") is False
        and result.get("execution_completed") is False
        and result.get("execution_effect") == "NONE"
        for result in result_values
    )
    (artifact_dir / "submitted.json").write_text(json.dumps(submissions, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "ingress_records.jsonl").write_text(ingress_raw, encoding="utf-8")
    (artifact_dir / "dispatch_records.jsonl").write_text(dispatched_raw, encoding="utf-8")
    (artifact_dir / "result_records.jsonl").write_text(result_raw, encoding="utf-8")
    adb_version = subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True)
    (artifact_dir / "adb_version.txt").write_text(adb_version.stdout, encoding="utf-8")
    summary = {
        "run_id": "ANDROID-C1",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
        "concurrency": 2,
        "submitted_request_ids": request_ids,
        "accounting": accounting,
        "result_invariant": result_invariant,
        "measurement_scope": "app-side ingress/dispatch/result accounting only; no latency, throughput, CPU, memory, or energy claim",
    }
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if accounting["complete"] and result_invariant else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb-path", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--package-name", default="io.dros.tmc.baseline")
    parser.add_argument("--activity-name", default="io.dros.tmc.baseline.MainActivity")
    parser.add_argument("--artifact-dir", required=True)
    raise SystemExit(run(parser.parse_args()))
