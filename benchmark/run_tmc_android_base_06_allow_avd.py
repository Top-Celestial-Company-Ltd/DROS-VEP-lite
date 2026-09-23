"""Collect BASE-06-ALLOW decision-latency samples on the same warm AVD."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(1, str(REPO_ROOT))

from benchmark.analyze_tmc_android_base_06 import analyze_results
from vep.android_baseline import AndroidBaselineController


WARMUP_COUNT = 10
SAMPLE_COUNT = 100


def build_request(index: int) -> dict[str, object]:
    return {
        "request_id": f"ANDROID-BASE-06-ALLOW-{index:06d}",
        "principal": "measurement-agent",
        "action": "READ_CONTACTS",
        "capability": "CAP_CONTACTS",
        "policy_version": "android-baseline-policy-v1",
        "revocation_epoch": 0,
        "arguments_hash": "sha256:android-base-06-allow-args",
    }


def run(args: argparse.Namespace) -> int:
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    effect_marker = artifact_dir / "effects.jsonl"
    controller = AndroidBaselineController(
        effect_marker_path=effect_marker,
        adb_path=Path(args.adb_path),
        package_name=args.package_name,
        activity_name=args.activity_name,
        device_id=args.device_id,
    )

    for index in range(1, WARMUP_COUNT + 1):
        result = controller.submit(build_request(index))
        if result.get("decision") != "ALLOW":
            return 1

    raw_path = artifact_dir / "results.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw:
        for sample_index in range(1, SAMPLE_COUNT + 1):
            request = build_request(WARMUP_COUNT + sample_index)
            result = controller.submit(request)
            if (
                result.get("decision") != "ALLOW"
                or result.get("execution_started") is not True
                or result.get("execution_completed") is not True
                or result.get("execution_effect") != "BOUNDED_FIXTURE"
            ):
                return 1
            raw.write(
                json.dumps(
                    {
                        "sample_index": sample_index,
                        "request_id": request["request_id"],
                        "principal": request["principal"],
                        "action": request["action"],
                        "capability": request["capability"],
                        "policy_version": request["policy_version"],
                        "revocation_epoch": request["revocation_epoch"],
                        "arguments_hash": request["arguments_hash"],
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
    effect_count = effect_marker.read_text(encoding="utf-8").count("\n")
    if effect_count != WARMUP_COUNT + SAMPLE_COUNT:
        return 1
    summary.update(
        {
            "run_id": "ANDROID-BASE-06-ALLOW",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
            "warmup_count": WARMUP_COUNT,
            "measured_sample_count": SAMPLE_COUNT,
            "mode": "serial",
            "avd_state": "warm; device must be boot-complete before invocation",
            "reset_procedure": "app package cleared once by first controller submission; no reset between measured samples",
            "apk_sha256": hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest(),
            "effect_marker_line_count": effect_count,
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
                "warmup_count": WARMUP_COUNT,
                "sample_count": SAMPLE_COUNT,
                "mode": "serial",
                "percentile_algorithm": "nearest-rank; rank=ceil(p*n), clamped to [1,n]",
                "background_and_animation_configuration": "not modified by benchmark",
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
    raise SystemExit(run(parser.parse_args()))
