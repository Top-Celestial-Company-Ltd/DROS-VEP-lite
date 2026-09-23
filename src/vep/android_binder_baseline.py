"""Android Binder protected-service baseline seam."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class AndroidBinderBaselineController:
    """Contract seam for a permission-protected Binder service."""

    def __init__(self, *, binder_permission_granted: bool | None = None) -> None:
        self._binder_permission_granted = binder_permission_granted

    def evaluate(self, request: Mapping[str, Any]) -> dict[str, Any]:
        request_id = str(request.get("request_id", ""))
        if self._binder_permission_granted is not True:
            return {
                "request_id": request_id,
                "authority": "ANDROID_BINDER_SERVICE_PERMISSION",
                "decision": "DENY",
                "execution_started": False,
                "execution_completed": False,
                "execution_effect": "NONE",
                "reason": "BINDER_SERVICE_PERMISSION_DENIED",
            }
        return {
            "request_id": request_id,
            "authority": "ANDROID_BINDER_SERVICE_PERMISSION",
            "decision": "ALLOW",
            "execution_started": True,
            "execution_completed": True,
            "execution_effect": "BOUNDED_BINDER_FIXTURE",
            "reason": "BINDER_SERVICE_PERMISSION_GRANTED",
        }
