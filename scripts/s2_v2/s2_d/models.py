#!/usr/bin/env python3
"""Data models and schemas for Milestone M1.1-S2-D.

Enforces strict schemas for snapshots, evidence, oracles, and Gate 1 verification.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"
    ABORTED = "ABORTED"


class FirewallMode(str, Enum):
    DRY_RUN = "DRY_RUN"
    LIVE = "LIVE"


class SnapshotPhase(str, Enum):
    PRE_TEST = "PRE_TEST"
    POST_TEST = "POST_TEST"


@dataclass
class PX4SubjectSnapshot:
    pid: Optional[int]
    exe_path: Optional[str]
    binary_sha256: Optional[str]
    start_time_ticks: Optional[int]
    inode: Optional[int] = None
    device: Optional[int] = None
    cmdline: Optional[str] = None
    cwd: Optional[str] = None
    size_bytes: Optional[int] = None
    mtime_epoch: Optional[float] = None
    is_running: bool = False


@dataclass
class HostFirewallSnapshot:
    rules_hash: str  # Kept for backward compatibility (maps to semantic_rules_hash)
    filter_dump: str
    active_drop_rules_count: int = 0
    mode: str = "DRY_RUN"
    raw_rules_hash: str = ""
    semantic_rules_hash: str = ""
    canonical_dump: str = ""


@dataclass
class SystemSnapshot:
    snapshot_phase: SnapshotPhase
    timestamp_utc: str
    git_state: Dict[str, Any]
    s2_c_baseline: Dict[str, Any]
    px4_subject_identity: PX4SubjectSnapshot
    host_firewall_state: HostFirewallSnapshot

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["snapshot_phase"] = self.snapshot_phase.value
        return data


@dataclass
class NormalizedEvidence:
    """Normalized evidence collected during Phase 3 verification."""
    network_enforcement: Dict[str, Any] = field(default_factory=dict)
    state_integrity: Dict[str, Any] = field(default_factory=dict)
    control_path_preservation: Dict[str, Any] = field(default_factory=dict)
    raw_evidence_paths: List[str] = field(default_factory=list)


@dataclass
class OracleEvaluation:
    oracle_name: str
    verdict: Verdict
    rationale: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Gate1Result:
    """Fixed schema for Gate 1 non-invasiveness verification."""
    gate: str = "S2-D-GATE-1"
    purpose: str = "runner_non_invasiveness_validation"
    claim_status: str = "NO_S2_D_CLAIM"
    live_containment_executed: bool = False
    live_execution_authorized: bool = False
    px4_modified: bool = False
    px4_restarted: bool = False
    firewall_modified: bool = False
    verdict: Verdict = Verdict.PASS
    checklist: Dict[str, str] = field(default_factory=dict)
    timestamp_utc: str = ""
    runner_commit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["verdict"] = self.verdict.value
        return data
