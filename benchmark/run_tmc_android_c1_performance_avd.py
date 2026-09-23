"""Measure C1 pipeline throughput and dispatcher decision latency only."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(1, str(REPO_ROOT))

from benchmark.android_concurrency import dispatch_waves
from benchmark.android_ingress import verify_pipeline_records
from benchmark.analyze_tmc_android_base_06 import analyze_results
from vep.android_baseline import AndroidBaselineController


WARMUP_COUNT = 10
SAMPLE_COUNT = 100


def build_request(prefix: str, index: int) -> dict[str, object]:
    return {
        "request_id": f"{prefix}-{index:06d}",
        "principal": "c1-performance-agent",
        "action": "READ_CONTACTS",
        "capability": "CAP_CAMERA",
        "policy_version": "android-baseline-policy-v1",
        "revocation_epoch": 0,
        "arguments_hash": "sha256:android-c1-performance-args",
    }


def parse_records(raw: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def filter_records(records: list[dict[str, object]], request_ids: set[str]) -> list[dict[str, object]]:
    return [record for record in records if str(record.get("request_id", "")) in request_ids]


def run(args: argparse.Namespace) -> int:
    concurrency = args.concurrency
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    controller = AndroidBaselineController(
        effect_marker_path=artifact_dir / "unused-effects.jsonl",
        adb_path=Path(args.adb_path),
        package_name=args.package_name,
        activity_name=args.activity_name,
        device_id=args.device_id,
    )

    for index in range(1, WARMUP_COUNT + 1):
        submission = controller.submit_ingress(build_request(f"ANDROID-C{concurrency}-PERF-WARMUP", index))
        if submission.get("submitted") is not True:
            return 1

    requests = [build_request(f"ANDROID-C{concurrency}-PERF", index) for index in range(1, SAMPLE_COUNT + 1)]
    request_ids = {str(request["request_id"]) for request in requests}
    started_ns = time.perf_counter_ns()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(controller.submit_ingress, request) for request in requests]
        submissions = [future.result() for future in futures]
    elapsed_ns = time.perf_counter_ns() - started_ns
    if not all(submission.get("submitted") is True for submission in submissions):
        return 1

    ingress_all = parse_records(controller.collect_app_records("ingress_records.jsonl"))
    dispatched_all = parse_records(controller.collect_app_records("dispatch_records.jsonl"))
    result_all = parse_records(controller.collect_app_records("result_records.jsonl"))
    ingress = filter_records(ingress_all, request_ids)
    dispatched = filter_records(dispatched_all, request_ids)
    results = filter_records(result_all, request_ids)
    accounting = verify_pipeline_records(request_ids, ingress, dispatched, results)
    result_invariant = all(
        result.get("decision") == "DENY"
        and result.get("execution_started") is False
        and result.get("execution_completed") is False
        and result.get("execution_effect") == "NONE"
        for result in results
    )
    if not accounting["complete"] or not result_invariant:
        return 1

    raw_path = artifact_dir / "results.jsonl"
    raw_path.write_text("\n".join(json.dumps(result, sort_keys=True) for result in results) + "\n", encoding="utf-8")
    (artifact_dir / "ingress_records.jsonl").write_text("\n".join(json.dumps(record, sort_keys=True) for record in ingress) + "\n", encoding="utf-8")
    (artifact_dir / "dispatch_records.jsonl").write_text("\n".join(json.dumps(record, sort_keys=True) for record in dispatched) + "\n", encoding="utf-8")
    (artifact_dir / "submitted.json").write_text(json.dumps(submissions, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = analyze_results(raw_path)
    summary.update(
        {
            "run_id": args.run_id,
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
            "concurrency": concurrency,
            "warmup_count": WARMUP_COUNT,
            "measured_sample_count": SAMPLE_COUNT,
            "dispatch_mode": f"fixed-size waves of {concurrency}",
            "host_elapsed_ns": elapsed_ns,
            "host_throughput_requests_per_second": SAMPLE_COUNT / (elapsed_ns / 1_000_000_000),
            "pipeline_accounting": accounting,
            "result_invariant": result_invariant,
            "apk_sha256": hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest(),
            "measurement_boundary": "host throughput covers measured broadcast calls; decision latency is app-observed dispatcher interval; CPU, memory, and energy excluded",
        }
    )
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    adb_version = subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True)
    (artifact_dir / "adb_version.txt").write_text(adb_version.stdout, encoding="utf-8")
    properties = subprocess.run([args.adb_path, "-s", args.device_id, "shell", "getprop"], check=True, capture_output=True, text=True)
    (artifact_dir / "device_getprop.txt").write_text(properties.stdout, encoding="utf-8")
    (artifact_dir / "environment.json").write_text(
        json.dumps(
            {
                "target": summary["target"],
                "concurrency": concurrency,
                "warmup_count": WARMUP_COUNT,
                "sample_count": SAMPLE_COUNT,
                "dispatch_mode": f"fixed-size waves of {concurrency}",
                "percentile_algorithm": "nearest-rank; rank=ceil(p*n), clamped to [1,n]",
                "measurement_boundary": summary["measurement_boundary"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb-path", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--package-name", default="io.dros.tmc.baseline")
    parser.add_argument("--activity-name", default="io.dros.tmc.baseline.MainActivity")
    parser.add_argument("--apk-path", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--run-id", default="ANDROID-C1-PERFORMANCE")
    raise SystemExit(run(parser.parse_args()))
