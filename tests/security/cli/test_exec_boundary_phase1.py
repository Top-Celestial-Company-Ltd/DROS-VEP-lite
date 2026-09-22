# -*- coding: utf-8 -*-
"""Phase 1 red tests for the Linux CLI/process execution boundary.

These tests define the public seam only.  The implementation is intentionally
absent at this stage; a failing collection is expected until the CLI PEP is
implemented against the existing PDP/GuardVM semantics.
"""

from datetime import datetime, timezone

import pytest

from vep.cli_execution_boundary import CliExecutionPep, ExecutionRequest


def _request(**overrides):
    values = {
        "principal": "agent-a",
        "task": "task-cli-001",
        "capability": "process.execute.safe",
        "executable": "/usr/bin/printf",
        "argv": ["printf", "ok"],
        "target": "stdout",
        "working_directory": "/srv/agent/work",
        "runtime_posture": {"platform": "linux", "namespace": "agent-a"},
        "policy_context": {"policy_version": "phase1-fixture"},
        "issued_at": datetime.now(timezone.utc),
        "ttl_seconds": 30,
        "provenance": {"agent_id": "agent-a", "session_id": "session-001"},
    }
    values.update(overrides)
    return ExecutionRequest(**values)


def test_execve_allow_is_decided_before_process_creation():
    """An allowed request must be approved by the existing PDP seam first."""
    pep = CliExecutionPep.for_test_policy(
        allowed_executables={"/usr/bin/printf"},
        allowed_capabilities={"process.execute.safe"},
    )

    result = pep.evaluate(_request())

    assert result.decision == "ALLOW"
    assert result.syscall in {"execve", "execveat"}
    assert result.execution == "NOT_EXECUTED"
    assert result.authorization_source == "existing_pdp_guardvm"


def test_execve_denial_does_not_create_a_process():
    """An executable outside the authorized scope must fail closed."""
    pep = CliExecutionPep.for_test_policy(
        allowed_executables={"/usr/bin/printf"},
        allowed_capabilities={"process.execute.safe"},
    )

    result = pep.evaluate(_request(executable="/bin/sh", argv=["sh", "-c", "id"]))

    assert result.decision == "DENY"
    assert result.execution == "NOT_EXECUTED"
    assert result.reason_code == "EXECUTABLE_OUT_OF_SCOPE"


@pytest.mark.parametrize("syscall", ["execve", "execveat"])
def test_execve_variants_produce_the_same_normalized_request(syscall):
    """Both Linux process-replacement variants must bind the same authority."""
    pep = CliExecutionPep.for_test_policy(
        allowed_executables={"/usr/bin/printf"},
        allowed_capabilities={"process.execute.safe"},
    )

    result = pep.evaluate(_request(), syscall=syscall)

    assert result.decision == "ALLOW"
    assert result.argv_hash.startswith("sha256:")
    assert result.executable == "/usr/bin/printf"
    assert result.capability == "process.execute.safe"


def test_argument_mutation_changes_authorization_binding():
    """The command name alone must not authorize a malicious argv payload."""
    pep = CliExecutionPep.for_test_policy(
        allowed_executables={"/usr/bin/python3"},
        allowed_capabilities={"process.execute.safe"},
        allowed_argv_hashes={"sha256:fixture-safe-argv"},
    )

    result = pep.evaluate(
        _request(
            executable="/usr/bin/python3",
            argv=["python3", "-c", "import os; os.system('id')"],
        )
    )

    assert result.decision == "DENY"
    assert result.reason_code == "ARGUMENT_BINDING_VIOLATION"
