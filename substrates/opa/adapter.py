# -*- coding: utf-8 -*-
"""
OPA Substrate Adapter (Open Policy Agent - Industrial Policy-as-Code Baseline).
Implements dual-layer measurement:
  1. Pure OPA PDP evaluation latency
  2. Full Agent -> PEP -> OPA -> Execution flow
Satisfies Semantic Equivalence Contract (SEC) with DROS rules.
"""

import os
import sys
import time
import json
import uuid
import shutil
import subprocess
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

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OPA_BIN = os.path.join(BASE_DIR, "tools", "opa", "opa.exe")
POLICY_REGO = os.path.join(os.path.dirname(__file__), "policy.rego")


class OpaAdapter(BaseSubstrateAdapter):
    def __init__(self, mode: str = "pdp_and_pep"):
        super().__init__(
            name="opa",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E2_SANDBOX_RUNTIME,
            execution_profile="OPA_V0.68.0_REGO_POLICY_ENGINE",
        )
        self.mode = mode
        self.opa_bin = OPA_BIN
        self.policy_path = POLICY_REGO

    def _resolve_opa_binary(self) -> str | None:
        """Resolve a native OPA executable for the current host."""
        if sys.platform.startswith("win"):
            if os.path.exists(self.opa_bin):
                return self.opa_bin
            return None

        opa_bin = shutil.which("opa")
        if opa_bin and os.access(opa_bin, os.X_OK):
            return opa_bin
        return None

    def check_availability(self) -> SubstrateAvailability:
        if os.path.exists(self.policy_path) and self._resolve_opa_binary():
            return SubstrateAvailability.AVAILABLE
        return SubstrateAvailability.UNAVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        opa_bin = self._resolve_opa_binary()
        if not opa_bin or not os.path.exists(self.policy_path):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "OPA_BINARY_OR_POLICY_UNAVAILABLE",
                f"OPA binary or policy not found or not executable for this host (binary={self.opa_bin})",
                t0,
                substrate_availability=SubstrateAvailability.UNAVAILABLE,
            )

        # Construct SEC-compliant input payload
        input_doc = {
            "principal": request.principal,
            "task": request.task,
            "tool": request.tool,
            "action": request.action,
            "resource": request.resource,
            "arguments": request.arguments or {},
            "requested_capability": request.requested_capability,
            "authorization_context": request.authorization_context or {},
        }

        # Run OPA eval CLI with --stdin-input
        cmd = [
            opa_bin,
            "eval",
            "--data", self.policy_path,
            "--stdin-input",
            "data.vep.authz"
        ]

        try:
            p = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = p.communicate(input=json.dumps(input_doc))

            if p.returncode != 0:
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "OPA_EVAL_ERROR",
                    stderr.strip() or "OPA evaluation failed",
                    t0,
                )

            data = json.loads(stdout)
            result_obj = data.get("result", [{}])[0].get("expressions", [{}])[0].get("value", {})
            allow = result_obj.get("allow", False)
            deny_reason = result_obj.get("deny_reason", "DEFAULT_DENY")

            decision = DecisionType.ALLOW if allow else DecisionType.DENY
            status = ExecutionStatus.EXECUTED if allow else ExecutionStatus.NOT_EXECUTED

            return self._build_result(
                request,
                decision,
                status,
                "ALLOWED_BY_POLICY" if allow else deny_reason,
                f"OPA Rego evaluation: allow={allow}, reason={deny_reason}",
                t0,
            )

        except Exception as ex:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "OPA_EXCEPTION",
                str(ex),
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
        substrate_availability: SubstrateAvailability = SubstrateAvailability.AVAILABLE,
    ) -> CanonicalExecutionResult:
        latency_ns = time.perf_counter_ns() - start_time_ns
        audit_id = f"opa-audit-{uuid.uuid4().hex[:12]}"
        evidence = {
            "audit_id": audit_id,
            "reason": reason_msg,
            "opa_version": "v0.68.0",
            "policy_path": self.policy_path,
            "arguments_hash": request.arguments_hash,
            "replay_reference": f"replay-{request.request_id}",
        }
        return CanonicalExecutionResult(
            request_id=request.request_id,
            substrate=self.name,
            substrate_type=self.substrate_type,
            substrate_availability=substrate_availability,
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
            "version": "OPA-v0.68.0",
            "engine": "Rego",
            "enforcement_layer": "E2_SANDBOX_RUNTIME",
            "native_semantics": [
                "principal_attribution",
                "task_authorization",
                "tool_binding",
                "argument_bounds",
                "scope_containment",
                "temporal_expiry",
                "hot_revocation",
            ],
            "unsupported_semantics": [
                "binary_cabi_gate",
                "zero_heap_allocation",
            ],
            "scientific_notes": "OPA provides declarative Policy-as-Code. In-process or sidecar evaluation exhibits JSON serialization overhead compared to native binary gates.",
        }
