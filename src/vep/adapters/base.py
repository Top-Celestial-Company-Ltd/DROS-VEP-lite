# -*- coding: utf-8 -*-
"""
VEP Base Substrate Adapter Interface.
All substrates (DROS, WASI, seL4, CHERI, TLA+) must conform to this contract.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from vep.schema import (
    CanonicalExecutionRequest,
    CanonicalExecutionResult,
    SubstrateType,
    SubstrateAvailability,
    EnforcementLayer,
)


class BaseSubstrateAdapter(ABC):
    def __init__(
        self,
        name: str,
        substrate_type: SubstrateType,
        enforcement_layer: EnforcementLayer,
        execution_profile: str = "DEFAULT_PROFILE",
    ):
        self.name = name
        self.substrate_type = substrate_type
        self.enforcement_layer = enforcement_layer
        self.execution_profile = execution_profile

    @abstractmethod
    def check_availability(self) -> SubstrateAvailability:
        """Returns whether this substrate is installed and usable on the host."""
        pass

    @abstractmethod
    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        """
        Evaluates the post-compromise execution attempt against this substrate.
        Runtime substrates decide and attempt execution.
        Assurance substrates evaluate formal invariants without real execution.
        """
        pass

    @abstractmethod
    def replay(self, request: CanonicalExecutionRequest, evidence_ref: Dict[str, Any]) -> CanonicalExecutionResult:
        """
        Deterministically replays an execution request using recorded parameters.
        Must reproduce identical decision and evidence characteristics.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns metadata:
        - version
        - native_semantics
        - unsupported_semantics
        - scientific_notes
        """
        pass
