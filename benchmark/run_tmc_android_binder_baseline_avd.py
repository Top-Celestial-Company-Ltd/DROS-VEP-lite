"""Run the protected Binder service baseline on the declared Pixel_7 AVD."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path


SERVICE_PACKAGE = "io.dros.tmc.binderfixture"
CLIENT_PACKAGE = "io.dros.tmc.binderclient"
PERMISSION = "io.dros.tmc.binderfixture.permission.EXECUTE_FIXTURE"
ACTIVITY = f"{CLIENT_PACKAGE}/.MainActivity"


def adb(adb_path: str, device_id: str, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        [adb_path, "-s", device_id, *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def read_run_as(adb_path: str, device_id: str, package: str, relative_path: str) -> str:
    return adb(
        adb_path,
        device_id,
        "shell",
        "run-as",
        package,
        "cat",
        relative_path,
        check=False,
    ).strip()


def launch_and_read(adb_path: str, device_id: str, request_id: str) -> tuple[dict, str]:
    adb(
        adb_path,
        device_id,
        "shell",
        "am",
        "start",
        "-W",
        "-n",
        ACTIVITY,
        "--es",
        "request_id",
        request_id,
    )
    deadline = time.monotonic() + 5.0
    result_text = ""
    while time.monotonic() < deadline:
        result_text = read_run_as(adb_path, device_id, CLIENT_PACKAGE, "files/result.json")
        if result_text:
            break
        time.sleep(0.1)
    if not result_text:
        raise RuntimeError(f"missing client result for {request_id}")
    return json.loads(result_text), read_run_as(
        adb_path, device_id, SERVICE_PACKAGE, "files/effects.jsonl"
    )


def run(args: argparse.Namespace) -> int:
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    service_apk_hash = hashlib.sha256(Path(args.service_apk_path).read_bytes()).hexdigest()
    client_apk_hash = hashlib.sha256(Path(args.client_apk_path).read_bytes()).hexdigest()

    adb(args.adb_path, args.device_id, "uninstall", SERVICE_PACKAGE, check=False)
    adb(args.adb_path, args.device_id, "uninstall", CLIENT_PACKAGE, check=False)
    adb(args.adb_path, args.device_id, "install", args.service_apk_path)
    adb(args.adb_path, args.device_id, "install", args.client_apk_path)
    adb(args.adb_path, args.device_id, "shell", "pm", "clear", SERVICE_PACKAGE)
    adb(args.adb_path, args.device_id, "shell", "pm", "clear", CLIENT_PACKAGE)
    adb(
        args.adb_path,
        args.device_id,
        "shell",
        "pm",
        "revoke",
        CLIENT_PACKAGE,
        PERMISSION,
        check=False,
    )

    deny_result, deny_effect = launch_and_read(
        args.adb_path, args.device_id, "ANDROID-BINDER-01-DENY-000001"
    )

    adb(args.adb_path, args.device_id, "shell", "pm", "clear", SERVICE_PACKAGE)
    adb(args.adb_path, args.device_id, "shell", "pm", "clear", CLIENT_PACKAGE)
    grant_output = adb(
        args.adb_path,
        args.device_id,
        "shell",
        "pm",
        "grant",
        CLIENT_PACKAGE,
        PERMISSION,
        check=False,
    )
    allow_result, allow_effect = launch_and_read(
        args.adb_path, args.device_id, "ANDROID-BINDER-01-ALLOW-000001"
    )

    checks = {
        "deny_decision": deny_result.get("decision") == "DENY",
        "deny_permission_reason": deny_result.get("reason") == "BINDER_SERVICE_PERMISSION_DENIED",
        "deny_no_execution": (
            deny_result.get("execution_started") is False
            and deny_result.get("execution_completed") is False
        ),
        "deny_no_effect": deny_result.get("execution_effect") == "NONE" and deny_effect == "",
        "allow_decision": allow_result.get("decision") == "ALLOW",
        "allow_execution": (
            allow_result.get("execution_started") is True
            and allow_result.get("execution_completed") is True
        ),
        "allow_effect": (
            allow_result.get("execution_effect") == "BOUNDED_BINDER_FIXTURE"
            and '"effect":"BOUNDED_BINDER_FIXTURE"' in allow_effect
        ),
    }
    results = {
        "deny": {"result": deny_result, "service_effects": deny_effect},
        "allow": {"result": allow_result, "service_effects": allow_effect},
    }
    (artifact_dir / "results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    (artifact_dir / "binder_permission_state.txt").write_text(
        "deny phase: client permission revoked\n"
        f"grant command output: {grant_output}\n"
        "allow phase: client permission granted\n",
        encoding="utf-8",
    )
    (artifact_dir / "adb_version.txt").write_text(
        subprocess.run(
            [args.adb_path, "version"], check=True, capture_output=True, text=True, encoding="utf-8"
        ).stdout,
        encoding="utf-8",
    )
    (artifact_dir / "device_getprop.txt").write_text(
        adb(args.adb_path, args.device_id, "shell", "getprop"), encoding="utf-8"
    )
    summary = {
        "run_id": "ANDROID-BINDER-01",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "target": {"avd": "Pixel_7", "android_api": 34, "abi": "x86_64", "device_id": args.device_id},
        "authority": "Android protected Binder service with a declared runtime permission",
        "service_apk_sha256": service_apk_hash,
        "client_apk_sha256": client_apk_hash,
        "checks": checks,
        "claim_ceiling": "Declared Pixel_7 Android 34 x86_64 protected Binder service path only; not Binder framework-wide or Android-wide security proof.",
    }
    (artifact_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    closure = {
        "status": "VERIFIED" if all(checks.values()) else "FAILED",
        "run_id": "ANDROID-BINDER-01",
        "checks": checks,
        "canonical": all(checks.values()),
    }
    (artifact_dir / "evidence_closure.json").write_text(
        json.dumps(closure, indent=2, sort_keys=True), encoding="utf-8"
    )
    adb(args.adb_path, args.device_id, "shell", "pm", "revoke", CLIENT_PACKAGE, PERMISSION, check=False)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb-path", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--service-apk-path", required=True)
    parser.add_argument("--client-apk-path", required=True)
    parser.add_argument("--artifact-dir", required=True)
    raise SystemExit(run(parser.parse_args()))
