# -*- coding: utf-8 -*-
"""Layer 1.5 substrate-only Landlock EXECUTE feasibility probe.

This probe tests candidate substrate enforcement only.  It intentionally has
no DROS principal, capability, PDP, or GuardVM integration.
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
EXECUTE = 1 << 0
SYS_LANDLOCK_CREATE_RULESET = 444
SYS_LANDLOCK_ADD_RULE = 445
SYS_LANDLOCK_RESTRICT_SELF = 446
SYS_PRCTL = 157
PR_SET_NO_NEW_PRIVS = 38


class RulesetAttr(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64), ("scoped", ctypes.c_uint64)]


class PathBeneathAttr(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int)]


def _syscall(libc: Any, number: int, *args: Any) -> int:
    libc.syscall.restype = ctypes.c_long
    return int(libc.syscall(number, *args))


def _apply_landlock(*, allow_execute: bool) -> tuple[bool, str | None]:
    libc = ctypes.CDLL(None, use_errno=True)
    no_new_privs = _syscall(libc, SYS_PRCTL, PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)
    if no_new_privs != 0:
        return False, f"prctl_failed_errno_{ctypes.get_errno()}"

    ruleset = RulesetAttr(handled_access_fs=EXECUTE, scoped=0)
    fd = _syscall(
        libc,
        SYS_LANDLOCK_CREATE_RULESET,
        ctypes.byref(ruleset),
        ctypes.sizeof(ruleset),
        0,
    )
    if fd < 0:
        return False, f"create_ruleset_failed_errno_{ctypes.get_errno()}"

    try:
        if allow_execute:
            # Allow the complete loader/runtime tree for the substrate-only
            # ALLOW control.  The DENY control still installs no rule.
            parent_fd = os.open("/", os.O_PATH | os.O_DIRECTORY)
            try:
                rule = PathBeneathAttr(parent_fd=parent_fd, allowed_access=EXECUTE)
                added = _syscall(
                    libc,
                    SYS_LANDLOCK_ADD_RULE,
                    fd,
                    1,
                    ctypes.byref(rule),
                    0,
                )
                if added != 0:
                    return False, f"add_rule_failed_errno_{ctypes.get_errno()}"
            finally:
                os.close(parent_fd)

        restricted = _syscall(libc, SYS_LANDLOCK_RESTRICT_SELF, fd, 0)
        if restricted != 0:
            return False, f"restrict_self_failed_errno_{ctypes.get_errno()}"
        return True, None
    finally:
        os.close(fd)


def _attempt_exec(*, allow_execute: bool) -> dict[str, Any]:
    parent_pid = os.getpid()
    pid = os.fork()
    if pid == 0:
        try:
            ok, error = _apply_landlock(allow_execute=allow_execute)
            if not ok:
                print(error, file=sys.stderr)
                os._exit(125)
            os.execve(EXECUTABLE, ["true"], os.environ.copy())
        except BaseException:
            os._exit(127)

    waited_pid, status = os.waitpid(pid, 0)
    return {
        "candidate": "landlock",
        "syscall": "execve",
        "policy": "ALLOW_EXECUTE" if allow_execute else "DENY_EXECUTE",
        "parent_pid": parent_pid,
        "child_pid": waited_pid,
        "target_process_created": os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0,
        "child_exit_code": os.waitstatus_to_exitcode(status),
        "executable": EXECUTABLE,
        "substrate_decision": "ALLOW" if allow_execute else "DENY",
        "dros_decision": "NOT_CONNECTED",
        "audit": "SUBSTRATE_OBSERVATION_ONLY",
    }


def main() -> int:
    started = time.time_ns()
    evidence: dict[str, Any] = {
        "schema": "dros.cli_execution_boundary.substrate_enforcement.v1",
        "layer": "LAYER_1_5_CANDIDATE_ENFORCEMENT",
        "host": platform.node(),
        "platform": platform.platform(),
        "candidate": "landlock",
        "dros_integration": "NOT_CONNECTED",
    }

    if platform.system().lower() != "linux":
        evidence["verdict"] = "UNSUPPORTED_NON_LINUX_HOST"
        evidence["results"] = []
    else:
        results = [_attempt_exec(allow_execute=False), _attempt_exec(allow_execute=True)]
        evidence["results"] = results
        deny = next(item for item in results if item["policy"] == "DENY_EXECUTE")
        allow = next(item for item in results if item["policy"] == "ALLOW_EXECUTE")
        if deny["target_process_created"] is False and allow["target_process_created"] is True:
            evidence["verdict"] = "SUBSTRATE_ENFORCEMENT_CONFIRMED"
        else:
            evidence["verdict"] = "SUBSTRATE_ENFORCEMENT_NOT_CONFIRMED"

    evidence["finished_at_ns"] = time.time_ns()
    evidence["duration_ns"] = evidence["finished_at_ns"] - started
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / "landlock_exec_enforcement_claw-vm.json"
    output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    print(f"[+] evidence: {output}")
    return 0 if evidence["verdict"] in {
        "SUBSTRATE_ENFORCEMENT_CONFIRMED",
        "UNSUPPORTED_NON_LINUX_HOST",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
