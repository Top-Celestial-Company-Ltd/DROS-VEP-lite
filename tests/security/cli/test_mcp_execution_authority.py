"""MCP execution ingress contract tests.

These tests cover only the registered MCP execution path.  They do not claim
host-wide CLI mediation or kernel-level process enforcement.
"""

from datetime import UTC, datetime
from pathlib import Path

from vep.execution_authority import (
    ExecutionAuthorizationPdp,
    ExecutionAuthority,
    PolicyEvaluation,
)
from vep.mcp_execution_authority import (
    McpExecutionGateway,
    McpToolRequest,
    SemanticToolSpec,
    sha256_file,
)


class AllowAuthority:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, request):
        self.calls += 1
        return type(
            "Decision",
            (),
            {
                "decision": "ALLOW",
                "reason": "POLICY_ALLOW",
                "policy_id": "mcp-test",
                "policy_version": "1",
                "principal": request.principal,
                "capability_id": request.capability,
                "request_id": "sha256:test",
                "trace_id": "sha256:test-trace",
                "expires_at": request.issued_at,
            },
        )()


class AllowPolicy(ExecutionAuthorizationPdp):
    def evaluate(self, request):
        return PolicyEvaluation(
            decision="ALLOW",
            reason="POLICY_ALLOW",
            policy_id="mcp-policy",
            policy_version="1",
        )


def semantic_spec() -> SemanticToolSpec:
    return SemanticToolSpec(
        tool_name="create_invoice",
        capability="invoice.create",
        executable="/usr/local/bin/invoice-worker",
        executable_digest="sha256:approved-worker",
        parameter_types={"customer_id": str, "currency": str},
        enum_values={"currency": frozenset({"TWD", "USD"})},
        argv_builder=lambda args: [
            "/usr/local/bin/invoice-worker",
            "--customer-id",
            args["customer_id"],
            "--currency",
            args["currency"],
        ],
    )


def principal_verifier(credential: dict[str, object], principal: str) -> bool:
    return credential.get("subject") == principal


def executable_digest_resolver(path: str) -> str:
    assert path == "/usr/local/bin/invoice-worker"
    return "sha256:approved-worker"


def request(tool_name: str, arguments: dict[str, object]) -> McpToolRequest:
    return McpToolRequest(
        principal="agent-a",
        tool_name=tool_name,
        arguments=arguments,
        target="billing",
        working_directory="/srv/agent/work",
        runtime_posture={"sandbox": "landlock"},
        policy_context={"policy_id": "mcp-test"},
        issued_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        ttl_seconds=60,
        provenance={"source": "mcp-test"},
        principal_credential={
            "subject": "agent-a",
            "issuer": "test-issuer",
            "audience": "dros-execution",
            "signature": "test-signature",
        },
    )


def test_arbitrary_shell_capability_is_denied_by_default() -> None:
    gateway = McpExecutionGateway(AllowAuthority(), semantic_tools={})

    decision = gateway.authorize(
        request("run_shell", {"command": "echo approved; id"})
    )

    assert decision.decision == "DENY"
    assert decision.reason == "ARBITRARY_EXECUTION_CAPABILITY_DENIED"


def test_semantic_tool_uses_typed_schema_before_authority() -> None:
    gateway = McpExecutionGateway(
        AllowAuthority(),
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=principal_verifier,
        executable_digest_resolver=executable_digest_resolver,
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": "C-001", "currency": "USD"})
    )

    assert decision.decision == "ALLOW"


def test_semantic_tool_rejects_untyped_or_out_of_enum_arguments() -> None:
    gateway = McpExecutionGateway(
        AllowAuthority(),
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=principal_verifier,
        executable_digest_resolver=executable_digest_resolver,
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": 1001, "currency": "HACK"})
    )

    assert decision.decision == "DENY"
    assert decision.reason == "TYPED_ARGUMENT_VALIDATION_FAILED"


def test_semantic_tool_requires_verified_principal_credential() -> None:
    authority = AllowAuthority()
    gateway = McpExecutionGateway(
        authority,
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=lambda credential, principal: (
            credential.get("subject") == principal
            and credential.get("issuer") == "test-issuer"
        ),
        executable_digest_resolver=executable_digest_resolver,
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": "C-001", "currency": "USD"})
    )

    assert decision.decision == "ALLOW"
    assert authority.calls == 1


def test_forged_principal_credential_is_denied_before_authority() -> None:
    authority = AllowAuthority()
    gateway = McpExecutionGateway(
        authority,
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=lambda credential, principal: False,
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": "C-001", "currency": "USD"})
    )

    assert decision.decision == "DENY"
    assert decision.reason == "PRINCIPAL_CREDENTIAL_INVALID"
    assert authority.calls == 0


def test_executable_digest_mismatch_denies_before_authority() -> None:
    authority = AllowAuthority()
    gateway = McpExecutionGateway(
        authority,
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=principal_verifier,
        executable_digest_resolver=lambda path: "sha256:tampered-worker",
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": "C-001", "currency": "USD"})
    )

    assert decision.decision == "DENY"
    assert decision.reason == "EXECUTABLE_DIGEST_MISMATCH"
    assert authority.calls == 0


def test_file_content_mutation_is_detected_before_authority(tmp_path: Path) -> None:
    worker = tmp_path / "invoice-worker"
    worker.write_bytes(b"approved-worker")
    approved_digest = sha256_file(str(worker))
    spec = SemanticToolSpec(
        tool_name="run_worker",
        capability="worker.run",
        executable=str(worker),
        executable_digest=approved_digest,
        parameter_types={"job_id": str},
        enum_values={},
        argv_builder=lambda args: [str(worker), args["job_id"]],
    )
    authority = AllowAuthority()
    gateway = McpExecutionGateway(
        authority,
        semantic_tools={"run_worker": spec},
        principal_verifier=principal_verifier,
        executable_digest_resolver=sha256_file,
    )
    worker_request = McpToolRequest(
        principal="agent-a",
        tool_name="run_worker",
        arguments={"job_id": "J-001"},
        target="worker",
        working_directory=str(tmp_path),
        runtime_posture={"sandbox": "landlock"},
        policy_context={"policy_id": "mcp-test"},
        issued_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        ttl_seconds=60,
        provenance={"source": "mcp-test"},
        principal_credential={"subject": "agent-a"},
    )

    worker.write_bytes(b"tampered-worker")
    decision = gateway.authorize(worker_request)

    assert decision.decision == "DENY"
    assert decision.reason == "EXECUTABLE_DIGEST_MISMATCH"
    assert authority.calls == 0


def test_semantic_mcp_request_reaches_canonical_execution_authority() -> None:
    authority = ExecutionAuthority(
        AllowPolicy(), now=lambda: datetime(2026, 9, 22, 12, 0, 1, tzinfo=UTC)
    )
    gateway = McpExecutionGateway(
        authority,
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=principal_verifier,
        executable_digest_resolver=executable_digest_resolver,
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": "C-001", "currency": "USD"})
    )

    assert decision.decision == "ALLOW"
    assert decision.authorization_source == "execution_authorization_pdp"
    assert decision.policy_id == "mcp-policy"


def test_expired_semantic_mcp_request_fails_closed_in_canonical_authority() -> None:
    authority = ExecutionAuthority(
        AllowPolicy(), now=lambda: datetime(2026, 9, 22, 12, 2, tzinfo=UTC)
    )
    gateway = McpExecutionGateway(
        authority,
        semantic_tools={"create_invoice": semantic_spec()},
        principal_verifier=principal_verifier,
        executable_digest_resolver=executable_digest_resolver,
    )

    decision = gateway.authorize(
        request("create_invoice", {"customer_id": "C-001", "currency": "USD"})
    )

    assert decision.decision == "DENY"
    assert decision.reason == "CAPABILITY_EXPIRED"
