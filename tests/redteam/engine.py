# -*- coding: utf-8 -*-
"""
DROS Redteam Test Engine: In-Memory 6P Runtime & C-ABI Capability Bitmask Evaluator
Provides sub-microsecond zero-dependency verification for public redteam suites.
"""
import time
import json
import hashlib
import hmac

class DrosRedteamEngine:
    def __init__(self):
        # 64-bit capability bitmask definitions
        self.CAP_INVENTORY_READ  = 1 << 0
        self.CAP_INVENTORY_WRITE = 1 << 1
        self.CAP_SUPPORT_TOOL    = 1 << 2
        self.CAP_FINANCE_READ    = 1 << 10
        self.CAP_FINANCE_EXEC    = 1 << 11
        self.CAP_SYSTEM_ADMIN    = 1 << 30
        self.CAP_ROOT_SYSCALL    = 1 << 63

        # Role to Bitmask mapping
        self.role_capabilities = {
            "support-agent": self.CAP_INVENTORY_READ | self.CAP_SUPPORT_TOOL,
            "finance-agent": self.CAP_FINANCE_READ | self.CAP_FINANCE_EXEC,
            "admin-agent": 0xFFFFFFFFFFFFFFFF
        }

        # Dynamic Revocation Registry (Agent DID -> is_revoked, revoke_timestamp_ns)
        self.revocation_table = {}
        
        # In-Memory Merkle Audit Log Chain
        self.audit_log = []
        self.last_audit_hash = "0" * 64

    def revoke_agent(self, agent_did):
        """Simulates atomic RCU pointer swap for revocation."""
        t_swap = time.perf_counter_ns()
        self.revocation_table[agent_did] = (True, t_swap)
        return t_swap

    def evaluate_request(self, agent_did, role, target_tool, required_cap, payload=None, dit_token=None):
        """
        Executes C-ABI bitmask evaluation and emits tamper-evident audit record.
        """
        t_start = time.perf_counter_ns()
        
        # 1. Expiry & Revocation Check (L3)
        is_revoked, revoke_time = self.revocation_table.get(agent_did, (False, 0))
        if is_revoked and t_start >= revoke_time:
            t_end = time.perf_counter_ns()
            decision = "DENY"
            status = 403
            reason = "REVOKED_IDENTITY"
            audit_entry = self._append_audit(agent_did, role, target_tool, decision, status, reason, t_end - t_start)
            return {"decision": decision, "status": status, "reason": reason, "latency_ns": t_end - t_start, "audit": audit_entry}

        # 2. DIT Token Integrity Check (L1)
        if dit_token is not None:
            if dit_token.get("expired", False):
                t_end = time.perf_counter_ns()
                decision = "DENY"
                status = 401
                reason = "EXPIRED_TOKEN"
                audit_entry = self._append_audit(agent_did, role, target_tool, decision, status, reason, t_end - t_start)
                return {"decision": decision, "status": status, "reason": reason, "latency_ns": t_end - t_start, "audit": audit_entry}

        # 3. C-ABI Capability Bitmask Check (L2)
        agent_caps = self.role_capabilities.get(role, 0)
        if (agent_caps & required_cap) == required_cap:
            decision = "PERMIT"
            status = 200
            reason = "CAPABILITY_AUTHORIZED"
        else:
            decision = "DENY"
            status = 403
            reason = "UNAUTHORIZED_CAPABILITY"

        # 4. Content Redaction Check for sensitive fields (B2)
        if decision == "PERMIT" and payload and "request_raw_secret" in payload:
            decision = "REDACT"
            status = 200
            reason = "POLICY_REDACTED_SECRET"

        t_end = time.perf_counter_ns()
        latency_ns = t_end - t_start
        audit_entry = self._append_audit(agent_did, role, target_tool, decision, status, reason, latency_ns)
        return {"decision": decision, "status": status, "reason": reason, "latency_ns": latency_ns, "audit": audit_entry}

    def _append_audit(self, agent_did, role, target_tool, decision, status, reason, latency_ns):
        entry = {
            "seq": len(self.audit_log) + 1,
            "timestamp_ns": time.time_ns(),
            "agent_did": agent_did,
            "role": role,
            "target_tool": target_tool,
            "decision": decision,
            "status": status,
            "reason": reason,
            "prev_hash": self.last_audit_hash
        }
        entry_bytes = json.dumps(entry, sort_keys=True).encode('utf-8')
        curr_hash = hashlib.sha256(entry_bytes).hexdigest()
        entry["hash"] = curr_hash
        self.last_audit_hash = curr_hash
        self.audit_log.append(entry)
        return entry

    def verify_audit_chain(self):
        """Verifies the cryptographic integrity of the entire audit chain."""
        prev = "0" * 64
        for entry in self.audit_log:
            saved_hash = entry["hash"]
            check_entry = dict(entry)
            del check_entry["hash"]
            expected = hashlib.sha256(json.dumps(check_entry, sort_keys=True).encode('utf-8')).hexdigest()
            if expected != saved_hash or entry["prev_hash"] != prev:
                return False
            prev = saved_hash
        return True
