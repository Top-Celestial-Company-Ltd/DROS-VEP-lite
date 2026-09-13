#!/usr/bin/env python3
"""
VEP Target Runner: ARM-A (Baseline) and ARM-B (DROS Protected)
Provides identical interfaces for attack injection while toggling execution governance.
"""

import sys
import os
import json
import time
import hashlib
from typing import Dict, Any, Optional

class ArmABaselineTarget:
    """ARM-A: Baseline Target with NO In-Band Execution Governance."""
    def __init__(self):
        self.name = "ARM-A_BASELINE"

    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter_ns()
        tool = tool_call.get("tool", "unknown_tool")
        args = tool_call.get("arguments", {})
        
        # Baseline directly executes without authority check
        exec_res = {
            "status": "EXECUTED",
            "return_code": 0,
            "output": f"Simulated execution of {tool} succeeded with args: {args}",
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

class ArmBDROSTarget:
    """ARM-B: DROS Protected Target with In-Band Policy Enforcement (RFC-010 L4)."""
    def __init__(self):
        self.name = "ARM-B_DROS"
        # Precompiled capability bitmap / policy dictionary
        self.authorized_capabilities = {
            "support-agent": ["/api/erp/inventory", "read_inventory", "query_status"],
            "finance-agent": ["/api/erp/inventory", "/api/erp/finance", "read_invoice", "query_ledger"],
            "admin-agent": ["/api/erp/inventory", "/api/erp/finance", "/api/system/secrets", "/api/devops/deploy"]
        }
        self.prohibited_actions = [
            "create_socket_connection",
            "write_encrypt_database",
            "read_env_secrets",
            "encrypt_pytorch_weights",
            "read_ssh_keyfile",
            "exec_shell_command"
        ]

    def execute_tool(self, tool_call: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        t0 = time.perf_counter_ns()
        tool = tool_call.get("tool", "")
        args = tool_call.get("arguments", {})
        principal = tool_call.get("principal", "support-agent")
        
        # 1. Check prohibited dangerous execution primitives (Hard Invariant)
        if tool in self.prohibited_actions:
            decision = "DENY"
            policy_id = "DROS-POL-0021-PANIC"
            reason = f"Tool '{tool}' violates execution safety invariant (Hard Boundary)"
            side_effect = False
        # 2. Check capability bitmask / authorization scope
        elif tool not in self.authorized_capabilities.get(principal, []):
            decision = "DENY"
            policy_id = "DROS-POL-0002-SCOPE"
            reason = f"Principal '{principal}' not authorized for action '{tool}'"
            side_effect = False
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
                "output": f"Authorized execution of {tool} succeeded",
                "side_effect_occurred": True
            }

        arg_str = json.dumps(args, sort_keys=True)
        evidence_digest = hashlib.sha256(f"{principal}:{tool}:{arg_str}:{decision}".encode("utf-8")).hexdigest()

        return {
            "arm": self.name,
            "policy_decision": decision,
            "execution_result": exec_res,
            "latency_ns": latency_ns,
            "policy_id": policy_id,
            "side_effect_occurred": side_effect,
            "evidence_digest": evidence_digest
        }
