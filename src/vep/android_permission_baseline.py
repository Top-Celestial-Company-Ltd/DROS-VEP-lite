"""Android native permission baseline seam.

The baseline models the authority decision as Android's declared
``READ_CONTACTS`` permission state.  It is deliberately separate from the
DROS action boundary so that comparative runs do not accidentally reuse the
system under evaluation.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class AndroidPermissionBaselineController:
    """Host-side controller for the Android native-permission baseline."""

    _ACTION_PERMISSION = {"READ_CONTACTS": "ANDROID_PERMISSION_READ_CONTACTS"}

    def __init__(
        self,
        *,
        permission_granted: bool | None = None,
        adb_path: Path | None = None,
        package_name: str = "io.dros.tmc.permissionbaseline",
        activity_name: str = "io.dros.tmc.permissionbaseline.MainActivity",
        device_id: str | None = None,
        timeout_seconds: float = 30.0,
        effect_marker_path: Path | None = None,
    ) -> None:
        self._permission_granted = permission_granted
        self._adb_path = adb_path
        self._package_name = package_name
        self._activity_name = activity_name
        self._device_id = device_id
        self._timeout_seconds = timeout_seconds
        self._effect_marker_path = effect_marker_path

    def evaluate(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Evaluate a request against an injected native permission state.

        This method exists for the contract test only.  A real AVD run uses
        :meth:`submit`, which obtains the decision from Android's permission
        manager inside the baseline APK.
        """

        request_id = str(request.get("request_id", ""))
        authority = self._ACTION_PERMISSION.get(str(request.get("action", "")))
        if authority is None or self._permission_granted is not True:
            return {
                "request_id": request_id,
                "authority": authority or "ANDROID_PERMISSION_UNKNOWN",
                "decision": "DENY",
                "execution_started": False,
                "execution_completed": False,
                "execution_effect": "NONE",
                "reason": "ANDROID_PERMISSION_DENIED",
            }
        return {
            "request_id": request_id,
            "authority": authority,
            "decision": "ALLOW",
            "execution_started": True,
            "execution_completed": True,
            "execution_effect": "BOUNDED_PERMISSION_FIXTURE",
            "reason": "ANDROID_PERMISSION_GRANTED",
        }

    def submit(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if self._adb_path is None:
            return self.evaluate(request)
        payload = json.dumps(dict(request), separators=(",", ":"))
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        self._run_adb("shell", "am", "start", "-W", "-n", f"{self._package_name}/{self._activity_name}", "--es", "request_b64", encoded)
        filename = self._result_filename(str(request.get("request_id", "")))
        for _ in range(120):
            raw = self._run_adb_optional("exec-out", "run-as", self._package_name, "cat", f"files/{filename}")
            if raw.strip():
                result = json.loads(raw)
                self._sync_effect_marker()
                return result
            time.sleep(0.025)
        raise TimeoutError(f"timed out waiting for Android permission result: {request.get('request_id', '')}")

    def _sync_effect_marker(self) -> None:
        if self._effect_marker_path is None:
            return
        raw = self._run_adb_optional("exec-out", "run-as", self._package_name, "cat", "files/effects.jsonl")
        if raw:
            self._effect_marker_path.parent.mkdir(parents=True, exist_ok=True)
            self._effect_marker_path.write_text(raw, encoding="utf-8")

    @staticmethod
    def _result_filename(request_id: str) -> str:
        return f"result_{re.sub(r'[^A-Za-z0-9_-]', '_', request_id)}.json"

    def _run_adb(self, *arguments: str) -> str:
        completed = subprocess.run(
            [str(self._adb_path), *(self._device_args()), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=self._timeout_seconds,
        )
        return completed.stdout

    def _run_adb_optional(self, *arguments: str) -> str:
        completed = subprocess.run(
            [str(self._adb_path), *(self._device_args()), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=self._timeout_seconds,
        )
        if completed.returncode != 0 or completed.stderr or completed.stdout.startswith("cat:"):
            return ""
        return completed.stdout

    def _device_args(self) -> list[str]:
        return ["-s", self._device_id] if self._device_id else []
