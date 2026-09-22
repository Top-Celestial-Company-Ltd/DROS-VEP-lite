# -*- coding: utf-8 -*-
"""Layer 2 Linux feasibility harness for execve/execveat.

This harness deliberately distinguishes real syscall/process observations from
DROS authorization evidence.  Until a real CLI PEP is installed at the
selected deployment boundary, the verdict is BOUNDARY_SELECTION_REQUIRED.
"""

from __future__ import annotations

import ctypes
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "reports" / "benchmarks" / "post_compromise" / "cli_execution_boundary"
EXECUTABLE = "/usr/bin/true"
EXECVEAT_NR_X86_64 = 322
AT_FDCWD = -100
AT_EMPTY_PATH = 0x1000


def _wait_for_child(pid: int) -> dict[str, Any]:
    waited_pid, status = os.waitpid(pid, 0)
    return {
        "pid": waited_pid,
        "exit_code": os.waitstatus_to_exitcode(status),
        "signaled": os.WIFSIGNALED(status),
        "signal": os.WTERMSIG(status) if os.WIFSIGNALED(status) else None,
    }


def _run_execve() -> dict[str, Any]:
    parent_pid = os.getpid()
    pid = os.fork()
    if pid == 0:
        try:
            os.execve(EXECUTABLE, ["true"], os.environ.copy())
        except BaseException:
            os._exit(127)

    result = _wait_for_child(pid)
    result.update(
        {"syscall": "execve", "executable": EXECUTABLE, "parent_pid": parent_pid}
    )
    return result


def _run_execveat() -> dict[str, Any]:
    parent_pid = os.getpid()
    libc = ctypes.CDLL(None, use_errno=True)
    syscall = libc.syscall
    syscall.restype = ctypes.c_long
    fd = os.open(EXECUTABLE, os.O_RDONLY)
    try:
        pid = os.fork()
        if pid == 0:
            try:
                argv = (ctypes.c_char_p * 2)(b"true", None)
                envp = (ctypes.c_char_p * 1)(None)
                result = syscall(
                    EXECVEAT_NR_X86_64,
                    fd,
                    ctypes.c_char_p(b""),
                    argv,
                    envp,
                    AT_EMPTY_PATH,
                )
                os._exit(127 if result < 0 else 0)
            except BaseException:
                os._exit(127)

        result = _wait_for_child(pid)
        result.update(
            {"syscall": "execveat", "executable": EXECUTABLE, "parent_pid": parent_pid}
        )
        return result
    finally:
        os.close(fd)


def _dros_pep_available() -> bool:
    try:
        from vep.cli_execution_boundary import CliExecutionPep  # noqa: F401
    except ImportError:
        return False
    return False


def main() -> int:
    started_at = time.time_ns()
    evidence: dict[str, Any] = {
        "schema": "dros.cli_execution_boundary.feasibility.v1",
        "layer": "LAYER_2_LINUX_LIVE_FEASIBILITY",
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "selected_boundary": ["execve", "execveat"],
        "dros_pep_available": False,
        "dros_decision": "NOT_AVAILABLE",
        "audit": "NOT_AVAILABLE",
        "provenance": "HOST_OBSERVATION_ONLY",
        "results": [],
    }

    if platform.system().lower() != "linux":
        evidence["verdict"] = "UNSUPPORTED_NON_LINUX_HOST"
    else:
        evidence["results"] = [_run_execve(), _run_execveat()]
        evidence["verdict"] = (
            "SUCCESS" if evidence["dros_pep_available"] else "BOUNDARY_SELECTION_REQUIRED"
        )

    evidence["finished_at_ns"] = time.time_ns()
    evidence["duration_ns"] = evidence["finished_at_ns"] - started_at
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "latest_feasibility.json"
    output_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    print(f"[+] evidence: {output_path}")
    return 0 if evidence["verdict"] in {"SUCCESS", "BOUNDARY_SELECTION_REQUIRED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
