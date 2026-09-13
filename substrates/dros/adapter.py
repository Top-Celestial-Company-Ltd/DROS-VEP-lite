# -*- coding: utf-8 -*-
"""
DROS Substrate Adapter (Reference Agent-Aware Execution Governance).
Enforces fine-grained principal attribution, argument boundaries, hot revocation, expiry, and replay nonces.
Enforcement Layer is strictly defined by deployment mode:
  - runtime (default): E2_SANDBOX_RUNTIME
  - kernel/ffi: E3_OS_KERNEL
"""

import time
import uuid
from typing import Any, Dict, Set
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


class DrosAdapter(BaseSubstrateAdapter):
    def __init__(self, deployment_mode: str = "runtime"):
        layer = EnforcementLayer.E3_OS_KERNEL if deployment_mode == "kernel" else EnforcementLayer.E2_SANDBOX_RUNTIME
        profile = "DROS_KERNEL_CABI_PEP" if deployment_mode == "kernel" else "DROS_INBAND_RUNTIME_PEP"
        super().__init__(
            name="dros",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=layer,
            execution_profile=profile,
        )
        self.deployment_mode = deployment_mode
        self.seen_nonces: Set[str] = set()

    def check_availability(self) -> SubstrateAvailability:
        return SubstrateAvailability.AVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        auth = request.authorization_context or {}

        # 1. Check Principal Attribution
        auth_principal = auth.get("authorized_principal")
        if auth_principal and auth_principal != request.principal:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "PRINCIPAL_ATTRIBUTION_MISMATCH",
                f"Principal '{request.principal}' is not authorized; expected '{auth_principal}'",
                t0,
            )

        # 2. Check Expiry
        if auth.get("is_expired") or auth.get("ttl", 1) <= 0:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "AUTHORIZATION_EXPIRED",
                "Token TTL expired or is_expired flag set",
                t0,
            )

        # 3. Check Hot Revocation
        if auth.get("is_revoked"):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "AUTHORIZATION_REVOKED",
                f"Authorization was explicitly revoked: {auth.get('revocation_reason', 'admin_revocation')}",
                t0,
            )

        # 4. Check Replay / Nonce
        nonce = auth.get("nonce") or request.arguments.get("nonce")
        if nonce:
            if nonce in self.seen_nonces or auth.get("replayed"):
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "REPLAY_DETECTED",
                    f"Duplicate execution detected with nonce '{nonce}'",
                    t0,
                )
            self.seen_nonces.add(nonce)

        # 5. Check Tool Binding
        authorized_tools = auth.get("authorized_tools")
        if authorized_tools and request.tool not in authorized_tools:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "TOOL_SUBSTITUTION_DENIED",
                f"Tool '{request.tool}' not in authorized tools {authorized_tools}",
                t0,
            )

        # 6. Check Scope
        scopes = auth.get("scope", [])
        if "workspace" in scopes and request.resource.startswith(("/protected", "/etc", "/")):
            if not request.resource.startswith("/workspace") and not request.resource.startswith("workspace"):
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "SCOPE_VIOLATION",
                    f"Resource '{request.resource}' out of authorized scope {scopes}",
                    t0,
                )

        # 7. Check Argument-Level Constraints
        arg_constraints = auth.get("argument_constraints", {})
        prefix = arg_constraints.get("path_prefix")
        if prefix:
            target_path = request.arguments.get("path", "")
            if not target_path.startswith(prefix):
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "ARGUMENT_BOUNDS_VIOLATION",
                    f"Path argument '{target_path}' violates prefix requirement '{prefix}'",
                    t0,
                )

        # 8. Check Privilege Escalation / Unprivileged Tools
        if request.tool in ["system.admin", "database.drop"] and "cluster-admin" not in scopes:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "PRIVILEGE_ESCALATION_DENIED",
                f"Privileged tool '{request.tool}' denied for unprivileged scope {scopes}",
                t0,
            )

        # 9. Check Egress
        if request.tool == "network.connect" and "external" not in scopes:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "UNAUTHORIZED_EGRESS",
                f"Network egress to '{request.resource}' denied",
                t0,
            )

        # If all policy checks pass, allow execution
        return self._build_result(
            request,
            DecisionType.ALLOW,
            ExecutionStatus.EXECUTED,
            "POLICY_CONFORMANCE_ALLOW",
            "Action conforming to DROS policy",
            t0,
        )

    def replay(self, request: CanonicalExecutionRequest, evidence_ref: Dict[str, Any]) -> CanonicalExecutionResult:
        # Replay executes evaluation with recorded parameters
        return self.evaluate(request)

    def _build_result(
        self,
        request: CanonicalExecutionRequest,
        decision: DecisionType,
        execution: ExecutionStatus,
        reason_class: str,
        reason_msg: str,
        start_time_ns: int,
        semantic_scope: SemanticScope = SemanticScope.NATIVE,
    ) -> CanonicalExecutionResult:
        latency_ns = time.perf_counter_ns() - start_time_ns
        audit_id = f"dros-audit-{uuid.uuid4().hex[:12]}"
        evidence = {
            "audit_id": audit_id,
            "reason": reason_msg,
            "deployment_mode": self.deployment_mode,
            "policy_version": "v1.0-commercial",
            "arguments_hash": request.arguments_hash,
            "replay_reference": f"replay-{request.request_id}",
        }
        return CanonicalExecutionResult(
            request_id=request.request_id,
            substrate=self.name,
            substrate_type=self.substrate_type,
            substrate_availability=SubstrateAvailability.AVAILABLE,
            decision=decision,
            execution=execution,
            assurance_status=AssuranceStatus.NOT_APPLICABLE,
            reason_class=reason_class,
            enforcement_layer=self.enforcement_layer,
            evidence=evidence,
            latency_ns=latency_ns,
            semantic_scope=semantic_scope,
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "deployment_mode": self.deployment_mode,
            "native_semantics": [
                "principal_attribution",
                "task_authorization",
                "tool_binding",
                "argument_bounds",
                "scope_containment",
                "temporal_expiry",
                "hot_revocation",
                "replay_protection",
            ],
            "unsupported_semantics": [],
            "scientific_notes": "Reference in-band execution governance for compromised agents.",
        }
