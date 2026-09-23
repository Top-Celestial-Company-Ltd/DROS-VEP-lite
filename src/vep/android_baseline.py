"""Minimal Android baseline reference seam for the first TDD slice.

This module is intentionally an in-process app-side reference boundary.  It
does not claim AVD, Android framework, SELinux, Binder, or OS-wide
enforcement.  ``AndroidBaselineController`` only forwards a request to the
app-side boundary and returns its observable result; authorization is owned by
``AndroidActionBoundary``.
"""

from __future__ import annotations

import json
import base64
import re
import subprocess
import threading
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class AndroidActionBoundary:
    """Bounded action fixture that owns the first app-side decision."""

    _ACTION_CAPABILITIES = {
        "READ_CONTACTS": "CAP_CONTACTS",
    }

    def __init__(self, *, effect_marker_path: Path) -> None:
        self._effect_marker_path = effect_marker_path
        self._revoked_principals: set[str] = set()

    def revoke(self, principal: str) -> None:
        self._revoked_principals.add(principal)

    def evaluate(self, request: Mapping[str, Any]) -> dict[str, Any]:
        required = self._ACTION_CAPABILITIES.get(str(request.get("action", "")))
        capability = request.get("capability")
        principal = str(request.get("principal", ""))

        if required is None:
            return self._denied(request, "UNKNOWN_ACTION")
        if principal in self._revoked_principals:
            return self._denied(request, "AUTHORITY_REVOKED")
        if capability != required:
            return self._denied(request, "CAPABILITY_MISSING")

        result = self._base_result(request)
        result.update(
            {
                "decision": "ALLOW",
                "execution_started": True,
                "execution_completed": True,
                "execution_effect": "BOUNDED_FIXTURE",
                "reason": "CAPABILITY_AUTHORIZED",
            }
        )
        self._record_effect(request)
        return result

    def _denied(self, request: Mapping[str, Any], reason: str) -> dict[str, Any]:
        result = self._base_result(request)
        result.update(
            {
                "decision": "DENY",
                "execution_started": False,
                "execution_completed": False,
                "execution_effect": "NONE",
                "reason": reason,
            }
        )
        return result

    @staticmethod
    def _base_result(request: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "request_id": request.get("request_id", ""),
            "decision_latency_ns": 0,
            "app_elapsed_ns": 0,
            "policy_hash": request.get("policy_version", ""),
        }

    def _record_effect(self, request: Mapping[str, Any]) -> None:
        self._effect_marker_path.parent.mkdir(parents=True, exist_ok=True)
        with self._effect_marker_path.open("a", encoding="utf-8") as marker:
            marker.write(
                json.dumps(
                    {
                        "request_id": request.get("request_id", ""),
                        "effect": "BOUNDED_FIXTURE",
                    },
                    sort_keys=True,
                )
                + "\n"
            )


class AndroidBaselineController:
    """Host-side forwarding seam; it does not perform authorization."""

    def __init__(
        self,
        *,
        effect_marker_path: Path,
        action_boundary: AndroidActionBoundary | None = None,
        adb_path: Path | None = None,
        package_name: str | None = None,
        activity_name: str | None = None,
        device_id: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._action_boundary = action_boundary or AndroidActionBoundary(
            effect_marker_path=effect_marker_path
        )
        self._effect_marker_path = effect_marker_path
        self._adb_path = adb_path
        self._package_name = package_name
        self._activity_name = activity_name
        self._device_id = device_id
        self._timeout_seconds = timeout_seconds
        self._device_initialized = False
        self._initialization_lock = threading.Lock()

    def submit(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Forward one request to the app-side bounded action boundary."""

        if self._adb_path is not None:
            return self._submit_via_adb(request)
        return self._action_boundary.evaluate(request)

    def revoke(self, principal: str) -> dict[str, Any]:
        """Revoke one principal without evaluating or executing an action."""

        if self._adb_path is None:
            self._action_boundary.revoke(principal)
            return {"revoked": True, "principal": principal}

        self._prepare_device()
        self._run_adb(
            *self._adb_arguments(),
            "shell",
            "am",
            "start",
            "-W",
            "-n",
            f"{self._package_name}/{self._activity_name}",
            "--es",
            "revoke_principal",
            principal,
        )
        return {"revoked": True, "principal": principal}

    def submit_ingress(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Submit one request to the app-side ingress receiver only."""

        if self._adb_path is None:
            raise ValueError("ingress mode requires an ADB-connected controller")
        if not self._package_name:
            raise ValueError("ADB mode requires package_name")
        self._prepare_device()
        payload = json.dumps(dict(request), ensure_ascii=False, separators=(",", ":"))
        encoded_payload = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        self._run_adb(
            *self._adb_arguments(),
            "shell",
            "am",
            "broadcast",
            "-a",
            "io.dros.tmc.baseline.REQUEST_INGRESS",
            "-n",
            f"{self._package_name}/.RequestIngressReceiver",
            "--es",
            "request_b64",
            encoded_payload,
        )
        return {"request_id": request.get("request_id", ""), "submitted": True}

    def collect_ingress_records(self) -> str:
        """Read app-side ingress records without interpreting authorization."""

        return self.collect_app_records("ingress_records.jsonl")

    def collect_app_records(self, filename: str) -> str:
        """Read one app-side stage record file without interpreting it."""

        if self._adb_path is None or not self._package_name:
            raise ValueError("ingress records require an ADB-connected controller")
        return self._run_adb_optional(
            *self._adb_arguments(),
            "exec-out",
            "run-as",
            self._package_name,
            "cat",
            f"files/{filename}",
        )

    def _submit_via_adb(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if not self._package_name or not self._activity_name:
            raise ValueError("ADB mode requires package_name and activity_name")

        self._prepare_device()
        adb = self._adb_arguments()
        payload = json.dumps(dict(request), ensure_ascii=False, separators=(",", ":"))
        encoded_payload = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        self._run_adb(
            *adb,
            "shell",
            "am",
            "start",
            "-W",
            "-n",
            f"{self._package_name}/{self._activity_name}",
            "--es",
            "request_b64",
            encoded_payload,
        )
        result_file = self._result_filename(str(request.get("request_id", "")))
        raw_result = self._read_result_file(
            adb, result_file, str(request.get("request_id", ""))
        )
        result = json.loads(raw_result)
        raw_effect = self._run_adb_optional(
            *adb,
            "exec-out",
            "run-as",
            self._package_name,
            "cat",
            "files/effects.jsonl",
        )
        if raw_effect:
            self._effect_marker_path.parent.mkdir(parents=True, exist_ok=True)
            self._effect_marker_path.write_text(raw_effect, encoding="utf-8")
        return result

    @staticmethod
    def _result_filename(request_id: str) -> str:
        safe_request_id = re.sub(r"[^A-Za-z0-9_-]", "_", request_id)
        return f"result_{safe_request_id}.json"

    def _read_result_file(
        self,
        adb: list[str],
        result_file: str,
        request_id: str,
    ) -> str:
        for _ in range(80):
            raw_result = self._run_adb_optional(
                *adb,
                "exec-out",
                "run-as",
                self._package_name,
                "cat",
                f"files/{result_file}",
            )
            if raw_result.strip():
                return raw_result
            time.sleep(0.025)
        raise TimeoutError(f"timed out waiting for Android result: {request_id}")

    def _adb_arguments(self) -> list[str]:
        arguments: list[str] = []
        if self._device_id:
            arguments.extend(["-s", self._device_id])
        return arguments

    def _prepare_device(self) -> None:
        with self._initialization_lock:
            if self._device_initialized:
                return
            if not self._package_name:
                raise ValueError("ADB mode requires package_name")
            self._run_adb(
                *self._adb_arguments(), "shell", "pm", "clear", self._package_name
            )
            self._device_initialized = True

    def _run_adb(self, *arguments: str) -> str:
        completed = subprocess.run(
            [str(self._adb_path), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=self._timeout_seconds,
        )
        return completed.stdout

    def _run_adb_optional(self, *arguments: str) -> str:
        completed = subprocess.run(
            [str(self._adb_path), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=self._timeout_seconds,
        )
        if (
            completed.returncode != 0
            or completed.stderr
            or completed.stdout.startswith("cat:")
        ):
            return ""
        return completed.stdout
