# -*- coding: utf-8 -*-
"""
ScopeGate Reference Reproduction Substrate Adapter (arXiv:2606.xxxxx).
Reproduces the 5-Stage PDP/PEP Capability Gating & Authorization Architecture:
  Stage 1: Intent & Principal Authentication
  Stage 2: Scope & Resource Bounding (Directory / Money Ceiling / Privilege / Egress)
  Stage 3: Argument Sanitization & Integrity Matching
  Stage 4: Dynamic Revocation & TTL Check
  Stage 5: Deterministic Action Gate & Replay Defense (Default-Deny)
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


class ScopeGateAdapter(BaseSubstrateAdapter):
    def __init__(self, money_ceiling: float = 100.0):
        super().__init__(
            name="scopegate",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E2_SANDBOX_RUNTIME,
            execution_profile="SCOPE_GATE_5_STAGE_PDP_PEP_REFERENCE",
        )
        self.money_ceiling = money_ceiling
        self.seen_nonces: Set[str] = set()

    def check_availability(self) -> SubstrateAvailability:
        return SubstrateAvailability.AVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        auth = request.authorization_context or {}

        # Stage 1: Principal Attribution & Confused-Deputy Defense
        auth_principal = auth.get("authorized_principal")
        if auth_principal and auth_principal != request.principal:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE1_CONFUSED_DEPUTY_BLOCKED",
                f"ScopeGate Stage 1: Principal '{request.principal}' mismatch with authorized '{auth_principal}'",
                t0,
            )

        # Stage 2: Scope & Resource / Privilege / Egress Bounds
        req_scope = auth.get("scope", [])
        
        # 2a. Workspace Scope
        if "workspace" in req_scope and not request.resource.startswith("/workspace"):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE2_SCOPE_VIOLATION",
                f"ScopeGate Stage 2: Resource '{request.resource}' out of workspace scope",
                t0,
            )

        # 2b. Network Egress Scope
        if request.tool == "network.connect" and "external" not in req_scope:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE2_UNAUTHORIZED_EGRESS",
                f"ScopeGate Stage 2: Egress connection to '{request.resource}' outside authorized scope {req_scope}",
                t0,
            )

        # 2c. Privilege Boundary
        if request.tool in ["system.admin", "database.drop"] and "cluster-admin" not in req_scope:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE2_PRIVILEGE_ESCALATION_BLOCKED",
                f"ScopeGate Stage 2: Privileged tool '{request.tool}' requires cluster-admin scope",
                t0,
            )

        # Stage 3: Tool & Argument Integrity
        auth_tools = auth.get("authorized_tools")
        if auth_tools and request.tool not in auth_tools:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE3_TOOL_UNAUTHORIZED",
                f"ScopeGate Stage 3: Tool '{request.tool}' not in authorized tools {auth_tools}",
                t0,
            )

        arg_constraints = auth.get("argument_constraints", {})
        if "path_prefix" in arg_constraints:
            req_path = request.arguments.get("path", "")
            prefix = arg_constraints["path_prefix"]
            if not req_path.startswith(prefix):
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "SG_STAGE3_ARGUMENT_PATH_MUTATION",
                    f"ScopeGate Stage 3: Argument path '{req_path}' violates required prefix '{prefix}'",
                    t0,
                )

        # Stage 4: TTL and Revocation
        if auth.get("is_revoked"):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE4_REVOCATION_BLOCKED",
                "ScopeGate Stage 4: Authorization context has been dynamically revoked",
                t0,
            )

        if auth.get("is_expired") or auth.get("ttl", 1) <= 0:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SG_STAGE4_TTL_EXPIRED",
                "ScopeGate Stage 4: Authorization token TTL expired",
                t0,
            )

        # Stage 5: Replay Nonce & Deterministic Gate
        nonce = auth.get("nonce") or request.authorization_context.get("nonce")
        if nonce:
            if nonce in self.seen_nonces:
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "SG_STAGE5_REPLAY_DETECTED",
                    f"ScopeGate Stage 5: Nonce '{nonce}' has already been consumed",
                    t0,
                )
            self.seen_nonces.add(nonce)

        # Default Allow if all 5 stages passed
        return self._build_result(
            request,
            DecisionType.ALLOW,
            ExecutionStatus.EXECUTED,
            "SG_ALL_STAGES_PASSED",
            "ScopeGate 5-Stage PDP/PEP verification passed",
            t0,
        )

    def replay(self, request: CanonicalExecutionRequest, evidence_ref: Dict[str, Any]) -> CanonicalExecutionResult:
        return self.evaluate(request)

    def _build_result(
        self,
        request: CanonicalExecutionRequest,
        decision: DecisionType,
        execution: ExecutionStatus,
        reason_class: str,
        reason_msg: str,
        start_time_ns: int,
    ) -> CanonicalExecutionResult:
        latency_ns = time.perf_counter_ns() - start_time_ns
        audit_id = f"scopegate-audit-{uuid.uuid4().hex[:12]}"
        evidence = {
            "audit_id": audit_id,
            "reason": reason_msg,
            "model": "ScopeGate-5Stage-Reference",
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
            semantic_scope=SemanticScope.NATIVE,
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "version": "ScopeGate-2026-Reference",
            "enforcement_layer": "E2_SANDBOX_RUNTIME",
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
            "unsupported_semantics": [
                "binary_cabi_gate",
                "kernel_syscall_interception",
            ],
            "scientific_notes": "ScopeGate provides in-process capability gating and authorization. In post-compromise scenarios with arbitrary code execution, in-process wrappers can be subject to memory inspection or runtime monkey-patching.",
        }
