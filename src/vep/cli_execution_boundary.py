# -*- coding: utf-8 -*-
"""Deterministic CLI execution-boundary request seam.

This module intentionally stops before the real OS process-creation hook.  It
normalizes a CLI request and delegates the authorization decision to the
existing PDP/GuardVM seam represented by the phase-one fixture policy.  It is
not a shell wrapper and it does not claim kernel-level enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from typing import Any, Iterable


def _argv_hash(argv: Iterable[str]) -> str:
    canonical = json.dumps(list(argv), ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True)
class ExecutionRequest:
    principal: str
    task: str
    capability: str
    executable: str
    argv: list[str]
    target: str
    working_directory: str
    runtime_posture: dict[str, Any]
    policy_context: dict[str, Any]
    issued_at: datetime
    ttl_seconds: int
    provenance: dict[str, Any]

    @property
    def argv_hash(self) -> str:
        return _argv_hash(self.argv)


@dataclass(frozen=True)
class ExecutionDecision:
    decision: str
    syscall: str
    execution: str
    authorization_source: str
    reason_code: str
    argv_hash: str
    executable: str
    capability: str


class CliExecutionPep:
    """Phase-one adapter seam; actual OS process creation is out of scope."""

    def __init__(
        self,
        *,
        allowed_executables: set[str],
        allowed_capabilities: set[str],
        allowed_argv_hashes: set[str] | None = None,
    ) -> None:
        self._allowed_executables = frozenset(allowed_executables)
        self._allowed_capabilities = frozenset(allowed_capabilities)
        self._allowed_argv_hashes = (
            frozenset(allowed_argv_hashes) if allowed_argv_hashes is not None else None
        )

    @classmethod
    def for_test_policy(
        cls,
        *,
        allowed_executables: set[str],
        allowed_capabilities: set[str],
        allowed_argv_hashes: set[str] | None = None,
    ) -> "CliExecutionPep":
        return cls(
            allowed_executables=allowed_executables,
            allowed_capabilities=allowed_capabilities,
            allowed_argv_hashes=allowed_argv_hashes,
        )

    def evaluate(
        self,
        request: ExecutionRequest,
        *,
        syscall: str = "execve",
    ) -> ExecutionDecision:
        if syscall not in {"execve", "execveat"}:
            raise ValueError(f"unsupported process boundary: {syscall}")

        reason_code = None
        if request.executable not in self._allowed_executables:
            reason_code = "EXECUTABLE_OUT_OF_SCOPE"
        elif request.capability not in self._allowed_capabilities:
            reason_code = "CAPABILITY_NOT_AUTHORIZED"
        elif (
            self._allowed_argv_hashes is not None
            and request.argv_hash not in self._allowed_argv_hashes
        ):
            reason_code = "ARGUMENT_BINDING_VIOLATION"

        if reason_code is not None:
            return ExecutionDecision(
                decision="DENY",
                syscall=syscall,
                execution="NOT_EXECUTED",
                authorization_source="existing_pdp_guardvm",
                reason_code=reason_code,
                argv_hash=request.argv_hash,
                executable=request.executable,
                capability=request.capability,
            )

        return ExecutionDecision(
            decision="ALLOW",
            syscall=syscall,
            execution="NOT_EXECUTED",
            authorization_source="existing_pdp_guardvm",
            reason_code="AUTHORIZED_PENDING_OS_EXECUTION",
            argv_hash=request.argv_hash,
            executable=request.executable,
            capability=request.capability,
        )
