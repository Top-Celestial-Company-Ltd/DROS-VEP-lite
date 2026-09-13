# -*- coding: utf-8 -*-
"""
M2 Verification: seL4 & CHERI Capability Substrate Calibration Tests.
Verifies the 4 critical calibration points:
1. seL4 PC-008: models capability derivation revocation (seL4_CNode_Revoke), NOT generic Agent authorization token revocation.
2. CHERI PC-008: in pure architecture model (CHERI_PURE_ISA_CAPABILITY_MODEL), reported as UNSUPPORTED.
3. CHERI PC-004: reported as UNSUPPORTED (hardware has no native concept of Agent tool identity).
4. CHERI PC-006: models hardware capability bounds monotonicity violation -> DENY.
"""

import pytest
from vep.schema import (
    CanonicalExecutionRequest,
    DecisionType,
    ExecutionStatus,
    SubstrateAvailability,
)
from vep.scenario import load_scenario
from sel4.adapter import Sel4Adapter
from cheri.adapter import CheriAdapter


def test_calibration_1_sel4_pc008_capability_derivation_revocation():
    scenario = load_scenario("scenarios/post_compromise/PC-008.yaml")
    req = scenario.get_requests()[0]

    adapter = Sel4Adapter(profile="SEL4_SIM_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    # seL4 denies via capability derivation revocation, not abstract agent token revocation
    assert res.decision == DecisionType.DENY
    assert res.execution == ExecutionStatus.NOT_EXECUTED
    assert res.reason_class == "SEL4_CAPABILITY_DERIVATION_REVOKED"
    assert res.evidence["mechanism"] == "seL4_CNode_Revoke"
    assert res.evidence["semantics"] == "capability_derivation_revocation_not_agent_token"


def test_calibration_2_cheri_pc008_pure_isa_no_temporal_revocation():
    scenario = load_scenario("scenarios/post_compromise/PC-008.yaml")
    req = scenario.get_requests()[0]

    # Pure architectural profile
    adapter_pure = CheriAdapter(profile="CHERI_PURE_ISA_CAPABILITY_MODEL")
    res_pure = adapter_pure.evaluate(req)

    # Pure hardware lacks temporal agent revocation -> MUST BE UNSUPPORTED
    assert res_pure.decision == DecisionType.UNSUPPORTED
    assert res_pure.execution == ExecutionStatus.UNSUPPORTED
    assert res_pure.reason_class == "CHERI_ARCHITECTURAL_NO_TEMPORAL_REVOCATION"

    # CheriBSD runtime profile provides temporal sweep
    adapter_runtime = CheriAdapter(profile="CHERI_CHERIBSD_RUNTIME")
    res_runtime = adapter_runtime.evaluate(req)
    assert res_runtime.decision == DecisionType.DENY
    assert res_runtime.reason_class == "CHERIBSD_TEMPORAL_REVOCATION_FAULT"


def test_calibration_3_cheri_pc004_no_native_tool_identity():
    scenario = load_scenario("scenarios/post_compromise/PC-004.yaml")
    req = scenario.get_requests()[0]

    adapter = CheriAdapter(profile="CHERI_PURE_ISA_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    # CHERI hardware operates on memory addresses/registers, has no native tool identity concept
    assert res.decision == DecisionType.UNSUPPORTED
    assert res.execution == ExecutionStatus.UNSUPPORTED
    assert res.reason_class == "CHERI_NATIVE_SEMANTICS_UNSUPPORTED"


def test_calibration_4_cheri_pc006_bounds_monotonicity():
    scenario = load_scenario("scenarios/post_compromise/PC-006.yaml")
    req = scenario.get_requests()[0]

    adapter = CheriAdapter(profile="CHERI_PURE_ISA_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    # CHERI hardware traps bounds monotonicity violation
    assert res.decision == DecisionType.DENY
    assert res.execution == ExecutionStatus.NOT_EXECUTED
    assert res.reason_class == "CHERI_MONOTONICITY_VIOLATION"
    assert res.evidence["hardware_trap"] == "CapabilityMonotonicityException"


def test_sel4_pc006_rights_cannot_escalate():
    scenario = load_scenario("scenarios/post_compromise/PC-006.yaml")
    req = scenario.get_requests()[0]

    adapter = Sel4Adapter(profile="SEL4_SIM_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    assert res.decision == DecisionType.DENY
    assert res.reason_class == "SEL4_CAPABILITY_RIGHTS_CANNOT_ESCALATE"
