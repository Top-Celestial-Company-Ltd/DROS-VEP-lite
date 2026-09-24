#!/usr/bin/env python3
"""Snapshot module for S2-D pre-test and post-test system state.

Produces machine-readable, immutable snapshots of PX4 identity, firewall state,
and S2-C baseline grounding.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .models import (
    HostFirewallSnapshot,
    PX4SubjectSnapshot,
    SnapshotPhase,
    SystemSnapshot,
)


def get_git_state(repo_root: Path) -> Dict[str, Any]:
    """Capture current Git commit, branch, and dirty status."""
    try:
        proc_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        head_commit = proc_sha.stdout.strip()

        proc_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        is_dirty = len(proc_status.stdout.strip()) > 0
        return {
            "head_commit": head_commit,
            "is_dirty": is_dirty,
            "status_output": proc_status.stdout.strip()[:200] if is_dirty else "",
        }
    except Exception as exc:
        return {
            "head_commit": "UNKNOWN",
            "is_dirty": True,
            "error": str(exc),
        }


def acquire_px4_identity(pid: Optional[int] = None) -> PX4SubjectSnapshot:
    """Acquire machine-verifiable identity of running PX4 process."""
    if pid is None:
        # Try to find px4 PID if on Linux
        if sys.platform.startswith("linux"):
            try:
                proc = subprocess.run(
                    ["pgrep", "-f", "bin/px4"],
                    capture_output=True,
                    text=True,
                )
                pids = [int(p) for p in proc.stdout.strip().split() if p.isdigit()]
                if pids:
                    pid = pids[0]
            except Exception:
                pid = None

    if pid is None:
        # Offline / Dry-run simulated subject
        return PX4SubjectSnapshot(
            pid=None,
            exe_path=None,
            binary_sha256=None,
            start_time_ticks=None,
            is_running=False,
        )

    # If running on Linux, inspect /proc/<pid>/
    proc_dir = Path(f"/proc/{pid}")
    if not proc_dir.exists():
        return PX4SubjectSnapshot(
            pid=pid,
            exe_path=None,
            binary_sha256=None,
            start_time_ticks=None,
            is_running=False,
        )

    exe_path: Optional[str] = None
    binary_sha256: Optional[str] = None
    start_time_ticks: Optional[int] = None
    inode: Optional[int] = None
    device: Optional[int] = None
    cmdline: Optional[str] = None
    cwd: Optional[str] = None
    size_bytes: Optional[int] = None
    mtime_epoch: Optional[float] = None

    try:
        exe_link = proc_dir / "exe"
        if exe_link.exists():
            resolved = exe_link.resolve()
            exe_path = str(resolved)
            st = resolved.stat()
            inode = st.st_ino
            device = st.st_dev
            size_bytes = st.st_size
            mtime_epoch = st.st_mtime

            # Compute sha256 of the binary
            h = hashlib.sha256()
            with open(resolved, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            binary_sha256 = h.hexdigest()

        cmdline_file = proc_dir / "cmdline"
        if cmdline_file.exists():
            cmdline = cmdline_file.read_bytes().replace(b"\x00", b" ").decode("utf-8", "replace").strip()

        cwd_link = proc_dir / "cwd"
        if cwd_link.exists():
            cwd = str(cwd_link.resolve())

        stat_file = proc_dir / "stat"
        if stat_file.exists():
            # Field 22 is starttime in jiffies
            parts = stat_file.read_text().split()
            if len(parts) >= 22:
                start_time_ticks = int(parts[21])

        return PX4SubjectSnapshot(
            pid=pid,
            exe_path=exe_path,
            binary_sha256=binary_sha256,
            start_time_ticks=start_time_ticks,
            inode=inode,
            device=device,
            cmdline=cmdline,
            cwd=cwd,
            size_bytes=size_bytes,
            mtime_epoch=mtime_epoch,
            is_running=True,
        )
    except Exception as exc:
        return PX4SubjectSnapshot(
            pid=pid,
            exe_path=str(exc),
            binary_sha256=None,
            start_time_ticks=None,
            is_running=True,
        )


def acquire_firewall_state(mode: str = "DRY_RUN") -> HostFirewallSnapshot:
    """Capture snapshot of host packet filtering tables without modifying state."""
    dump = ""
    active_count = 0
    if sys.platform.startswith("linux") and mode != "DRY_RUN":
        try:
            proc = subprocess.run(
                ["iptables-save"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                dump = proc.stdout
                for line in dump.splitlines():
                    if "DROP" in line:
                        active_count += 1
        except Exception as exc:
            dump = f"ERROR: {exc}"
    else:
        # Dry-run or non-Linux host baseline
        dump = "# DRY_RUN_FIREWALL_BASELINE_EMPTY\n*filter\n:INPUT ACCEPT [0:0]\nCOMMIT\n"

    rules_hash = hashlib.sha256(dump.encode("utf-8")).hexdigest()
    return HostFirewallSnapshot(
        rules_hash=rules_hash,
        filter_dump=dump,
        active_drop_rules_count=active_count,
        mode=mode,
    )


def create_system_snapshot(
    repo_root: Path,
    phase: SnapshotPhase,
    pid: Optional[int] = None,
    mode: str = "DRY_RUN",
    s2_c_baseline: Optional[Dict[str, Any]] = None,
) -> SystemSnapshot:
    """Generate an immutable, comprehensive system snapshot."""
    timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    git_state = get_git_state(repo_root)
    px4_identity = acquire_px4_identity(pid)
    firewall_state = acquire_firewall_state(mode)

    baseline = s2_c_baseline or {
        "anchor_file": "reports/evidence/drone/m1_1/s2_v2/s2_c_freeze_anchor.json",
        "endpoint_surface_sha256": "1e78d2b2eef1c4ca25d42e2d703a5f93abbbcd549a9ac7e6148467ac9999cd44",
        "reconciliation_partition": {
            "G": 0, "B": 3, "I": 1, "U": 1, "N": 0
        },
    }

    return SystemSnapshot(
        snapshot_phase=phase,
        timestamp_utc=timestamp_utc,
        git_state=git_state,
        s2_c_baseline=baseline,
        px4_subject_identity=px4_identity,
        host_firewall_state=firewall_state,
    )


def verify_snapshot_invariants(pre: SystemSnapshot, post: SystemSnapshot) -> Tuple[bool, List[str]]:
    """Verify continuity invariants between pre-test and post-test snapshots."""
    failures = []

    # Firewall Cleanliness: Post state must equal Pre state (F_post == F_pre)
    if pre.host_firewall_state.rules_hash != post.host_firewall_state.rules_hash:
        failures.append(
            f"Firewall state mutated across test: pre_hash={pre.host_firewall_state.rules_hash[:12]} "
            f"!= post_hash={post.host_firewall_state.rules_hash[:12]}"
        )

    # PX4 Subject Continuity
    pre_px4 = pre.px4_subject_identity
    post_px4 = post.px4_subject_identity

    if pre_px4.is_running and post_px4.is_running:
        if pre_px4.pid != post_px4.pid:
            failures.append(f"PX4 PID changed: {pre_px4.pid} -> {post_px4.pid} (Process restarted)")
        if pre_px4.start_time_ticks != post_px4.start_time_ticks:
            failures.append("PX4 start_time_ticks changed (Process respawned)")
        if pre_px4.binary_sha256 != post_px4.binary_sha256:
            failures.append("PX4 binary SHA-256 changed (Binary modified)")
        if pre_px4.inode is not None and pre_px4.inode != post_px4.inode:
            failures.append(f"PX4 binary inode changed: {pre_px4.inode} -> {post_px4.inode}")

    return len(failures) == 0, failures
