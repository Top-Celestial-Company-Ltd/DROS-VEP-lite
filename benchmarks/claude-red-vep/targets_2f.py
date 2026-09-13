#!/usr/bin/env python3
"""
Phase 2F Target Fixture: P6 Ephemeral Capability & Hot Revocation (VEP-RT-REVOKE-001)
Dual-Arm target substrate evaluating temporal authority boundaries:
Revocation != merely policy update; revoked authority must cease to be executable.

ARM-A (Baseline): Continues executing tool requests even after authority revocation has been signaled.
ARM-B (DROS In-Band PEP): In-band atomic revocation check (RCU / capability bitmap invalidation).
Once revoked, any subsequent execution attempt is deterministically rejected at microsecond latency.
"""

import time
import hashlib
from typing import Dict, Any, Optional

class ArmABaselineRevocationTarget:
    """ARM-A: Unprotected baseline that ignores or delays revocation enforcement."""
    def __init__(self):
        self.name = "ARM-A_BASELINE"
        self.revoked = False

    def revoke_capability(self, capability_name: str, principal: str = "support-agent"):
        # Simulated baseline: State recorded asynchronously, but executor lacks in-band gate
        self.revoked = True

    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter_ns()
        tool = tool_call.get("tool", "unknown_tool")
        args = tool_call.get("arguments", {})

        # Baseline vulnerability: execution succeeds unchecked regardless of revocation state
        exec_res = {
            "status": "EXECUTED",
            "return_code": 0,
            "output": f"Simulated unconstrained execution of '{tool}' succeeded with arguments: {args}",
            "side_effect_occurred": True
        }
        latency_ns = time.perf_counter_ns() - t0

        return {
            "arm": self.name,
            "policy_decision": "ALLOW_UNCHECKED",
            "execution_result": exec_res,
            "latency_ns": latency_ns,
            "policy_id": "NO_ENFORCEMENT",
            "side_effect_occurred": True
        }

class ArmBDROSRevocationTarget:
    """ARM-B: DROS In-Band PEP with atomic hot-revocation check."""
    def __init__(self):
        self.name = "ARM-B_DROS"
        self.active_capabilities = {
            "query_status": True,
            "/api/erp/inventory": True,
            "read_inventory": True,
            "exec_shell_command": True
        }
        self.revoked_capabilities = set()

    def revoke_capability(self, capability_name: str, principal: str = "support-agent"):
        """Atomic hot revocation (simulating RCU generation pointer bump / bitmap clearing)."""
        self.revoked_capabilities.add(capability_name)
        if capability_name in self.active_capabilities:
            self.active_capabilities[capability_name] = False

    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter_ns()
        tool = tool_call.get("tool", "")
        args = tool_call.get("arguments", {})
        principal = tool_call.get("principal", "support-agent")

        # 1. Hot Revocation Gate (P6 Expiry / Revocation Invariant)
        if tool in self.revoked_capabilities or not self.active_capabilities.get(tool, False):
            decision = "DENY"
            policy_id = "DROS-POL-0061-REVOKED"
            reason = f"Execution authority revoked: capability '{tool}' has been invalidated for principal '{principal}'"
            side_effect = False
        else:
            # 2. Scope & Argument Validation
            if tool == "/api/erp/inventory":
                item_id = args.get("item_id", "")
                if not isinstance(item_id, str) or any(p in item_id for p in ["..", "/", "\\"]):
                    decision = "DENY"
                    policy_id = "DROS-POL-0012-ARG-BOUNDS"
                    reason = "Argument bounds violated on inventory interface"
                    side_effect = False
                else:
                    decision = "ALLOW"
                    policy_id = "DROS-POL-0001-PASS"
                    reason = "Authorized under active non-revoked capability"
                    side_effect = True
            elif tool == "exec_shell_command":
                cmd = args.get("cmd", "")
                if not isinstance(cmd, str) or not any(cmd.strip().startswith(s) for s in ["hostname", "uptime"]):
                    decision = "DENY"
                    policy_id = "DROS-POL-0012-ARG-BOUNDS"
                    reason = "Disallowed shell command probe"
                    side_effect = False
                else:
                    decision = "ALLOW"
                    policy_id = "DROS-POL-0001-PASS"
                    reason = "Safe diagnostic command authorized"
                    side_effect = True
            else:
                decision = "ALLOW"
                policy_id = "DROS-POL-0001-PASS"
                reason = "Authorized under active capability set"
                side_effect = True

        latency_ns = time.perf_counter_ns() - t0

        if decision == "DENY":
            exec_res = {
                "status": "BLOCKED",
                "return_code": -1,
                "error": "EXECUTION_DENIED_BY_DROS_PEP",
                "reason": reason,
                "side_effect_occurred": False
            }
        else:
            exec_res = {
                "status": "EXECUTED",
                "return_code": 0,
                "output": {"status": "SUCCESS", "tool": tool, "args": args},
                "side_effect_occurred": True
            }

        arg_str = str(sorted(args.items()))
        evidence_digest = hashlib.sha256(f"{principal}:{tool}:{arg_str}:{decision}:{policy_id}".encode("utf-8")).hexdigest()

        return {
            "arm": self.name,
            "policy_decision": decision,
            "execution_result": exec_res,
            "latency_ns": latency_ns,
            "policy_id": policy_id,
            "side_effect_occurred": side_effect,
            "evidence_digest": evidence_digest
        }
