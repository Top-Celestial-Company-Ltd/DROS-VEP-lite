# -*- coding: utf-8 -*-
"""
DROS Mobile SDK Core v2.0 (Emulating On-Device iOS/Android FFI Runtime)
Provides sub-microsecond in-process execution gating for mobile LLM tool calls.
Supports MobileSafetyBench & MobileWorldSafety threat vectors:
- SMS/Notification Environmental Injection (Clipboard/Exfiltration)
- Stealth Background Geolocation Tracking
- Eavesdropping Surveillance (Background Microphone/Camera)
- Biometric Payment Hijacking
"""

import time
import json
import os

class DROSMobileGuard:
    def __init__(self, policy_path=None):
        if policy_path is None:
            policy_path = os.path.join(os.path.dirname(__file__), "..", "config", "mobile_policy.json")
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)
            
        self.capabilities = {
            k: int(v, 16) for k, v in self.policy["capability_bitmasks"].items()
        }
        self.roles = self.policy["roles"]
        self.audit_trail = []

    def verify_tool_invocation(self, role_id, action_name, params=None, biometric_token=None, is_background=False):
        """
        On-device FFI boundary verification (Sub-microsecond, Zero Network).
        Returns: (allowed: bool, reason: str, latency_ns: int)
        """
        t0 = time.perf_counter_ns()
        
        role = self.roles.get(role_id)
        if not role:
            t1 = time.perf_counter_ns()
            self._log(role_id, action_name, "DENY", "Unknown mobile role", t1 - t0)
            return False, "DENY_UNKNOWN_ROLE", t1 - t0

        role_mask = int(role["bitmask"], 16)
        required_mask = self.capabilities.get(action_name, 0)
        
        # 1. Zero-Heap Bitmask Comparison
        if (role_mask & required_mask) != required_mask:
            t1 = time.perf_counter_ns()
            self._log(role_id, action_name, "DENY", f"Permission missing: 0x{required_mask:X}", t1 - t0)
            return False, "DENY_PRIVILEGE_VIOLATION", t1 - t0

        # 2. Surveillance / Background Context Constraint (MobileSafetyBench)
        if is_background and action_name in ["RESTRICTED_MICROPHONE_RECORD", "RESTRICTED_GPS_LOCATION"]:
            t1 = time.perf_counter_ns()
            self._log(role_id, action_name, "DENY", "Blocked: Background surveillance forbidden", t1 - t0)
            return False, "DENY_BACKGROUND_SURVEILLANCE_FORBIDDEN", t1 - t0

        # 3. Clipboard Poisoning & Exfiltration (MobileWorldSafety)
        if action_name == "RESTRICTED_READ_CLIPBOARD":
            # Only explicit interactive sessions can read clipboard
            if role_id != "AUTHENTICATED_USER_SESSION":
                t1 = time.perf_counter_ns()
                self._log(role_id, action_name, "DENY", "Clipboard access denied for background/chatbot role", t1 - t0)
                return False, "DENY_CLIPBOARD_ISOLATION", t1 - t0

        # 4. Critical Financial / Biometric Enforcement (AgentDojo Banking)
        if action_name == "CRITICAL_FINANCIAL_PAYMENT":
            if not biometric_token or biometric_token != "SECURE_ENCLAVE_BIOMETRIC_AUTH_VALID":
                t1 = time.perf_counter_ns()
                self._log(role_id, action_name, "DENY", "Missing Secure Enclave biometric validation", t1 - t0)
                return False, "DENY_BIOMETRIC_REQUIRED", t1 - t0

        t1 = time.perf_counter_ns()
        self._log(role_id, action_name, "ALLOW", "Authorized mobile execution", t1 - t0)
        return True, "ALLOW_GOVERNED", t1 - t0

    def _log(self, role, action, verdict, reason, latency_ns):
        self.audit_trail.append({
            "timestamp": time.time(),
            "role": role,
            "action": action,
            "verdict": verdict,
            "reason": reason,
            "latency_ns": latency_ns
        })
