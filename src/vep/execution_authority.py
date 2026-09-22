"""Canonical execution-authority seam.

This module defines the authority contract only.  It does not implement a CLI
policy engine, process creation, Landlock, or GuardVM context compilation.
Concrete policy adapters (including the canonical Rust DCT adapter) satisfy
``ExecutionAuthorizationPdp`` at this seam.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from vep.cli_execution_boundary import ExecutionRequest


@dataclass(frozen=True)
class PolicyEvaluation:
    """The only policy result an authority adapter may provide."""

    decision: str
    reason: str
    policy_id: str
    policy_version: str


class ExecutionAuthorizationPdp(ABC):
    """Authority adapter interface; it must never create a process."""

    @abstractmethod
    def evaluate(self, request: ExecutionRequest) -> PolicyEvaluation:
        """Return a deterministic policy result for one execution request."""


@dataclass(frozen=True)
class ExecutionDecision:
    decision: str
    reason: str
    policy_id: str
    policy_version: str
    principal: str
    capability_id: str
    request_id: str
    trace_id: str
    expires_at: datetime
    authorization_source: str = "execution_authorization_pdp"
    execution: str = "NOT_EXECUTED"


def _request_identity(request: ExecutionRequest) -> str:
    payload = {
        "principal": request.principal,
        "task": request.task,
        "capability": request.capability,
        "executable": request.executable,
        "argv_hash": request.argv_hash,
        "target": request.target,
        "working_directory": request.working_directory,
        "runtime_posture": request.runtime_posture,
        "policy_context": request.policy_context,
        "issued_at": request.issued_at.isoformat(),
        "ttl_seconds": request.ttl_seconds,
        "provenance": request.provenance,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _trace_id(request_id: str) -> str:
    return f"sha256:{hashlib.sha256((request_id + ":trace").encode('ascii')).hexdigest()}"


class ExecutionAuthority:
    """Small fail-closed authority module behind the execution seam."""

    def __init__(
        self,
        pdp: ExecutionAuthorizationPdp,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._pdp = pdp
        self._now = now or (lambda: datetime.now(UTC))

    def decide(self, request: ExecutionRequest) -> ExecutionDecision:
        request_id = _request_identity(request)
        trace_id = _trace_id(request_id)
        expires_at = request.issued_at + timedelta(seconds=request.ttl_seconds)
        base = {
            "policy_id": "",
            "policy_version": "",
            "principal": request.principal,
            "capability_id": request.capability,
            "request_id": request_id,
            "trace_id": trace_id,
            "expires_at": expires_at,
        }

        reason = self._validate(request)
        if reason is not None:
            return ExecutionDecision(decision="DENY", reason=reason, **base)

        try:
            evaluation = self._pdp.evaluate(request)
        except Exception:  # noqa: BLE001 - PDP failure must fail closed.
            return ExecutionDecision(decision="DENY", reason="PDP_UNAVAILABLE", **base)

        if evaluation.decision not in {"ALLOW", "DENY"}:
            return ExecutionDecision(decision="DENY", reason="INVALID_PDP_DECISION", **base)

        return ExecutionDecision(
            decision=evaluation.decision,
            reason=evaluation.reason,
            policy_id=evaluation.policy_id,
            policy_version=evaluation.policy_version,
            **{
                key: value
                for key, value in base.items()
                if key not in {"policy_id", "policy_version"}
            },
        )

    def _validate(self, request: ExecutionRequest) -> str | None:
        if not request.principal:
            return "MISSING_PRINCIPAL"
        if not request.capability:
            return "MISSING_CAPABILITY"
        if not request.executable:
            return "MISSING_EXECUTABLE"
        if request.ttl_seconds <= 0:
            return "INVALID_TTL"
        if request.issued_at.tzinfo is None:
            return "INVALID_ISSUED_AT"
        if self._now() >= request.issued_at + timedelta(seconds=request.ttl_seconds):
            return "CAPABILITY_EXPIRED"
        return None
