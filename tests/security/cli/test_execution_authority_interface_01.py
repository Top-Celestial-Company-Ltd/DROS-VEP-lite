"""EXEC-AUTHORITY-INTERFACE-01 contract tests.

These tests define the authority seam only.  They do not claim canonical Rust
PDP integration or OS process enforcement.
"""

from datetime import UTC, datetime

import pytest
from vep.cli_execution_boundary import ExecutionRequest
from vep.execution_authority import (
    ExecutionAuthority,
    ExecutionAuthorizationPdp,
    PolicyEvaluation,
)


def make_request(**overrides: object) -> ExecutionRequest:
    values: dict[str, object] = {
        "principal": "agent-a",
        "task": "run-report",
        "capability": "cli.execute",
        "executable": "/usr/bin/true",
        "argv": ["/usr/bin/true"],
        "target": "local",
        "working_directory": "/tmp",
        "runtime_posture": {"sandbox": "landlock"},
        "policy_context": {"policy_id": "policy-test"},
        "issued_at": datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        "ttl_seconds": 60,
        "provenance": {"source": "test"},
    }
    values.update(overrides)
    return ExecutionRequest(**values)


class AllowPolicy(ExecutionAuthorizationPdp):
    def evaluate(self, request: ExecutionRequest) -> PolicyEvaluation:
        return PolicyEvaluation(
            decision="ALLOW",
            reason="POLICY_ALLOW",
            policy_id="policy-test",
            policy_version="1",
        )


class UnavailablePolicy(ExecutionAuthorizationPdp):
    def evaluate(self, request: ExecutionRequest) -> PolicyEvaluation:
        raise RuntimeError("PDP unavailable")


class DenyPolicy(ExecutionAuthorizationPdp):
    def __init__(self, reason: str) -> None:
        self._reason = reason

    def evaluate(self, request: ExecutionRequest) -> PolicyEvaluation:
        return PolicyEvaluation(
            decision="DENY",
            reason=self._reason,
            policy_id="policy-test",
            policy_version="1",
        )


def test_allow_returns_complete_execution_decision() -> None:
    authority = ExecutionAuthority(
        AllowPolicy(), now=lambda: datetime(2026, 9, 22, 12, 0, 1, tzinfo=UTC)
    )

    decision = authority.decide(make_request())

    assert decision.decision == "ALLOW"
    assert decision.reason == "POLICY_ALLOW"
    assert decision.policy_id == "policy-test"
    assert decision.policy_version == "1"
    assert decision.principal == "agent-a"
    assert decision.capability_id == "cli.execute"
    assert decision.request_id.startswith("sha256:")
    assert decision.trace_id.startswith("sha256:")
    assert decision.expires_at == datetime(2026, 9, 22, 12, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("principal", "", "MISSING_PRINCIPAL"),
        ("capability", "", "MISSING_CAPABILITY"),
        ("executable", "", "MISSING_EXECUTABLE"),
    ],
)
def test_malformed_authority_request_denies_without_calling_pdp(
    field: str, value: str, reason: str
) -> None:
    authority = ExecutionAuthority(AllowPolicy())

    decision = authority.decide(make_request(**{field: value}))

    assert decision.decision == "DENY"
    assert decision.reason == reason


def test_expired_capability_denies_before_pdp() -> None:
    authority = ExecutionAuthority(
        AllowPolicy(), now=lambda: datetime(2026, 9, 22, 12, 2, tzinfo=UTC)
    )

    decision = authority.decide(make_request())

    assert decision.decision == "DENY"
    assert decision.reason == "CAPABILITY_EXPIRED"


def test_pdp_unavailable_fails_closed() -> None:
    authority = ExecutionAuthority(UnavailablePolicy())

    decision = authority.decide(make_request())

    assert decision.decision == "DENY"
    assert decision.reason == "PDP_UNAVAILABLE"


@pytest.mark.parametrize("reason", ["CAPABILITY_REVOKED", "UNKNOWN_EXECUTABLE"])
def test_policy_denials_are_preserved_by_authority_seam(reason: str) -> None:
    authority = ExecutionAuthority(DenyPolicy(reason))

    decision = authority.decide(make_request())

    assert decision.decision == "DENY"
    assert decision.reason == reason


def test_invalid_ttl_denies_before_pdp() -> None:
    authority = ExecutionAuthority(AllowPolicy())

    decision = authority.decide(make_request(ttl_seconds=0))

    assert decision.decision == "DENY"
    assert decision.reason == "INVALID_TTL"


def test_request_identity_is_stable_for_same_input() -> None:
    authority = ExecutionAuthority(AllowPolicy())

    first = authority.decide(make_request())
    second = authority.decide(make_request())

    assert first.request_id == second.request_id
    assert first.trace_id == second.trace_id
