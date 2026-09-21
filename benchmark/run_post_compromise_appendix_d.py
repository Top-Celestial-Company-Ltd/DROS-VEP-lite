
# -*- coding: utf-8 -*-
"""Appendix D local runner for the post-compromise / lower-layer bypass benchmark.

This wrapper keeps the execution path simple:
  1. Runs the canonical post-compromise benchmark via vep.py.
  2. Captures the latest experiment pointer.
  3. Writes a compact manifest so the resulting artifact can be referenced from
     the whitepaper Appendix D evidence index.

The script is intentionally substrate-agnostic. On a Linux host with seccomp,
Landlock, or container support available adapters, the same wrapper can be reused
without code changes.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports" / "benchmarks" / "post_compromise"
LATEST_PTR = REPORTS_DIR / "latest.json"


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def read_latest_experiment() -> dict[str, str]:
    if not LATEST_PTR.exists():
        return {}
    try:
        return json.loads(LATEST_PTR.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Appendix D local post-compromise benchmark wrapper")
    parser.add_argument(
        "--substrate",
        default="dros,dros-kernel,opa,scopegate,wasi,tla,sel4,cheri",
        help="Comma-separated substrate list passed to vep.py benchmark post-compromise",
    )
    parser.add_argument(
        "--scenario",
        default=None,
        help="Optional single scenario ID (e.g. PC-001). If omitted, all scenarios run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the command and exit without executing it.",
    )
    args = parser.parse_args()

    vep_cli = BASE_DIR / "vep.py"
    cmd = [sys.executable, str(vep_cli), "benchmark", "post-compromise"]
    if args.scenario:
        cmd += ["--scenario", args.scenario]
    if args.substrate:
        cmd += ["--substrate", args.substrate]

    print("=" * 80)
    print("Appendix D local runner")
    print("=" * 80)
    print("Command:")
    print(" ".join(cmd))
    print("=" * 80)

    if args.dry_run:
        return 0

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    proc = run_cmd(cmd, BASE_DIR)
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Stream output to the terminal for immediate review.
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    latest = read_latest_experiment()
    manifest = {
        "started_at": started,
        "finished_at": finished,
        "hostname": platform.node(),
        "os": platform.platform(),
        "python_version": platform.python_version(),
        "command": cmd,
        "exit_code": proc.returncode,
        "latest_experiment": latest,
        "note": "Local Appendix D wrapper. Raw syscall / lower-layer bypass artifacts must be collected on a Linux-capable host for seccomp/Landlock/container measurements.",
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = REPORTS_DIR / "appendix_d_local_run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Wrote manifest: {manifest_path}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
