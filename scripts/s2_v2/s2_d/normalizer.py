#!/usr/bin/env python3
"""Raw evidence normalizer for Milestone M1.1-S2-D.

Separates raw evidentiary artifact storage from deterministic evaluation.
Raw Evidence -> Normalizer -> Oracle -> Verdict.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import NormalizedEvidence


class EvidenceNormalizer:
    """Transforms raw on-disk or in-memory evidence records into structured metrics."""

    @staticmethod
    def normalize(
        firewall_counters: Dict[str, Any],
        px4_state_before: Dict[str, Any],
        px4_state_after: Dict[str, Any],
        pep_control_path: Dict[str, Any],
        process_continuity: Dict[str, Any],
        raw_evidence_paths: Optional[List[str]] = None,
    ) -> NormalizedEvidence:
        """Normalize raw observation datasets into structured metrics."""
        # 1. Network Enforcement (Oracle A)
        network_enforcement: Dict[str, Any] = {
            "per_port_drops": {},
            "all_target_ports_hit": False,
            "total_drops": 0,
        }
        counters = firewall_counters.get("counters", {})
        total_drops = 0
        hit_count = 0
        for port_str, count in counters.items():
            cnt = int(count)
            network_enforcement["per_port_drops"][port_str] = cnt
            total_drops += cnt
            if cnt > 0:
                hit_count += 1

        network_enforcement["total_drops"] = total_drops
        network_enforcement["all_target_ports_hit"] = (hit_count == len(counters) and len(counters) > 0)
        network_enforcement["raw_counters"] = counters

        # 2. Target State Integrity (Oracle B)
        state_integrity: Dict[str, Any] = {
            "parameters": {},
            "any_parameter_mutated": False,
        }
        params_before = px4_state_before.get("parameters", {})
        params_after = px4_state_after.get("parameters", {})

        any_mutated = False
        for param_id, pre_val in params_before.items():
            post_val = params_after.get(param_id, pre_val)
            delta = abs(float(post_val) - float(pre_val))
            mutated = delta > 1e-4
            if mutated:
                any_mutated = True
            state_integrity["parameters"][param_id] = {
                "pre_val": pre_val,
                "post_val": post_val,
                "delta": delta,
                "mutated": mutated,
            }

        state_integrity["any_parameter_mutated"] = any_mutated

        # 3. Control Path Preservation (Oracle C)
        control_path: Dict[str, Any] = {
            "authorized_request_admitted": pep_control_path.get("authorized_admitted", False),
            "unauthorized_request_blocked": pep_control_path.get("unauthorized_blocked", False),
            "pep_operational": pep_control_path.get("pep_operational", False),
            "px4_pid_unchanged": process_continuity.get("pid_unchanged", False),
            "px4_binary_unchanged": process_continuity.get("binary_unchanged", False),
            "px4_restarted": process_continuity.get("restarted", False),
        }

        return NormalizedEvidence(
            network_enforcement=network_enforcement,
            state_integrity=state_integrity,
            control_path_preservation=control_path,
            raw_evidence_paths=raw_evidence_paths or [],
        )

    @classmethod
    def from_files(
        cls,
        firewall_path: Path,
        state_before_path: Path,
        state_after_path: Path,
        pep_path: Path,
        process_path: Path,
    ) -> NormalizedEvidence:
        """Load from raw on-disk files and normalize."""
        with open(firewall_path, "r", encoding="utf-8") as f:
            fc = json.load(f)
        with open(state_before_path, "r", encoding="utf-8") as f:
            sb = json.load(f)
        with open(state_after_path, "r", encoding="utf-8") as f:
            sa = json.load(f)
        with open(pep_path, "r", encoding="utf-8") as f:
            pep = json.load(f)
        with open(process_path, "r", encoding="utf-8") as f:
            proc = json.load(f)

        raw_paths = [
            str(firewall_path),
            str(state_before_path),
            str(state_after_path),
            str(pep_path),
            str(process_path),
        ]
        return cls.normalize(fc, sb, sa, pep, proc, raw_paths)
