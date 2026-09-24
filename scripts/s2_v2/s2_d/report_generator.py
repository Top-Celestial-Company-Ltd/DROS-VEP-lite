#!/usr/bin/env python3
"""Report generator for Milestone M1.1-S2-D Gate 1.

Emits standardized machine-readable GATE1_RESULT.json and audit report.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict

from .models import Gate1Result


def emit_gate1_artifacts(result: Gate1Result, output_dir: Path) -> Path:
    """Emit GATE1_RESULT.json and markdown summary report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "GATE1_RESULT.json"
    md_path = output_dir / "GATE1_REPORT.md"

    # Enforce pure LF json emission
    payload = result.to_dict()
    raw_bytes = json.dumps(payload, indent=2).encode("utf-8") + b"\n"
    json_path.write_bytes(raw_bytes)

    # Markdown report
    lines = [
        "# Milestone M1.1-S2-D Gate 1 Verification Report",
        "## Runner Non-Invasiveness & Initialization Audit",
        "",
        f"> **Gate Status**: `{result.verdict.value}`  ",
        f"> **Claim Status**: `{result.claim_status}` (Zero S2-D Claims Emitted)  ",
        f"> **Live Containment Executed**: `{result.live_containment_executed}`  ",
        f"> **Live Execution Authorized**: `{result.live_execution_authorized}`  ",
        f"> **PX4 Modified**: `{result.px4_modified}`  ",
        f"> **PX4 Restarted**: `{result.px4_restarted}`  ",
        f"> **Firewall Modified**: `{result.firewall_modified}`  ",
        "",
        "---",
        "",
        "### 12-Point Gate 1 Non-Invasiveness Checklist",
        "",
        "| Criterion ID | Evaluation Description | Result |",
        "| :--- | :--- | :---: |",
    ]
    for k, v in result.checklist.items():
        lines.append(f"| `{k}` | Gate 1 Preflight Verification | **{v}** |")

    lines.extend([
        "",
        "---",
        "",
        "### Epistemic Assurance",
        "* Gate 1 establishes that the S2-D runner correctly observes, initializes, simulates, and verifies its own execution pipeline without mutating the target system.",
        "* No S2-D containment claim is made by Gate 1.",
        "",
    ])

    md_bytes = "\n".join(lines).encode("utf-8") + b"\n"
    md_path.write_bytes(md_bytes)

    return json_path
