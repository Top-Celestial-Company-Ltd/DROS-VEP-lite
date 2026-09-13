# -*- coding: utf-8 -*-
"""
WASI Substrate Adapter (WebAssembly / Capability-oriented Execution Isolation).
Enforces capability sandbox boundaries (filesystem preopened paths, socket flags).
Scientifically notes unsupported agent-level semantics:
  - Agent principal attribution: UNSUPPORTED
  - Complex argument semantic rules: UNSUPPORTED
  - Dynamic token expiry: UNSUPPORTED
  - Hot authorization revocation: UNSUPPORTED
  - Duplicate replay protection: UNSUPPORTED
"""

import time
import uuid
from typing import Any, Dict, List
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


class WasiAdapter(BaseSubstrateAdapter):
    def __init__(self, preopened_dirs: List[str] = None, allow_net: bool = False):
        super().__init__(
            name="wasi",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E2_SANDBOX_RUNTIME,
            execution_profile="WASI_PREVIEW1_DESCRIPTOR_SANDBOX",
        )
        self.preopened_dirs = preopened_dirs or ["/workspace"]
        self.allow_net = allow_net

    def check_availability(self) -> SubstrateAvailability:
        return SubstrateAvailability.AVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        auth = request.authorization_context or {}

        # 1. Non-native Semantics: Argument semantic rules (PC-005)
        # Inside a granted directory capability, WASI does not inspect application argument bounds
        if auth.get("argument_constraints") and "path_prefix" in auth.get("argument_constraints"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "WASI_NATIVE_SEMANTICS_UNSUPPORTED",
                "WASI capability isolation operates at directory descriptor level, not application argument level",
                t0,
            )

        # 2. Native Sandbox Capability Check: Filesystem Preopened boundary (PC-001, PC-006)
        if request.tool.startswith("filesystem.") or request.requested_capability.startswith("fs."):
            target_path = request.arguments.get("path") or request.resource or ""
            # If requesting explicit root / or /protected outside preopened directory:
            is_within_preopened = any(target_path.startswith(p) for p in self.preopened_dirs)
            if not is_within_preopened:
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "WASI_CAPABILITY_FAULT",
                    f"Path '{target_path}' not within preopened directories {self.preopened_dirs}",
                    t0,
                )

        # 2. Native Sandbox Capability Check: Network socket capability (PC-002)
        if request.tool.startswith("network.") or request.requested_capability.startswith("net."):
            if not self.allow_net:
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "WASI_NET_CAPABILITY_FAULT",
                    "Network capability denied by WASI sandbox manifest (no socket rights)",
                    t0,
                )

        # 3. Non-native Semantics: Argument semantic rules (PC-005)
        if auth.get("argument_constraints") and "path_prefix" in auth.get("argument_constraints"):
            # Inside a preopened directory, WASI does not inspect business argument semantics
            target_path = request.arguments.get("path", "")
            # If target_path is technically outside preopen, it was caught above.
            # But if it is an argument substitution question or specific sub-path rule:
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "WASI_NATIVE_SEMANTICS_UNSUPPORTED",
                "WASI capability isolation operates at directory descriptor level, not application argument level",
                t0,
            )

        # 4. Non-native Semantics: Expiry & Revocation (PC-007, PC-008)
        if auth.get("is_expired") or auth.get("is_revoked"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "WASI_NATIVE_SEMANTICS_UNSUPPORTED",
                "WASI sandbox has no native temporal expiry or dynamic revocation mechanisms",
                t0,
            )

        # 5. Non-native Semantics: Principal attribution & Tool substitution (PC-004, PC-010)
        if auth.get("authorized_principal") or auth.get("authorized_tools"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "WASI_NATIVE_SEMANTICS_UNSUPPORTED",
                "WASI sandbox cannot bind LLM agent identity or task-tool authorizations",
                t0,
            )

        # 6. Non-native Semantics: Replay Nonce (PC-009)
        if auth.get("replayed") or auth.get("nonce"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "WASI_NATIVE_SEMANTICS_UNSUPPORTED",
                "WASI runtime provides no native nonce or replay prevention layer",
                t0,
            )

        # Default allowed within sandbox boundary
        return self._build_result(
            request,
            DecisionType.ALLOW,
            ExecutionStatus.EXECUTED,
            "WASI_SANDBOX_ALLOW",
            "Execution permitted within WASI sandbox capability bounds",
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
        evidence = {
            "audit_id": f"wasi-audit-{uuid.uuid4().hex[:12]}",
            "reason": reason_msg,
            "preopened_dirs": self.preopened_dirs,
            "allow_net": self.allow_net,
            "arguments_hash": request.arguments_hash,
            "replay_reference": f"replay-{request.request_id}",
        }
        scope = SemanticScope.UNSUPPORTED if decision == DecisionType.UNSUPPORTED else SemanticScope.NATIVE
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
            semantic_scope=scope,
        )

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "version": "WASI-Preview1-Model",
            "native_semantics": ["filesystem_preopen_boundary", "network_capability_flag"],
            "unsupported_semantics": [
                "principal_attribution",
                "task_authorization",
                "argument_bounds",
                "temporal_expiry",
                "hot_revocation",
                "replay_protection",
            ],
            "scientific_notes": "WASI provides strong syscall and resource sandboxing, but does not possess Agent-level authorization vocabulary.",
        }
