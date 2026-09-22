"""MCP ingress adapter for the registered execution-authority path.

This module is intentionally limited to MCP request classification and typed
normalization.  It cannot grant authority, create a process, or replace the
canonical execution PDP.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from vep.cli_execution_boundary import ExecutionRequest
from vep.execution_authority import ExecutionDecision


def sha256_file(path: str) -> str:
    """Return the current content digest for an executable binding check."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


@dataclass(frozen=True)
class McpToolRequest:
    principal: str
    tool_name: str
    arguments: Mapping[str, object]
    target: str
    working_directory: str
    runtime_posture: dict[str, Any]
    policy_context: dict[str, Any]
    issued_at: datetime
    ttl_seconds: int
    provenance: dict[str, Any]
    principal_credential: Mapping[str, object] | None = None


@dataclass(frozen=True)
class SemanticToolSpec:
    tool_name: str
    capability: str
    executable: str
    executable_digest: str
    parameter_types: Mapping[str, type]
    enum_values: Mapping[str, frozenset[str]]
    argv_builder: Callable[[Mapping[str, object]], list[str]]

    def build_argv(self, arguments: Mapping[str, object]) -> list[str] | None:
        if set(arguments) != set(self.parameter_types):
            return None
        for name, expected_type in self.parameter_types.items():
            value = arguments.get(name)
            if not isinstance(value, expected_type):
                return None
            allowed_values = self.enum_values.get(name)
            if allowed_values is not None and value not in allowed_values:
                return None
        argv = self.argv_builder(arguments)
        if not argv or argv[0] != self.executable or not all(
            isinstance(value, str) for value in argv
        ):
            return None
        return argv


class McpExecutionGateway:
    """MCP PEP that delegates all positive authorization to the canonical PDP."""

    _ARBITRARY_EXECUTION_TOOLS = frozenset(
        {"run_shell", "shell_exec", "execute_command", "run_bash"}
    )

    def __init__(
        self,
        authority: Any,
        *,
        semantic_tools: Mapping[str, SemanticToolSpec],
        principal_verifier: Callable[[Mapping[str, object], str], bool] | None = None,
        executable_digest_resolver: Callable[[str], str | None] | None = None,
    ):
        self._authority = authority
        self._semantic_tools = dict(semantic_tools)
        self._principal_verifier = principal_verifier
        self._executable_digest_resolver = executable_digest_resolver

    def authorize(self, request: McpToolRequest) -> ExecutionDecision:
        if request.tool_name in self._ARBITRARY_EXECUTION_TOOLS:
            return self._deny(request, "ARBITRARY_EXECUTION_CAPABILITY_DENIED")

        spec = self._semantic_tools.get(request.tool_name)
        if spec is None:
            return self._deny(request, "UNKNOWN_MCP_TOOL")

        if (
            self._principal_verifier is None
            or request.principal_credential is None
            or not self._principal_verifier(
                request.principal_credential, request.principal
            )
        ):
            return self._deny(request, "PRINCIPAL_CREDENTIAL_INVALID")

        argv = spec.build_argv(request.arguments)
        if argv is None:
            return self._deny(request, "TYPED_ARGUMENT_VALIDATION_FAILED")

        if self._executable_digest_resolver is None:
            return self._deny(request, "EXECUTABLE_INTEGRITY_UNAVAILABLE")
        try:
            actual_digest = self._executable_digest_resolver(spec.executable)
        except OSError:
            return self._deny(request, "EXECUTABLE_INTEGRITY_UNAVAILABLE")
        if actual_digest != spec.executable_digest:
            return self._deny(request, "EXECUTABLE_DIGEST_MISMATCH")

        execution_request = ExecutionRequest(
            principal=request.principal,
            task=request.tool_name,
            capability=spec.capability,
            executable=spec.executable,
            argv=argv,
            target=request.target,
            working_directory=request.working_directory,
            runtime_posture=request.runtime_posture,
            policy_context=request.policy_context,
            issued_at=request.issued_at,
            ttl_seconds=request.ttl_seconds,
            provenance=request.provenance,
        )
        return self._authority.decide(execution_request)

    @staticmethod
    def _deny(request: McpToolRequest, reason: str) -> ExecutionDecision:
        canonical = json.dumps(
            {
                "principal": request.principal,
                "tool_name": request.tool_name,
                "arguments": dict(request.arguments),
                "target": request.target,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        request_id = f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"
        return ExecutionDecision(
            decision="DENY",
            reason=reason,
            policy_id="",
            policy_version="",
            principal=request.principal,
            capability_id="",
            request_id=request_id,
            trace_id=f"sha256:{hashlib.sha256((request_id + ':trace').encode('ascii')).hexdigest()}",
            expires_at=request.issued_at,
            authorization_source="mcp_execution_gateway",
        )
