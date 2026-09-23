"""Android AppOps native baseline seam."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class AndroidAppOpsBaselineController:
    """Public contract seam for the native READ_CONTACTS AppOp."""

    def __init__(self, *, appops_allowed: bool | None = None) -> None:
        self._appops_allowed = appops_allowed

    def evaluate(self, request: Mapping[str, Any]) -> dict[str, Any]:
        request_id = str(request.get("request_id", ""))
        if self._appops_allowed is not True:
            return {
                "request_id": request_id,
                "authority": "ANDROID_APPOPS_READ_CONTACTS",
                "decision": "DENY",
                "execution_started": False,
                "execution_completed": False,
                "execution_effect": "NONE",
                "reason": "ANDROID_APPOPS_DENIED",
            }
        return {
            "request_id": request_id,
            "authority": "ANDROID_APPOPS_READ_CONTACTS",
            "decision": "ALLOW",
            "execution_started": True,
            "execution_completed": True,
            "execution_effect": "BOUNDED_APPOPS_FIXTURE",
            "reason": "ANDROID_APPOPS_ALLOWED",
        }
