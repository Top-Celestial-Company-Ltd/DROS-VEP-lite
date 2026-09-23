"""Run the single ANDROID-BASE-04 slice through a real ADB-connected app."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from vep.android_baseline import AndroidBaselineController


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
    request = {
        "request_id": "ANDROID-BASE-04-000001",
        "principal": "compromised-agent",
        "action": "READ_CONTACTS",
        "capability": "CAP_CAMERA",
        "policy_version": "android-baseline-policy-v1",
        "revocation_epoch": 0,
        "arguments_hash": "sha256:android-base-04-args",
    }
    result = controller.submit(request)
    (artifact_dir / "request.json").write_text(
        json.dumps(request, indent=2, sort_keys=True), encoding="utf-8"
    )
    (artifact_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    adb_version = subprocess.run(
        [args.adb_path, "version"], check=True, capture_output=True, text=True
    )
    (artifact_dir / "adb_version.txt").write_text(adb_version.stdout, encoding="utf-8")
    properties = subprocess.run(
        [args.adb_path, "-s", args.device_id, "shell", "getprop"],
        check=True,
        capture_output=True,
        text=True,
    )
    (artifact_dir / "device_getprop.txt").write_text(properties.stdout, encoding="utf-8")
    apk_hash = hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest()
    summary = {
        "run_id": "ANDROID-BASE-04",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {
            "avd": "Pixel_7",
            "android_api": 34,
            "abi": "x86_64",
            "device_id": args.device_id,
        },
        "apk_sha256": apk_hash,
        "result": result,
        "effect_marker_present": effect_marker.exists(),
        "measurement_scope": "security ordering only; no performance or energy claim",
    }
    (artifact_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    if result.get("decision") != "DENY":
        return 1
    if result.get("execution_started") is not False:
        return 1
    if result.get("execution_completed") is not False:
        return 1
    if result.get("execution_effect") != "NONE":
        return 1
    if effect_marker.exists() and effect_marker.read_text(encoding="utf-8") != "":
        return 1
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
