# -*- coding: utf-8 -*-
"""Container Substrate Adapter.
Models a container namespace / cgroup boundary used as a deployment isolation layer.
"""

import os
import time
import uuid
import shutil
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


class ContainerAdapter(BaseSubstrateAdapter):
    def __init__(self):
        super().__init__(
            name="container",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E2_SANDBOX_RUNTIME,
            execution_profile="CONTAINER_NAMESPACE_BOUNDARY",
        )

    def check_availability(self) -> SubstrateAvailability:
        return SubstrateAvailability.AVAILABLE if (shutil.which("docker") or shutil.which("podman") or os.name == "posix") else SubstrateAvailability.UNAVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        avail = self.check_availability()
        if avail == SubstrateAvailability.UNAVAILABLE:
            return self._build_result(request, DecisionType.UNSUPPORTED, ExecutionStatus.UNSUPPORTED, "CONTAINER_UNAVAILABLE", "Container runtime unavailable on this host", t0, avail)

        auth = request.authorization_context or {}
        if auth.get("is_revoked"):
            return self._build_result(request, DecisionType.DENY, ExecutionStatus.NOT_EXECUTED, "CONTAINER_REVOKED", "Container isolation boundary blocks revoked authority", t0, avail)
        if auth.get("authorized_principal") and auth.get("authorized_principal") != request.principal:
            return self._build_result(request, DecisionType.DENY, ExecutionStatus.NOT_EXECUTED, "CONTAINER_PRINCIPAL_MISMATCH", "Container boundary preserves principal separation", t0, avail)
        if auth.get("replayed"):
            return self._build_result(request, DecisionType.UNSUPPORTED, ExecutionStatus.UNSUPPORTED, "CONTAINER_NATIVE_SEMANTICS_UNSUPPORTED", "Container boundary does not natively enforce replay semantics", t0, avail)
        return self._build_result(request, DecisionType.ALLOW, ExecutionStatus.EXECUTED, "CONTAINER_ALLOWED", "Execution permitted inside container boundary", t0, avail)

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
            evidence={"audit_id": f"container-audit-{uuid.uuid4().hex[:12]}", "reason": reason_msg, "arguments_hash": request.arguments_hash},
            latency_ns=time.perf_counter_ns() - start_time_ns,
            semantic_scope=SemanticScope.NATIVE if decision != DecisionType.UNSUPPORTED else SemanticScope.UNSUPPORTED,
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "version": "Container-Model-2026",
            "native_semantics": ["namespace_boundary", "cgroup_isolation"],
            "unsupported_semantics": ["principal_attribution", "task_authorization", "tool_binding", "temporal_expiry", "hot_revocation", "replay_protection"],
            "scientific_notes": "Container runtime is modeled as deployment isolation and process-boundary control for Appendix D boundary tests.",
        }
