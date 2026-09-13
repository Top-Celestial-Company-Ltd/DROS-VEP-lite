# -*- coding: utf-8 -*-
"""
M3 Anti-Overclaim Verification Test Suite.
Verifies that VEP's semantic boundaries are rigidly preserved without false-positive claims:
"A substrate capability shall not be classified as Agent-level governance unless the substrate
natively expresses the corresponding Agent-level semantic property."
"""

import pytest
from vep.schema import (
    DecisionType,
    ExecutionStatus,
    SemanticScope,
)
from vep.scenario import load_scenario
from cheri.adapter import CheriAdapter
from sel4.adapter import Sel4Adapter
from wasi.adapter import WasiAdapter
from dros.adapter import DrosAdapter
from tla.adapter import TlaAssuranceAdapter


def test_anti_overclaim_cheri_no_agent_tool_identity():
    """CHERI capability pointer cannot be claimed as Agent Tool Substitution governance."""
    scenario = load_scenario("scenarios/post_compromise/PC-004.yaml")
    req = scenario.get_requests()[0]

    adapter = CheriAdapter(profile="CHERI_PURE_ISA_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    assert res.decision == DecisionType.UNSUPPORTED
    assert res.semantic_scope == SemanticScope.UNSUPPORTED
    assert "CHERI_NATIVE_SEMANTICS_UNSUPPORTED" in res.reason_class


def test_anti_overclaim_sel4_no_agent_token_ttl():
    """seL4 CSpace cannot be claimed as Agent Token TTL/expiry governance."""
    scenario = load_scenario("scenarios/post_compromise/PC-007.yaml")
    req = scenario.get_requests()[0]

    adapter = Sel4Adapter(profile="SEL4_SIM_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    assert res.decision == DecisionType.UNSUPPORTED
    assert res.semantic_scope == SemanticScope.UNSUPPORTED
    assert "SEL4_NATIVE_SEMANTICS_UNSUPPORTED" in res.reason_class


def test_anti_overclaim_cheri_pure_isa_no_temporal_revocation():
    """Pure CHERI ISA hardware cannot claim temporal revocation without OS runtime profile."""
    scenario = load_scenario("scenarios/post_compromise/PC-008.yaml")
    req = scenario.get_requests()[0]

    adapter = CheriAdapter(profile="CHERI_PURE_ISA_CAPABILITY_MODEL")
    res = adapter.evaluate(req)

    assert res.decision == DecisionType.UNSUPPORTED
    assert res.semantic_scope == SemanticScope.UNSUPPORTED
    assert res.reason_class == "CHERI_ARCHITECTURAL_NO_TEMPORAL_REVOCATION"


def test_anti_overclaim_wasi_no_argument_prefix_inspection():
    """WASI preopened descriptor sandbox cannot claim JSON argument path inspection."""
    scenario = load_scenario("scenarios/post_compromise/PC-005.yaml")
    req = scenario.get_requests()[0]

    adapter = WasiAdapter()
    res = adapter.evaluate(req)

    assert res.decision == DecisionType.UNSUPPORTED
    assert res.semantic_scope == SemanticScope.UNSUPPORTED
    assert "WASI_NATIVE_SEMANTICS_UNSUPPORTED" in res.reason_class


def test_anti_overclaim_tla_is_assurance_not_runtime_interceptor():
    """TLA+ model checker cannot be claimed as runtime interceptor."""
    scenario = load_scenario("scenarios/post_compromise/PC-001.yaml")
    req = scenario.get_requests()[0]

    adapter = TlaAssuranceAdapter()
    res = adapter.evaluate(req)

    assert res.decision == DecisionType.UNSUPPORTED
    assert res.execution == ExecutionStatus.NOT_APPLICABLE
    assert res.semantic_scope == SemanticScope.FORMAL
    assert res.enforcement_layer.value == "E5_FORMAL_ASSURANCE"


def test_positive_control_dros_native_agent_governance():
    """DROS natively enforces Agent argument boundaries and revocation."""
    s_arg = load_scenario("scenarios/post_compromise/PC-005.yaml")
    req_arg = s_arg.get_requests()[0]

    adapter = DrosAdapter()
    res_arg = adapter.evaluate(req_arg)

    assert res_arg.decision == DecisionType.DENY
    assert res_arg.execution == ExecutionStatus.NOT_EXECUTED
    assert res_arg.semantic_scope == SemanticScope.NATIVE
    assert res_arg.reason_class in ["ARGUMENT_BOUNDS_VIOLATION", "SCOPE_VIOLATION"]
