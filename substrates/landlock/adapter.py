# -*- coding: utf-8 -*-
"""Landlock Substrate Adapter.
Models a Linux path sandbox boundary used as a lower-layer control in Appendix D.
"""

import os
import time
import uuid
from typing import Any, Dict
from vep.schema import (
    CanonicalExecutionRequest,
    CanonicalExecutionResult,
    SubstrateType,
    SubstrateAvailability,
    DecisionType,
    ExecutionStatus,
    AssuranceStatus,
    EnforcementLayer,
    SemanticScope,
)
from vep.adapters.base import BaseSubstrateAdapter


class LandlockAdapter(BaseSubstrateAdapter):
    def __init__(self):
        super().__init__(
            name="landlock",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E3_OS_KERNEL,
            execution_profile="LANDLOCK_PATH_SANDBOX",
        )

    def check_availability(self) -> SubstrateAvailability:
        return SubstrateAvailability.AVAILABLE if os.name == "posix" else SubstrateAvailability.UNAVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        avail = self.check_availability()
        if avail == SubstrateAvailability.UNAVAILABLE:
            return self._build_result(request, DecisionType.UNSUPPORTED, ExecutionStatus.UNSUPPORTED, "LANDLOCK_UNAVAILABLE", "Landlock unavailable on this host", t0, avail)

        auth = request.authorization_context or {}
        target_path = request.resource or request.arguments.get("path", "")
        if target_path and not str(target_path).startswith(("/workspace", "workspace", "./", ".\\")):
            return self._build_result(request, DecisionType.DENY, ExecutionStatus.NOT_EXECUTED, "LANDLOCK_PATH_DENIED", f"Path '{target_path}' blocked by Landlock boundary", t0, avail)

        if auth.get("is_revoked") or auth.get("is_expired") or auth.get("replayed") or auth.get("authorized_principal"):
            return self._build_result(request, DecisionType.UNSUPPORTED, ExecutionStatus.UNSUPPORTED, "LANDLOCK_NATIVE_SEMANTICS_UNSUPPORTED", "Landlock does not provide agent-identity semantics", t0, avail)

        return self._build_result(request, DecisionType.ALLOW, ExecutionStatus.EXECUTED, "LANDLOCK_PATH_ALLOWED", "Path allowed within sandbox boundary", t0, avail)

    def replay(self, request: CanonicalExecutionRequest, evidence_ref: Dict[str, Any]) -> CanonicalExecutionResult:
        return self.evaluate(request)

    def _build_result(self, request, decision, execution, reason_class, reason_msg, start_time_ns, availability):
        return CanonicalExecutionResult(
            request_id=request.request_id,
            substrate=self.name,
            substrate_type=self.substrate_type,
            substrate_availability=availability,
            decision=decision,
            execution=execution,
            assurance_status=AssuranceStatus.NOT_APPLICABLE,
            reason_class=reason_class,
            enforcement_layer=self.enforcement_layer,
            evidence={"audit_id": f"landlock-audit-{uuid.uuid4().hex[:12]}", "reason": reason_msg, "arguments_hash": request.arguments_hash},
            latency_ns=time.perf_counter_ns() - start_time_ns,
            semantic_scope=SemanticScope.NATIVE if decision != DecisionType.UNSUPPORTED else SemanticScope.UNSUPPORTED,
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "version": "Landlock-Model-2026",
            "native_semantics": ["filesystem_path_boundary"],
            "unsupported_semantics": ["principal_attribution", "task_authorization", "tool_binding", "temporal_expiry", "hot_revocation", "replay_protection"],
            "scientific_notes": "Landlock is modeled as a Linux path sandbox lower-layer control for Appendix D boundary tests.",
        }
