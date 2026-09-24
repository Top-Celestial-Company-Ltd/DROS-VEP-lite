"""DROS Drone Extension Milestone M1.1-S2-D Package.

Provides reversible host-level perimeter containment testing and verification.
"""
from __future__ import annotations

from .firewall_manager import FirewallManager
from .models import Gate1Result, NormalizedEvidence, OracleEvaluation, SnapshotPhase, SystemSnapshot, Verdict
from .normalizer import EvidenceNormalizer
from .oracles import derive_composite_verdict, evaluate_oracle_a, evaluate_oracle_b, evaluate_oracle_c
from .preflight import PreflightChecker
from .probe_executor import ProbeExecutor
from .snapshot import create_system_snapshot, verify_snapshot_invariants

__all__ = [
    "FirewallManager",
    "Gate1Result",
    "NormalizedEvidence",
    "OracleEvaluation",
    "SnapshotPhase",
    "SystemSnapshot",
    "Verdict",
    "EvidenceNormalizer",
    "derive_composite_verdict",
    "evaluate_oracle_a",
    "evaluate_oracle_b",
    "evaluate_oracle_c",
    "PreflightChecker",
    "ProbeExecutor",
    "create_system_snapshot",
    "verify_snapshot_invariants",
]
