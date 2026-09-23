"""Run the Android AppOps READ_CONTACTS baseline on a real AVD."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vep.android_baseline import AndroidBaselineController


PACKAGE = "io.dros.tmc.appopsbaseline"
PERMISSION = "android.permission.READ_CONTACTS"
APPOP = "READ_CONTACTS"


def adb(adb_path: str, device_id: str, *args: str) -> str:
    completed = subprocess.run([adb_path, "-s", device_id, *args], check=True, capture_output=True, text=True, encoding="utf-8")
    return completed.stdout


def run(args: argparse.Namespace) -> int:
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    effect_marker = artifact_dir / "effects.jsonl"
    effect_marker.unlink(missing_ok=True)
    apk_hash = hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest()

    subprocess.run([args.adb_path, "-s", args.device_id, "install", "-r", args.apk_path], check=True)
    adb(args.adb_path, args.device_id, "shell", "pm", "clear", PACKAGE)
    adb(args.adb_path, args.device_id, "shell", "pm", "grant", PACKAGE, PERMISSION)
    adb(args.adb_path, args.device_id, "shell", "appops", "set", PACKAGE, APPOP, "deny")

    controller = AndroidBaselineController(
        effect_marker_path=effect_marker,
        adb_path=Path(args.adb_path),
        package_name=PACKAGE,
        activity_name=f"{PACKAGE}.MainActivity",
        device_id=args.device_id,
    )
    deny_request = {"request_id": "ANDROID-APPOPS-01-DENY-000001", "action": "READ_CONTACTS"}
    deny_result = controller.submit(deny_request)
    deny_effect = effect_marker.read_text(encoding="utf-8") if effect_marker.exists() else ""

    adb(args.adb_path, args.device_id, "shell", "pm", "clear", PACKAGE)
    adb(args.adb_path, args.device_id, "shell", "pm", "grant", PACKAGE, PERMISSION)
    adb(args.adb_path, args.device_id, "shell", "appops", "set", PACKAGE, APPOP, "allow")
    effect_marker.unlink(missing_ok=True)
    allow_request = {"request_id": "ANDROID-APPOPS-01-ALLOW-000001", "action": "READ_CONTACTS"}
    allow_result = controller.submit(allow_request)
    allow_effect = effect_marker.read_text(encoding="utf-8") if effect_marker.exists() else ""

    checks = {
        "deny_decision": deny_result.get("decision") == "DENY",
        "deny_reason": deny_result.get("reason") == "ANDROID_APPOPS_DENIED",
        "deny_no_execution": deny_result.get("execution_started") is False and deny_result.get("execution_completed") is False,
        "deny_no_effect": deny_result.get("execution_effect") == "NONE" and deny_effect == "",
        "allow_decision": allow_result.get("decision") == "ALLOW",
        "allow_execution": allow_result.get("execution_started") is True and allow_result.get("execution_completed") is True,
        "allow_effect": allow_result.get("execution_effect") == "BOUNDED_APPOPS_FIXTURE" and bool(allow_effect.strip()),
    }
    (artifact_dir / "results.json").write_text(json.dumps({"deny": deny_result, "allow": allow_result}, indent=2, sort_keys=True), encoding="utf-8")
    (artifact_dir / "appops_state.txt").write_text("permission: READ_CONTACTS granted\ndeny phase: appops deny\nallow phase: appops allow\n", encoding="utf-8")
    (artifact_dir / "adb_version.txt").write_text(subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True).stdout, encoding="utf-8")
    (artifact_dir / "device_getprop.txt").write_text(adb(args.adb_path, args.device_id, "shell", "getprop"), encoding="utf-8")
    summary = {
        "run_id": "ANDROID-APPOPS-01",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
        "apk_sha256": apk_hash,
        "authority": "Android native AppOps READ_CONTACTS",
        "checks": checks,
        "claim_ceiling": "Declared Pixel_7 Android 34 x86_64 AppOps application-runtime path only; not Android-wide or OS-wide security proof.",
    }
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (artifact_dir / "evidence_closure.json").write_text(json.dumps({"status": "VERIFIED" if all(checks.values()) else "FAILED", "run_id": "ANDROID-APPOPS-01", "checks": checks}, indent=2, sort_keys=True), encoding="utf-8")
    adb(args.adb_path, args.device_id, "shell", "appops", "set", PACKAGE, APPOP, "deny")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb-path", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--apk-path", required=True)
    parser.add_argument("--artifact-dir", required=True)
    raise SystemExit(run(parser.parse_args()))
