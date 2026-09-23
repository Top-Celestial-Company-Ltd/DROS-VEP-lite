"""Run the first small DENY concurrency baseline at C1/C2/C3."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(1, str(REPO_ROOT))

from benchmark.android_concurrency import dispatch_waves
from benchmark.analyze_tmc_android_base_06 import analyze_results
from vep.android_baseline import AndroidBaselineController


WARMUP_COUNT = 10
SAMPLE_COUNT = 100
CONCURRENCY_LEVELS = (2, 4, 8)


def build_request(index: int) -> dict[str, object]:
    return {
        "request_id": f"ANDROID-CONCURRENCY-{index:06d}",
        "principal": "concurrency-agent",
        "action": "READ_CONTACTS",
        "capability": "CAP_CAMERA",
        "policy_version": "android-baseline-policy-v1",
        "revocation_epoch": 0,
        "arguments_hash": "sha256:android-concurrency-args",
    }


def run_level(args: argparse.Namespace, level: int, root: Path) -> int:
    artifact_dir = root / f"c{level}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    controller = AndroidBaselineController(
        effect_marker_path=artifact_dir / "effects.jsonl",
        adb_path=Path(args.adb_path),
        package_name=args.package_name,
        activity_name=args.activity_name,
        device_id=args.device_id,
    )

    for index in range(1, WARMUP_COUNT + 1):
        result = controller.submit(build_request(index))
        if result.get("decision") != "DENY":
            return 1

    requests = [
        build_request(WARMUP_COUNT + sample_index)
        for sample_index in range(1, SAMPLE_COUNT + 1)
    ]
    started_ns = time.perf_counter_ns()
    results = dispatch_waves(controller.submit, requests, concurrency=level)
    elapsed_ns = time.perf_counter_ns() - started_ns

    raw_path = artifact_dir / "results.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw:
        for sample_index, (request_id, result) in enumerate(results, start=1):
            if (
                result.get("decision") != "DENY"
                or result.get("execution_started") is not False
                or result.get("execution_completed") is not False
                or result.get("execution_effect") != "NONE"
            ):
                return 1
            raw.write(
                json.dumps(
                    {
                        "sample_index": sample_index,
                        "request_id": request_id,
                        "principal": "concurrency-agent",
                        "action": "READ_CONTACTS",
                        "capability": "CAP_CAMERA",
                        "policy_version": "android-baseline-policy-v1",
                        "revocation_epoch": 0,
                        "arguments_hash": "sha256:android-concurrency-args",
                        "decision": result.get("decision"),
                        "execution_started": result.get("execution_started"),
                        "execution_completed": result.get("execution_completed"),
                        "execution_effect": result.get("execution_effect"),
                        "reason": result.get("reason"),
                        "decision_latency_ns": result.get("decision_latency_ns"),
                        "app_elapsed_ns": result.get("app_elapsed_ns"),
                    },
                    sort_keys=True,
                )
                + "\n"
            )

    summary = analyze_results(raw_path)
    summary.update(
        {
            "run_id": f"ANDROID-CONCURRENCY-C{level}",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
            "concurrency": level,
            "warmup_count": WARMUP_COUNT,
            "measured_sample_count": SAMPLE_COUNT,
            "dispatch_mode": "fixed-size waves",
            "host_elapsed_ns": elapsed_ns,
            "host_throughput_requests_per_second": SAMPLE_COUNT / (elapsed_ns / 1_000_000_000),
            "reset_procedure": "app package cleared once before this level's warm-up; no reset between measured waves",
            "apk_sha256": hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest(),
            "invariant_gate": "all completed requests DENY, not started, not completed, NONE effect",
        }
    )
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def run(args: argparse.Namespace) -> int:
    root = Path(args.artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    adb_version = subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True)
    properties = subprocess.run([args.adb_path, "-s", args.device_id, "shell", "getprop"], check=True, capture_output=True, text=True)
    for level in CONCURRENCY_LEVELS:
        if run_level(args, level, root) != 0:
            return 1
    (root / "adb_version.txt").write_text(adb_version.stdout, encoding="utf-8")
    (root / "device_getprop.txt").write_text(properties.stdout, encoding="utf-8")
    (root / "environment.json").write_text(
        json.dumps(
            {
                "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
                "concurrency_levels": list(CONCURRENCY_LEVELS),
                "warmup_count": WARMUP_COUNT,
                "sample_count_per_level": SAMPLE_COUNT,
                "dispatch_mode": "fixed-size waves",
                "measurement_boundary": "app-observed request-to-authorization-decision interval; host throughput reported separately",
                "background_and_animation_configuration": "not modified by benchmark",
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
    raise SystemExit(run(parser.parse_args()))
