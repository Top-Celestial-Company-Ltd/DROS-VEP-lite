"""Run the Android native READ_CONTACTS permission baseline on a real AVD."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vep.android_permission_baseline import AndroidPermissionBaselineController


PERMISSION = "android.permission.READ_CONTACTS"
PACKAGE = "io.dros.tmc.permissionbaseline"


def adb(adb_path: str, device_id: str, *args: str) -> str:
    completed = subprocess.run(
        [adb_path, "-s", device_id, *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def run(args: argparse.Namespace) -> int:
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stale_effects = artifact_dir / "effects.jsonl"
    if stale_effects.exists():
        stale_effects.unlink()
    apk_hash = hashlib.sha256(Path(args.apk_path).read_bytes()).hexdigest()

    subprocess.run([args.adb_path, "-s", args.device_id, "install", "-r", args.apk_path], check=True)
    adb(args.adb_path, args.device_id, "shell", "pm", "clear", PACKAGE)
    adb(args.adb_path, args.device_id, "shell", "pm", "revoke", PACKAGE, PERMISSION)

    effect_marker = artifact_dir / "effects.jsonl"
    controller = AndroidPermissionBaselineController(
        adb_path=Path(args.adb_path),
        package_name=PACKAGE,
        activity_name=f"{PACKAGE}.MainActivity",
        device_id=args.device_id,
        effect_marker_path=effect_marker,
    )

    denied_request = {
        "request_id": "ANDROID-PERM-01-DENY-000001",
        "action": "READ_CONTACTS",
        "authority_state": "permission_revoked",
    }
    denied_result = controller.submit(denied_request)
    denied_effect = effect_marker.read_text(encoding="utf-8") if effect_marker.exists() else ""
    (artifact_dir / "deny_phase_effects.jsonl").write_text(denied_effect, encoding="utf-8")
    if effect_marker.exists():
        effect_marker.unlink()

    adb(args.adb_path, args.device_id, "shell", "pm", "clear", PACKAGE)
    adb(args.adb_path, args.device_id, "shell", "pm", "grant", PACKAGE, PERMISSION)

    allowed_request = {
        "request_id": "ANDROID-PERM-01-ALLOW-000001",
        "action": "READ_CONTACTS",
        "authority_state": "permission_granted",
    }
    allowed_result = controller.submit(allowed_request)
    allowed_effect = effect_marker.read_text(encoding="utf-8") if effect_marker.exists() else ""

    (artifact_dir / "requests.json").write_text(
        json.dumps({"deny": denied_request, "allow": allowed_request}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (artifact_dir / "results.json").write_text(
        json.dumps({"deny": denied_result, "allow": allowed_result}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (artifact_dir / "permission_state.txt").write_text(
        "deny_phase: revoked\nallow_phase: granted\n", encoding="utf-8"
    )
    (artifact_dir / "adb_version.txt").write_text(
        subprocess.run([args.adb_path, "version"], check=True, capture_output=True, text=True).stdout,
        encoding="utf-8",
    )
    (artifact_dir / "device_getprop.txt").write_text(
        adb(args.adb_path, args.device_id, "shell", "getprop"), encoding="utf-8"
    )

    checks = {
        "deny_decision": denied_result.get("decision") == "DENY",
        "deny_no_start": denied_result.get("execution_started") is False,
        "deny_no_complete": denied_result.get("execution_completed") is False,
        "deny_no_effect": denied_result.get("execution_effect") == "NONE" and denied_effect == "",
        "allow_decision": allowed_result.get("decision") == "ALLOW",
        "allow_started": allowed_result.get("execution_started") is True,
        "allow_completed": allowed_result.get("execution_completed") is True,
        "allow_effect": allowed_result.get("execution_effect") == "BOUNDED_PERMISSION_FIXTURE" and bool(allowed_effect.strip()),
    }
    summary = {
        "run_id": "ANDROID-PERM-01",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
        "apk_sha256": apk_hash,
        "authority": "Android native READ_CONTACTS permission manager",
        "checks": checks,
        "claim_ceiling": "Declared Pixel_7 Android 34 x86_64 app-runtime permission baseline only; not Android-wide or OS-wide security proof.",
    }
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (artifact_dir / "evidence_closure.json").write_text(
        json.dumps({"status": "VERIFIED" if all(checks.values()) else "FAILED", "run_id": "ANDROID-PERM-01", "checks": checks}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # Leave the device in the conservative revoked state after measurement.
    adb(args.adb_path, args.device_id, "shell", "pm", "revoke", PACKAGE, PERMISSION)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb-path", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--apk-path", required=True)
    parser.add_argument("--artifact-dir", required=True)
    raise SystemExit(run(parser.parse_args()))
