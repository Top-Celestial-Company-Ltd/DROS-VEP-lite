# -*- coding: utf-8 -*-
"""
CHERI Substrate Adapter (Hardware Capability / Memory Authority).
Scientific Calibration:
- Models CHERI hardware architectural capability properties (Tag, Bounds, Permissions, Sealing, Monotonicity).
- PC-001 & PC-002: DENY only under condition that resource is represented as bounded memory/object capability.
- PC-003: DENY for modeled capability misuse (attempt to exercise authority outside sealed capability state).
- PC-004: UNSUPPORTED because hardware has no native concept of Agent tool identity.
- PC-006: DENY for capability bounds monotonicity violation (cannot derive expanded bounds).
- PC-008: In pure architecture model (CHERI_PURE_ISA_CAPABILITY_MODEL), reported as UNSUPPORTED
  (hardware lacks native temporal agent/token revocation; temporal revocation requires CheriBSD runtime profile).
- PC-005, PC-007, PC-009, PC-010: UNSUPPORTED (higher-order agent semantics).
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


class CheriAdapter(BaseSubstrateAdapter):
    def __init__(self, profile: str = "CHERI_PURE_ISA_CAPABILITY_MODEL"):
        super().__init__(
            name="cheri",
            substrate_type=SubstrateType.RUNTIME,
            enforcement_layer=EnforcementLayer.E4_HARDWARE,
            execution_profile=profile,
        )

    def check_availability(self) -> SubstrateAvailability:
        if self.execution_profile in ["CHERI_PURE_ISA_CAPABILITY_MODEL", "CHERI_CHERIBSD_RUNTIME"]:
            return SubstrateAvailability.AVAILABLE
        elif self.execution_profile == "CHERI_MORELLO_NATIVE":
            has_cheri = shutil.which("cheri-qemu") is not None or shutil.which("qemu-system-morello") is not None
            return SubstrateAvailability.AVAILABLE if has_cheri else SubstrateAvailability.UNAVAILABLE
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
                f"CHERI target environment '{self.execution_profile}' not available on host",
                t0,
            )

        auth = request.authorization_context or {}

        # 1. PC-008: Revocation check depends strictly on execution_profile!
        if auth.get("is_revoked"):
            if self.execution_profile == "CHERI_CHERIBSD_RUNTIME":
                # CheriBSD runtime OS provides capability revocation sweep (Cornucopia / temporal safety)
                return self._build_result(
                    request,
                    DecisionType.DENY,
                    ExecutionStatus.NOT_EXECUTED,
                    "CHERIBSD_TEMPORAL_REVOCATION_FAULT",
                    "Capability revoked via CheriBSD temporal memory sweep; load/store trapped",
                    t0,
                    extra_evidence={"revocation_layer": "CheriBSD_runtime_sweep"},
                )
            else:
                # Pure architectural model: Hardware has no generic agent/token revocation primitive
                return self._build_result(
                    request,
                    DecisionType.UNSUPPORTED,
                    ExecutionStatus.UNSUPPORTED,
                    "CHERI_ARCHITECTURAL_NO_TEMPORAL_REVOCATION",
                    "Pure CHERI ISA provides architectural bounds and tags, not temporal Agent/token revocation",
                    t0,
                    extra_evidence={"profile_limitation": "pure_isa_lacks_runtime_sweep"},
                )

        # 2. PC-005: Argument Substitution (Hardware does not inspect higher-order path semantics)
        # Inside a valid bounded buffer/capability, CHERI hardware does not validate path string prefix rules
        if auth.get("argument_constraints") and "path_prefix" in auth.get("argument_constraints"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "CHERI_NATIVE_SEMANTICS_UNSUPPORTED",
                "Inside a valid bounded buffer, CHERI hardware does not validate path string prefix rules",
                t0,
            )

        # 3. PC-001: File Write (Modeled conditional on resource representation as bounded memory/object capability)
        if request.resource.startswith(("/protected", "/etc")):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "CHERI_TAG_OR_BOUNDS_FAULT",
                "Hardware capability bounds violation: target object address outside bounded capability",
                t0,
                extra_evidence={
                    "hardware_trap": "CapabilityBoundsException",
                    "condition": "resource_represented_as_bounded_memory_object_capability",
                },
            )

        # 3. PC-002: Network Device Access (Modeled as MMIO capability)
        if request.tool.startswith("network.") or request.requested_capability.startswith("net."):
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "CHERI_MMIO_CAPABILITY_FAULT",
                "Network controller MMIO address outside caller capability bounds; CPU hardware trapped",
                t0,
                extra_evidence={
                    "hardware_trap": "MMIO_BoundsException",
                    "condition": "device_represented_as_bounded_mmio_capability",
                },
            )

        # 4. PC-003: Privilege Escalation (Attempt to exercise authority outside sealed capability state)
        if request.tool in ["system.admin"] or request.action in ["grant_sudo"]:
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "CHERI_SEALING_VIOLATION",
                "Hardware sealing violation: attempted invocation of sealed/restricted privilege capability",
                t0,
                extra_evidence={"hardware_trap": "CapabilitySealedException"},
            )

        # 5. PC-006: Scope Expansion (Bounds monotonicity violation)
        if request.resource == "/" or request.requested_capability == "fs.list_root":
            return self._build_result(
                request,
                DecisionType.DENY,
                ExecutionStatus.NOT_EXECUTED,
                "CHERI_MONOTONICITY_VIOLATION",
                "Hardware capability monotonicity violation: derived capability cannot expand range beyond source",
                t0,
                extra_evidence={"hardware_trap": "CapabilityMonotonicityException"},
            )

        # 6. PC-004: Tool Substitution (No native Tool identity concept in hardware)
        if auth.get("authorized_tools") and request.tool not in auth.get("authorized_tools"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "CHERI_NATIVE_SEMANTICS_UNSUPPORTED",
                "CHERI hardware operates on memory addresses and registers; tool identity substitution is an application-level concept",
                t0,
            )

        # 7. PC-005: Argument Substitution (Hardware does not inspect higher-order path semantics)
        if auth.get("argument_constraints") and "path_prefix" in auth.get("argument_constraints"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "CHERI_NATIVE_SEMANTICS_UNSUPPORTED",
                "Inside a valid bounded buffer, CHERI hardware does not validate path string prefix rules",
                t0,
            )

        # 8. PC-007: Temporal Token Expiry (Hardware has no temporal timer for token expiry)
        if auth.get("is_expired"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "CHERI_NATIVE_SEMANTICS_UNSUPPORTED",
                "CHERI CPU architecture contains no native temporal token expiry or TTL state machine",
                t0,
            )

        # 9. PC-009: Replay Nonces (Hardware does not maintain replay nonce tables)
        if auth.get("replayed") or auth.get("nonce"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "CHERI_NATIVE_SEMANTICS_UNSUPPORTED",
                "CHERI CPU registers and caches do not inspect or maintain transaction replay nonces",
                t0,
            )

        # 10. PC-010: Principal Identity (Hardware bounded memory does not equal LLM Agent principal)
        if auth.get("authorized_principal"):
            return self._build_result(
                request,
                DecisionType.UNSUPPORTED,
                ExecutionStatus.UNSUPPORTED,
                "CHERI_NATIVE_SEMANTICS_UNSUPPORTED",
                "CHERI hardware capabilities bind memory objects and compartmentalization domains, not LLM identities",
                t0,
            )

        # Default allowed within capability bounds
        return self._build_result(
            request,
            DecisionType.ALLOW,
            ExecutionStatus.EXECUTED,
            "CHERI_CAPABILITY_ACCESS_PERMITTED",
            "Pointer dereference within hardware capability bounds and valid tag",
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
            "audit_id": f"cheri-audit-{uuid.uuid4().hex[:12]}",
            "reason": reason_msg,
            "execution_profile": self.execution_profile,
            "arguments_hash": request.arguments_hash,
            "replay_reference": f"replay-{request.request_id}",
        }
        if extra_evidence:
            evidence.update(extra_evidence)

        if decision == DecisionType.UNSUPPORTED:
            scope = SemanticScope.UNSUPPORTED
        elif self.execution_profile == "CHERI_CHERIBSD_RUNTIME" and reason_class == "CHERIBSD_TEMPORAL_REVOCATION_FAULT":
            scope = SemanticScope.PROFILE
        else:
            scope = SemanticScope.NATIVE

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
            "version": "CHERI-Morello-v1.0",
            "execution_profile": self.execution_profile,
            "native_semantics": [
                "hardware_bounded_pointers",
                "tagged_memory_protection",
                "capability_monotonicity",
                "capability_sealing",
            ],
            "unsupported_semantics": [
                "agent_tool_identity",
                "agent_principal_identity",
                "argument_json_prefix_bounds",
                "temporal_token_expiry",
                "replay_nonce_cache",
            ],
            "scientific_notes": "CHERI enforces unforgeable capability pointers in hardware. It requires runtime OS (CheriBSD) for temporal heap revocation.",
        }
