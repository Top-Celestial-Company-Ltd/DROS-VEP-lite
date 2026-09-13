# -*- coding: utf-8 -*-
"""
VEP Canonical Execution Schema (v1.0)
Defines standardized data contracts for multi-substrate post-compromise benchmarking.
Implementation-independent, strictly separates runtime execution from formal assurance.
"""

from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict


class SubstrateType(str, Enum):
    RUNTIME = "RUNTIME"
    ASSURANCE = "ASSURANCE"


class SubstrateAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ERROR = "ERROR"
    UNSUPPORTED = "UNSUPPORTED"


class ExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    NOT_EXECUTED = "NOT_EXECUTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ERROR = "ERROR"
    UNSUPPORTED = "UNSUPPORTED"


class AssuranceStatus(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PASS = "PASS"
    FAIL = "FAIL"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"


class EnforcementLayer(str, Enum):
    E0_NONE = "E0_NONE"
    E1_APP_API = "E1_APP_API"
    E2_SANDBOX_RUNTIME = "E2_SANDBOX_RUNTIME"
    E3_OS_KERNEL = "E3_OS_KERNEL"
    E4_HARDWARE = "E4_HARDWARE"
    E5_FORMAL_ASSURANCE = "E5_FORMAL_ASSURANCE"


class SemanticScope(str, Enum):
    NATIVE = "NATIVE"
    PROFILE = "PROFILE"
    APPLICATION = "APPLICATION"
    FORMAL = "FORMAL"
    UNSUPPORTED = "UNSUPPORTED"


class PostCompromiseProperty(str, Enum):
    RESOURCE_AUTHORITY = "RESOURCE_AUTHORITY"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    TOOL_ATTRIBUTION = "TOOL_ATTRIBUTION"
    ARGUMENT_INTEGRITY = "ARGUMENT_INTEGRITY"
    SCOPE_NON_EXPANSION = "SCOPE_NON_EXPANSION"
    TEMPORAL_AUTHORITY = "TEMPORAL_AUTHORITY"
    EXECUTION_UNIQUENESS = "EXECUTION_UNIQUENESS"
    PRINCIPAL_ATTRIBUTION = "PRINCIPAL_ATTRIBUTION"


def canonicalize_json(obj: Any) -> str:
    """Produces a deterministic, whitespace-stripped, sorted-key JSON string."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(obj: Any) -> str:
    """Computes SHA-256 over canonicalized JSON representation."""
    canonical = canonicalize_json(obj).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


@dataclass
class CanonicalExecutionRequest:
    request_id: str
    principal: str
    task: str
    tool: str
    action: str
    resource: str
    arguments: Dict[str, Any]
    requested_capability: str
    authorization_context: Dict[str, Any]
    timestamp: str
    compromise_state: str = "POST_COMPROMISE"
    arguments_hash: str = field(init=False)

    def __post_init__(self):
        # Automatically compute arguments_hash from arguments dict to eliminate drift
        self.arguments_hash = compute_hash(self.arguments)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalExecutionRequest":
        copied = dict(data)
        # Pop arguments_hash if present since __post_init__ auto-computes it
        copied.pop("arguments_hash", None)
        return cls(**copied)


@dataclass
class CanonicalExecutionResult:
    request_id: str
    substrate: str
    substrate_type: SubstrateType
    substrate_availability: SubstrateAvailability
    decision: DecisionType
    execution: ExecutionStatus
    assurance_status: AssuranceStatus
    reason_class: str
    enforcement_layer: EnforcementLayer
    evidence: Dict[str, Any]
    latency_ns: int
    semantic_scope: SemanticScope = SemanticScope.NATIVE

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["substrate_type"] = self.substrate_type.value
        d["substrate_availability"] = self.substrate_availability.value
        d["decision"] = self.decision.value
        d["execution"] = self.execution.value
        d["assurance_status"] = self.assurance_status.value
        d["enforcement_layer"] = self.enforcement_layer.value
        d["semantic_scope"] = self.semantic_scope.value
        return d
