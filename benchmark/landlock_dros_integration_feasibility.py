# -*- coding: utf-8 -*-
"""Layer 1.5 composition probe: reference DROS seam + Landlock substrate.

This is an integration-feasibility probe, not canonical DROS PDP/GuardVM
evidence.  It makes the authority and substrate decisions independently
observable before attempting a real execve.
"""

from __future__ import annotations

import ctypes
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vep.cli_execution_boundary import CliExecutionPep, ExecutionRequest


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "reports" / "benchmarks" / "post_compromise" / "cli_execution_boundary"
TRUE = "/usr/bin/true"
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
    if _syscall(libc, SYS_PRCTL, PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        return False, f"prctl_errno_{ctypes.get_errno()}"

    ruleset = RulesetAttr(handled_access_fs=EXECUTE, scoped=0)
    fd = _syscall(libc, SYS_LANDLOCK_CREATE_RULESET, ctypes.byref(ruleset), ctypes.sizeof(ruleset), 0)
    if fd < 0:
        return False, f"create_ruleset_errno_{ctypes.get_errno()}"
    try:
        if allow_execute:
            parent_fd = os.open("/", os.O_PATH | os.O_DIRECTORY)
            try:
                rule = PathBeneathAttr(allowed_access=EXECUTE, parent_fd=parent_fd)
                if _syscall(libc, SYS_LANDLOCK_ADD_RULE, fd, 1, ctypes.byref(rule), 0) != 0:
                    return False, f"add_rule_errno_{ctypes.get_errno()}"
            finally:
                os.close(parent_fd)
        if _syscall(libc, SYS_LANDLOCK_RESTRICT_SELF, fd, 0) != 0:
            return False, f"restrict_self_errno_{ctypes.get_errno()}"
        return True, None
    finally:
        os.close(fd)


def _request(*, executable: str) -> ExecutionRequest:
    return ExecutionRequest(
        principal="agent-a",
        task="task-cli-014",
        capability="process.execute.safe",
        executable=executable,
        argv=[Path(executable).name],
        target="stdout",
        working_directory="/srv/agent/work",
        runtime_posture={"platform": "linux", "namespace": "agent-a"},
        policy_context={"policy_version": "phase1-fixture"},
        issued_at=datetime.now(timezone.utc),
        ttl_seconds=30,
        provenance={"agent_id": "agent-a", "session_id": "session-014"},
    )


def _run_case(*, name: str, dros_executable: str, substrate_allow: bool) -> dict[str, Any]:
    pep = CliExecutionPep.for_test_policy(
        allowed_executables={TRUE},
        allowed_capabilities={"process.execute.safe"},
    )
    request = _request(executable=dros_executable)
    decision = pep.evaluate(request)
    result: dict[str, Any] = {
        "case": name,
        "dros_authority_source": "phase1_deterministic_reference_seam",
        "dros_decision": decision.decision,
        "dros_reason_code": decision.reason_code,
        "substrate": "landlock",
        "substrate_policy": "ALLOW_EXECUTE" if substrate_allow else "DENY_EXECUTE",
        "argv_hash": decision.argv_hash,
        "executable": dros_executable,
        "exec_attempted": False,
        "target_process_created": False,
        "parent_pid": os.getpid(),
        "child_pid": None,
        "audit": "COMPOSITION_OBSERVATION_ONLY",
    }

    if decision.decision == "DENY":
        return result

    result["exec_attempted"] = True
    parent_pid = os.getpid()
    pid = os.fork()
    result["child_pid"] = pid
    if pid == 0:
        try:
            ok, _error = _apply_landlock(allow_execute=substrate_allow)
            if not ok:
                os._exit(125)
            os.execve(TRUE, ["true"], os.environ.copy())
        except BaseException:
            os._exit(127)

    _, status = os.waitpid(pid, 0)
    result["parent_pid"] = parent_pid
    result["child_exit_code"] = os.waitstatus_to_exitcode(status)
    result["target_process_created"] = result["child_exit_code"] == 0
    return result


def main() -> int:
    if platform.system().lower() != "linux":
        print(json.dumps({"verdict": "UNSUPPORTED_NON_LINUX_HOST"}, indent=2))
        return 0

    results = [
        _run_case(name="14-A_DROS_DENY_SUBSTRATE_ALLOW", dros_executable="/bin/sh", substrate_allow=True),
        _run_case(name="14-B_DROS_ALLOW_SUBSTRATE_DENY", dros_executable=TRUE, substrate_allow=False),
        _run_case(name="14-C_DROS_ALLOW_SUBSTRATE_ALLOW", dros_executable=TRUE, substrate_allow=True),
    ]
    evidence = {
        "schema": "dros.cli_execution_boundary.composition.v1",
        "layer": "LAYER_1_5_DROS_INTEGRATION_FEASIBILITY",
        "host": platform.node(),
        "candidate": "landlock",
        "dros_pdp": "REFERENCE_SEAM_ONLY",
        "canonical_dros_pdp_guardvm": "NOT_CONNECTED",
        "results": results,
        "verdict": "DROS_INTEGRATION_NOT_PROVEN",
        "claim_boundary": "Composition behavior observed; canonical DROS authority integration is not established.",
        "finished_at_ns": time.time_ns(),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / "landlock_dros_integration_claw-vm.json"
    output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    print(f"[+] evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
