"""Run the single ANDROID-BASE-05 revocation path through a real AVD."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from vep.android_baseline import AndroidBaselineController


def build_revocation_request() -> dict[str, object]:
    return {
        "request_id": "ANDROID-BASE-05-000001",
        "principal": "revocable-agent",
        "action": "READ_CONTACTS",
        "capability": "CAP_CONTACTS",
        "policy_version": "android-baseline-policy-v1",
        "revocation_epoch": 0,
        "arguments_hash": "sha256:android-base-05-args",
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
    request = build_revocation_request()
    before = controller.submit(request)
    effect_count_before = len(effect_marker.read_text(encoding="utf-8").splitlines()) if effect_marker.exists() else 0
    revocation = controller.revoke(str(request["principal"]))
    after = controller.submit(request)
    effect_count_after = len(effect_marker.read_text(encoding="utf-8").splitlines()) if effect_marker.exists() else 0

    (artifact_dir / "request.json").write_text(json.dumps(request, indent=2, sort_keys=True), encoding="utf-8")
    (artifact_dir / "before_result.json").write_text(json.dumps(before, indent=2, sort_keys=True), encoding="utf-8")
    (artifact_dir / "revocation.json").write_text(json.dumps(revocation, indent=2, sort_keys=True), encoding="utf-8")
    (artifact_dir / "result.json").write_text(json.dumps(after, indent=2, sort_keys=True), encoding="utf-8")
    adb_version = subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True)
    (artifact_dir / "adb_version.txt").write_text(adb_version.stdout, encoding="utf-8")
    properties = subprocess.run([args.adb_path, "-s", args.device_id, "shell", "getprop"], check=True, capture_output=True, text=True)
    (artifact_dir / "device_getprop.txt").write_text(properties.stdout, encoding="utf-8")
    summary = {
        "run_id": "ANDROID-BASE-05",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
        "apk_sha256": hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest(),
        "before_result": before,
        "revocation": revocation,
        "result": after,
        "effect_count_before": effect_count_before,
        "effect_count_after": effect_count_after,
        "measurement_scope": "revocation and bounded fixture effect only; no performance or energy claim",
    }
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    if before.get("decision") != "ALLOW" or before.get("execution_effect") != "BOUNDED_FIXTURE":
        return 1
    if after.get("decision") != "DENY":
        return 1
    if after.get("execution_started") is not False or after.get("execution_completed") is not False:
        return 1
    if after.get("execution_effect") != "NONE":
        return 1
    if effect_count_after != effect_count_before:
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
