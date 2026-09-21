# -*- coding: utf-8 -*-
import pytest
from vep.schema import (
    CanonicalExecutionRequest,
    CanonicalExecutionResult,
    SubstrateType,
    SubstrateAvailability,
    DecisionType,
    ExecutionStatus,
    AssuranceStatus,
    EnforcementLayer,
)
from vep.scenario import load_scenario
from dros.adapter import DrosAdapter
from wasi.adapter import WasiAdapter
from tla.adapter import TlaAssuranceAdapter


def test_schema_argument_hash_auto_generation():
    req1 = CanonicalExecutionRequest(
        request_id="R-1",
        principal="agent-a",
        task="t1",
        tool="tool1",
        action="act",
        resource="res",
        arguments={"b": 2, "a": 1},
        requested_capability="cap",
        authorization_context={},
        timestamp="2026-01-01T00:00:00Z",
    )
    req2 = CanonicalExecutionRequest(
        request_id="R-2",
        principal="agent-a",
        task="t1",
        tool="tool1",
        action="act",
        resource="res",
        arguments={"a": 1, "b": 2},
        requested_capability="cap",
        authorization_context={},
        timestamp="2026-01-01T00:00:00Z",
    )
    # Ensure key sorting in canonical json eliminates hash drift
    assert req1.arguments_hash == req2.arguments_hash
    assert req1.arguments_hash.startswith("sha256:")


def test_golden_acceptance_pc008_three_distinct_outcomes():
    scenario = load_scenario("scenarios/post_compromise/PC-008.yaml")
    req = scenario.get_requests()[0]

    dros = DrosAdapter()
    wasi = WasiAdapter()
    tla = TlaAssuranceAdapter()

    res_dros = dros.evaluate(req)
    res_wasi = wasi.evaluate(req)
    res_tla = tla.evaluate(req)

    # 1. DROS: Runtime Enforcement
    assert res_dros.decision == DecisionType.DENY
    assert res_dros.execution == ExecutionStatus.NOT_EXECUTED
    assert res_dros.reason_class == "AUTHORIZATION_REVOKED"

    # 2. WASI: Runtime Capability Limitation (Unsupported agent-level semantics)
    assert res_wasi.decision == DecisionType.UNSUPPORTED
    assert res_wasi.execution == ExecutionStatus.UNSUPPORTED
    assert res_wasi.reason_class == "WASI_NATIVE_SEMANTICS_UNSUPPORTED"

    # 3. TLA+: Formal Assurance (No runtime execution interceptor)
    assert res_tla.decision == DecisionType.UNSUPPORTED
    assert res_tla.execution == ExecutionStatus.NOT_APPLICABLE
    assert res_tla.assurance_status == AssuranceStatus.PASS
    assert res_tla.reason_class == "FORMAL_INVARIANT_PRESERVED"


def test_opa_and_scopegate_pc008_revocation_enforcement():
    from opa.adapter import OpaAdapter
    from scopegate.adapter import ScopeGateAdapter

    scenario = load_scenario("scenarios/post_compromise/PC-008.yaml")
    req = scenario.get_requests()[0]

    opa = OpaAdapter()
    scopegate = ScopeGateAdapter()

    res_opa = opa.evaluate(req)
    res_sg = scopegate.evaluate(req)

    # OPA is a host-dependent policy engine. On Linux agents without a native
    # opa binary, the adapter must degrade to UNSUPPORTED instead of raising.
    if res_opa.decision == DecisionType.UNSUPPORTED:
        assert res_opa.execution == ExecutionStatus.UNSUPPORTED
        assert res_opa.reason_class == "OPA_BINARY_OR_POLICY_UNAVAILABLE"
    else:
        assert res_opa.decision == DecisionType.DENY
        assert res_opa.execution == ExecutionStatus.NOT_EXECUTED
        assert res_opa.reason_class == "AUTHORIZATION_REVOKED"

    assert res_sg.decision == DecisionType.DENY
    assert res_sg.execution == ExecutionStatus.NOT_EXECUTED
    assert res_sg.reason_class == "SG_STAGE4_REVOCATION_BLOCKED"

