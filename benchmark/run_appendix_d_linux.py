
# -*- coding: utf-8 -*-
"""Linux-oriented Appendix D runner for post-compromise / lower-layer bypass work.

This runner is intentionally conservative:
  - It gathers host capabilities and runtime provenance.
  - It executes the canonical post-compromise benchmark through vep.py.
  - It optionally runs the real-OS IPC P3 suite when the host is Linux.
  - It writes a single manifest that can be linked from the whitepaper Appendix D.

The script does not encode exploit payloads. It orchestrates existing repository
scenarios and reports evidence locations for later whitepaper backfill.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

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

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports" / "benchmarks" / "post_compromise"
VEP_CLI = ROOT / "vep.py"
LINUX_P3_TEST = ROOT / "tests" / "security" / "ipc" / "test_ipc_p3_real_os_suite.py"


def run_cmd(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def shell_exists(name: str) -> bool:
    return shutil.which(name) is not None


def read_proc_text(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        return None


def gather_linux_provenance() -> dict[str, Any]:
    info: dict[str, Any] = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "uname": None,
        "docker_available": shell_exists("docker"),
        "seccomp_mode": None,
        "landlock_present": Path("/sys/kernel/security/landlock").exists(),
        "proc_self_status": None,
    }

    if shell_exists("uname"):
        uname = run_cmd(["uname", "-a"], cwd=ROOT)
        info["uname"] = (uname.stdout or uname.stderr).strip() or None

    status = read_proc_text("/proc/self/status")
    info["proc_self_status"] = status
    if status:
        for line in status.splitlines():
            if line.startswith("Seccomp:"):
                info["seccomp_mode"] = line.split(":", 1)[1].strip()
                break

    return info


def run_post_compromise(substrates: str, scenario: str | None) -> dict[str, Any]:
    cmd = [sys.executable, str(VEP_CLI), "benchmark", "post-compromise", "--substrate", substrates]
    if scenario:
        cmd += ["--scenario", scenario]
    proc = run_cmd(cmd, ROOT)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_linux_real_os_suite() -> dict[str, Any]:
    if not LINUX_P3_TEST.exists():
        return {"skipped": True, "reason": "test_ipc_p3_real_os_suite.py not found"}

    if platform.system().lower() != "linux":
        return {
            "skipped": True,
            "reason": "host is not Linux; real OS suite is Linux-only",
            "platform": platform.platform(),
        }

    proc = run_cmd([sys.executable, "-m", "pytest", "-q", str(LINUX_P3_TEST)], cwd=ROOT)
    return {
        "skipped": False,
        "command": [sys.executable, "-m", "pytest", "-q", str(LINUX_P3_TEST)],
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Appendix D Linux-oriented runner")
    parser.add_argument(
        "--substrate",
        default="dros,dros-kernel,opa,scopegate,wasi,tla,sel4,cheri",
        help="Comma-separated substrate list for the post-compromise benchmark.",
    )
    parser.add_argument(
        "--scenario",
        default=None,
        help="Optional single scenario ID such as PC-001.",
    )
    parser.add_argument(
        "--skip-linux-p3",
        action="store_true",
        help="Skip the Linux real-OS IPC P3 suite even when running on Linux.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the manifest without running benchmarks.",
    )
    args = parser.parse_args()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    manifest: dict[str, Any] = {
        "started_at": started_at,
        "host": gather_linux_provenance(),
        "post_compromise": None,
        "linux_real_os_suite": None,
        "notes": [
            "This runner orchestrates repository-native benchmark evidence only.",
            "It does not embed exploit payloads or bypass code.",
        ],
    }

    if not args.dry_run:
        manifest["post_compromise"] = run_post_compromise(args.substrate, args.scenario)
        if not args.skip_linux_p3:
            manifest["linux_real_os_suite"] = run_linux_real_os_suite()
    else:
        manifest["post_compromise"] = {"skipped": True, "reason": "dry-run"}
        manifest["linux_real_os_suite"] = {"skipped": True, "reason": "dry-run"}

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["finished_at"] = finished_at

    out_path = REPORTS_DIR / "appendix_d_linux_run_manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Wrote manifest: {out_path}")

    # Surface stdout/stderr from the benchmark runs for immediate debugging.
    if manifest.get("post_compromise") and isinstance(manifest["post_compromise"], dict):
        if manifest["post_compromise"].get("stdout"):
            print(manifest["post_compromise"]["stdout"])
        if manifest["post_compromise"].get("stderr"):
            print(manifest["post_compromise"]["stderr"], file=sys.stderr)

    if manifest.get("linux_real_os_suite") and isinstance(manifest["linux_real_os_suite"], dict):
        if manifest["linux_real_os_suite"].get("stdout"):
            print(manifest["linux_real_os_suite"]["stdout"])
        if manifest["linux_real_os_suite"].get("stderr"):
            print(manifest["linux_real_os_suite"]["stderr"], file=sys.stderr)

    rc = 0
    if isinstance(manifest.get("post_compromise"), dict):
        rc = max(rc, int(manifest["post_compromise"].get("returncode", 0) or 0))
    if isinstance(manifest.get("linux_real_os_suite"), dict) and not manifest["linux_real_os_suite"].get("skipped", False):
        rc = max(rc, int(manifest["linux_real_os_suite"].get("returncode", 0) or 0))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
