# -*- coding: utf-8 -*-
"""
VEP Baseline Target: Bare Execution (Unprotected Scientific Control B0)
"""

from .base_target import UniversalGovernanceTarget
from typing import Dict, Any

class BareRuntimeAdapter(UniversalGovernanceTarget):
    """Passes all tool requests unconditionally with 0 governance (Baseline B0)"""

    def get_target_info(self) -> Dict[str, str]:
        return {
            "name": "Bare-Unprotected-Runtime",
            "version": "1.0.0",
            "engine_mode": "no-governance-baseline"
        }

    def evaluate_action(self, role: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "allowed": True,
            "reason": "OK_UNPROTECTED_EXECUTION",
            "latency_ns": 0
        }

    def revoke_capability(self, capability_name: str) -> int:
        return 0

    def reset_state(self) -> bool:
        return True
