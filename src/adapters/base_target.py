# -*- coding: utf-8 -*-
"""
VEP RFC-001: Universal Governance Target Interface
Defines the standard decoupled protocol for evaluating any Agent Governance Substrate.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class UniversalGovernanceTarget(ABC):
    """
    Decoupled interface for any Agent Governance System under test.
    Conforming implementations MAY be DROS, Bare Execution, or third-party gateways.
    """

    @abstractmethod
    def get_target_info(self) -> Dict[str, str]:
        """Returns target metadata (name, version, engine_mode)"""
        pass

    @abstractmethod
    def evaluate_action(self, role: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates an agent action intent.
        Must return:
          - allowed (bool): True if allowed, False if blocked
          - reason (str): Error reason code
          - latency_ns (int): Gate decision latency
        """
        pass

    @abstractmethod
    def revoke_capability(self, capability_name: str) -> int:
        """Triggers policy revocation, returns swap latency in nanoseconds"""
        pass

    @abstractmethod
    def reset_state(self) -> bool:
        """Purges caches and restores state to pristine baseline (Delta S = 0)"""
        pass
