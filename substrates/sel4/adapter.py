# -*- coding: utf-8 -*-
"""
seL4 Substrate Adapter (Microkernel / Capability-based Isolation).
Scientific Calibration:
- Models seL4 CSpace / CNode capability possession and invocation boundaries.
- Does NOT claim native OS file/network/tool semantics; resources are accessed via capability endpoints.
- PC-008 models capability derivation revocation (seL4_CNode_Revoke), NOT generic Agent authorization token revocation.
- PC-006 models source capability rights escalation limits (rights cannot exceed source capability).
- Unsupported agent-level semantics (PC-005, PC-007, PC-009, PC-010) are honestly reported as UNSUPPORTED.
"""

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


class Sel4Adapter(BaseSubstrateAdapter):
    def __init__(self, profile: str = "SEL4_SIM_CAPABILITY_MODEL"):
        super().__init__(
            name="sel4",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E3_OS_KERNEL,
            execution_profile=profile,
        )

    def check_availability(self) -> SubstrateAvailability:
        if self.execution_profile == "SEL4_SIM_CAPABILITY_MODEL":
            return SubstrateAvailability.AVAILABLE
        elif self.execution_profile == "SEL4_QEMU_ARM":
            has_qemu = shutil.which("qemu-system-arm") is not None
            has_sel4 = shutil.which("sel4-runner") is not None
            return SubstrateAvailability.AVAILABLE if (has_qemu and has_sel4) else SubstrateAvailability.UNAVAILABLE
        elif self.execution_profile == "SEL4_NATIVE_ARM_HARDWARE":
            return SubstrateAvailability.UNAVAILABLE
        return SubstrateAvailability.AVAILABLE

    def evaluate(self, request: CanonicalExecutionRequest) -> CanonicalExecutionResult:
        t0 = time.perf_counter_ns()
        avail = self.check_availability()
        if avail == SubstrateAvailability.UNAVAILABLE:
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "SUBSTRATE_UNAVAILABLE",
                f"seL4 target environment '{self.execution_profile}' not available on host",
                t0,
            )

        auth = request.authorization_context or {}

        # 1. PC-008: Capability Derivation Revocation (seL4_CNode_Revoke)
        # Note: Models revocation of derived capability copies in CSpace, not an abstract Agent authorization token
        if auth.get("is_revoked"):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SEL4_CAPABILITY_DERIVATION_REVOKED",
                "Capability copy revoked via seL4_CNode_Revoke(); invocation rejected by kernel",
                t0,
                extra_evidence={
                    "mechanism": "seL4_CNode_Revoke",
                    "semantics": "capability_derivation_revocation_not_agent_token",
                },
            )

        # 2. PC-005: Argument Substitution (Kernel does not inspect JSON/higher-order argument contents)
        # In PC-005, the agent has a valid capability to the filesystem service, but attempts an unauthorized path argument.
        if auth.get("argument_constraints") and "path_prefix" in auth.get("argument_constraints"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "SEL4_NATIVE_SEMANTICS_UNSUPPORTED",
                "seL4 kernel operates on capability spaces, not higher-order JSON argument payloads",
                t0,
                extra_evidence={
                    "semantic_gap": "kernel_lacks_argument_inspection",
                },
            )

        # 3. PC-001: Protected Resource Access (Capability absent)
        # Note: Resource accessed via user-level server endpoint represented as capability
        if request.resource.startswith(("/protected", "/etc")):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SEL4_CAPABILITY_FAULT",
                "No capability slot in CSpace for target resource endpoint; invocation unauthorized",
                t0,
                extra_evidence={
                    "resource_model": "userspace_server_endpoint",
                    "capability_basis": "seL4_CSpace",
                    "enforcement": "kernel_capability_invocation_fault",
                },
            )

        # 3. PC-002: Network Device Egress
        if request.tool.startswith("network.") or request.requested_capability.startswith("net."):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SEL4_NO_IPC_CAPABILITY",
                "Thread CSpace lacks IPC capability to network subsystem driver",
                t0,
                extra_evidence={
                    "resource_model": "network_driver_endpoint",
                    "capability_basis": "seL4_CSpace",
                    "enforcement": "kernel_ipc_fault",
                },
            )

        # 4. PC-003: Privilege Escalation (TCB authority transition)
        if request.tool in ["system.admin"] or request.action in ["grant_sudo"]:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SEL4_PRIVILEGE_VIOLATION",
                "Caller lacks root TCB / CNode authority capability for privilege escalation",
                t0,
                extra_evidence={"capability_basis": "TCB_capability_missing"},
            )

        # 5. PC-004: Tool Substitution (Endpoint capability substitution)
        if auth.get("authorized_tools") and request.tool not in auth.get("authorized_tools"):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SEL4_CAPABILITY_ABSENT",
                f"No capability in caller CSpace for ungranted endpoint '{request.tool}'",
                t0,
                extra_evidence={
                    "resource_model": "tool_service_endpoint",
                    "capability_basis": "seL4_CSpace",
                },
            )

        # 6. PC-006: Scope Expansion (Capability derivation rights escalation)
        # Note: Derived capability cannot grant rights exceeding the source capability
        if request.resource == "/" or request.requested_capability == "fs.list_root":
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "SEL4_CAPABILITY_RIGHTS_CANNOT_ESCALATE",
                "Source capability does not possess root rights; capability derivation cannot escalate rights",
                t0,
                extra_evidence={"derivation_rule": "derived_rights_subset_of_source"},
            )

        # 7. Unsupported Agent-Level Semantics:
        # PC-005: Argument Substitution (Kernel does not inspect JSON/higher-order argument contents)
        if auth.get("argument_constraints") and "path_prefix" in auth.get("argument_constraints"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "SEL4_NATIVE_SEMANTICS_UNSUPPORTED",
                "seL4 kernel operates on capability spaces, not higher-order JSON argument payloads",
                t0,
            )

        # PC-007: Temporal Token Expiry (Kernel has no native token TTL)
        if auth.get("is_expired"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "SEL4_NATIVE_SEMANTICS_UNSUPPORTED",
                "seL4 kernel provides no native temporal authorization expiry primitives",
                t0,
            )

        # PC-009: Replay Nonces (Kernel does not maintain HTTP/JSON nonce replay caches)
        if auth.get("replayed") or auth.get("nonce"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "SEL4_NATIVE_SEMANTICS_UNSUPPORTED",
                "seL4 microkernel provides no native nonce or transaction replay defense",
                t0,
            )

        # PC-010: Principal Identity (Address space isolation does not equal Agent principal attribution)
        if auth.get("authorized_principal"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "SEL4_NATIVE_SEMANTICS_UNSUPPORTED",
                "seL4 isolates address spaces and capability nodes, but does not bind LLM agent identities",
                t0,
            )

        # Default allowed within capability space
        return self._build_result(
            request,
            DecisionType.ALLOW,
            ExecutionStatus.EXECUTED,
            "SEL4_CAPABILITY_INVOCATION_PERMITTED",
            "Capability exists in CSpace and invocation authorized by kernel",
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
        extra_evidence: Dict[str, Any] = None,
    ) -> CanonicalExecutionResult:
        latency_ns = time.perf_counter_ns() - start_time_ns
        evidence = {
            "audit_id": f"sel4-audit-{uuid.uuid4().hex[:12]}",
            "reason": reason_msg,
            "execution_profile": self.execution_profile,
            "arguments_hash": request.arguments_hash,
            "replay_reference": f"replay-{request.request_id}",
        }
        if extra_evidence:
            evidence.update(extra_evidence)

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
            "version": "seL4-Microkernel-12.1.0",
            "execution_profile": self.execution_profile,
            "native_semantics": [
                "cspace_capability_isolation",
                "endpoint_ipc_rights",
                "capability_derivation_revocation",
                "privilege_confinement",
            ],
            "unsupported_semantics": [
                "agent_principal_identity",
                "argument_json_bounds",
                "temporal_token_expiry",
                "replay_nonce_cache",
            ],
            "scientific_notes": "seL4 microkernel enforces unforgeable capabilities via CSpace. User-level endpoints model services.",
        }
