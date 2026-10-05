# -*- coding: utf-8 -*-
"""
DROS Drone Execution Adapter (MAVLink / PX4 / Cyber-Physical PEP).
Enforces DROS PDP policies at the cyber-physical execution boundary before
any command reaches the PX4 MAVLink endpoint or actuator bus.
"""

import time
import calendar
import json
import hashlib
from typing import Dict, Any, Optional, Set, Tuple, List

from drone.validator import (
    validate_execution_request,
    validate_drone_posture,
    validate_provenance,
    compute_arg_hash,
    verify_execution_signature
)
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService

# Authoritative pre-registered Ed25519 identity keypairs
# 1. agent.mission.planner (low-privilege planning agent)
#    Priv: 15496b240763c8b70795633c9f50c40272223999db094cb36c36d5ef4b488152
PLANNER_PUBKEY_HEX = "14fcfd4a2713f2e23d1899cfb69d7a57e391410be74c7372b079597f0c3ab82f"

# 2. onboard-mission-agent (onboard flight computer agent)
#    Priv: e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f
ONBOARD_PUBKEY_HEX = "8d9214cb7f1262fb1c27e6d5fee11130ba8b21817536b076989f29e2ab0f12f9"

# Legacy test pubkey for backward compatibility
STANDARD_TEST_PUBKEY_HEX = ONBOARD_PUBKEY_HEX

class DroneExecutionAdapter:
    """
    DROS Enforcement Point for Drone / PX4 execution paths.
    Enforces:
      - Cryptographic Identity Attestation via Ed25519 (Ticket-02)
      - Server-Side Capability Grant Store (Ticket-01)
      - Principal Attribution & Capability Scope (ATS-006)
      - Runtime Posture Evaluation (ATS-007, ATS-010)
      - Nonce & Replay Prevention (ATS-008)
      - Cryptographic Provenance Verification (ATS-009)
      - Deterministic ArgHash Integrity
      - Safe Degradation & Fail-Closed Behavior (T5)
    """
    def __init__(self, sitl_engine: Optional[PX4SITLEngine] = None):
        self.sitl = sitl_engine  # Pure PDP does not require execution engine; optional for backward compatibility
        self.seen_request_ids: Set[str] = set()
        self.known_postures: Dict[str, Dict[str, Any]] = {} # posture_ref -> external posture object
        self.revoked_capabilities: Set[str] = set() # capability or request_id revoked
        self.audit_log: List[Dict[str, Any]] = []

        # Fault Injection flags for T5 Fail-Closed Verification
        self.pdp_healthy: bool = True
        self.pep_healthy: bool = True

        # Authoritative Server-Side Trust Root & Identity Store (Ticket-02)
        # 1-to-1 Principal-to-Key binding: Distinct cryptographic identities for distinct agents
        self.trusted_keystore: Dict[str, str] = {
            "agent.mission.planner": PLANNER_PUBKEY_HEX,
            "onboard-mission-agent": ONBOARD_PUBKEY_HEX
        }

        # Authoritative Server-Side Capability Grant Store (Ticket-01)
        # principal -> Set of granted capabilities
        self.capability_grant_store: Dict[str, Set[str]] = {
            "agent.mission.planner": {"READ_TELEMETRY", "PLAN_WAYPOINT", "SET_WAYPOINT", "SET_MODE", "TAKEOFF", "LAND", "RTL"},
            "onboard-mission-agent": {"READ_TELEMETRY", "PLAN_WAYPOINT", "SET_WAYPOINT", "SET_MODE", "ARM", "TAKEOFF", "LAND", "RTL", "MISSION_UPLOAD", "PARAMETER_WRITE", "CAMERA_TRIGGER", "GIMBAL_CONTROL"}
        }

        # Action-to-Capability mapping definition
        self.action_capability_map = {
            "READ_TELEMETRY": "READ_TELEMETRY",
            "PLAN_WAYPOINT": "PLAN_WAYPOINT",
            "SET_WAYPOINT": "SET_WAYPOINT",
            "TAKEOFF": "TAKEOFF",
            "LAND": "LAND",
            "RTL": "RTL",
            "SET_MODE": "SET_MODE",
            "ARM": "ARM",
            "DISARM": "DISARM",
            "ACTUATOR_COMMAND": "ACTUATOR_COMMAND",
            "MISSION_UPLOAD": "MISSION_UPLOAD",
            "PARAMETER_WRITE": "PARAMETER_WRITE",
            "CAMERA_TRIGGER": "CAMERA_TRIGGER",
            "GIMBAL_CONTROL": "GIMBAL_CONTROL",
            "SHELL_COMMAND": "SHELL_COMMAND",
            "FILE_OPERATION": "FILE_OPERATION"
        }

        # Companion interface prohibited actions
        self.disallowed_companion_paths: Set[str] = {"SHELL_COMMAND", "FILE_OPERATION"}

    def register_external_posture(self, posture_obj: Dict[str, Any]):
        """Registers verified external posture from navigation integrity service."""
        posture_ref = posture_obj.get("posture_ref")
        if posture_ref:
            self.known_postures[posture_ref] = posture_obj

    def revoke_capability(self, identifier: str):
        """Hot revocation of capability or request ID."""
        self.revoked_capabilities.add(identifier)

    def trigger_pdp_timeout(self):
        """Simulates PDP governance subsystem timeout/unavailability."""
        self.pdp_healthy = False

    def trigger_pep_crash(self):
        """Simulates PEP enforcement crash/fault."""
        self.pep_healthy = False

    def evaluate_and_execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main PDP/PEP evaluation loop.
        Returns standardized verdict dictionary:
          verdict: ALLOW | DENY | ERROR
          reason: string
          execution_status: EXECUTED | NOT_EXECUTED
          audit_record: dict
        """
        t0 = time.perf_counter_ns()

        # 0. Subsystem Health / Fail-Closed Check (T5-01 PDP Timeout & T5-02 PEP Crash)
        if not self.pep_healthy:
            # Physical response: safe isolation / flight-controller failsafe
            return self._build_verdict(
                request, "DENY", "PEP_CRASH_FAIL_CLOSED",
                "Policy Enforcement Point is crashed/faulted. Enforcing fail-closed isolation.",
                t0
            )

        if not self.pdp_healthy:
            # Physical response: flight-safety architecture takes over, DENY new privileged actions
            return self._build_verdict(
                request, "DENY", "PDP_TIMEOUT_FAIL_CLOSED",
                "Policy Decision Point timed out. Denying all new privileged execution requests.",
                t0
            )

        req_id = request.get("request_id", "")
        action = request.get("action", "")
        principal = request.get("principal", "")
        capability = request.get("capability", "")
        payload = request.get("payload", {})
        runtime_posture_ref = request.get("runtime_posture", {}).get("posture_ref")
        provenance = request.get("provenance", {})
        arg_hash = request.get("arg_hash", "")
        expiry = request.get("expiry", "")

        # 1. Schema Validation Check
        is_valid_schema, schema_err = validate_execution_request(request)
        if not is_valid_schema:
            return self._build_verdict(
                request, "DENY", "SCHEMA_VALIDATION_FAILED",
                f"Request does not conform to DroneExecutionRequest schema: {schema_err}",
                t0
            )

        # 2. ArgHash Integrity Verification
        computed_hash = compute_arg_hash(payload)
        if arg_hash and computed_hash != arg_hash:
            return self._build_verdict(
                request, "DENY", "ARG_HASH_MISMATCH",
                f"Argument hash tampered or altered. Expected {computed_hash}, got {arg_hash}",
                t0
            )

        # 3. Nonce & Replay Protection (ATS-008)
        if req_id in self.seen_request_ids:
            return self._build_verdict(
                request, "DENY", "REPLAY_DETECTED",
                f"Duplicate request_id '{req_id}' detected.",
                t0
            )
        self.seen_request_ids.add(req_id)

        # 4. TTL / Expiry Check
        if expiry:
            try:
                # Handle ISO UTC string
                # Comparison against current time
                exp_ts = calendar.timegm(time.strptime(expiry[:19], "%Y-%m-%dT%H:%M:%S"))
                if time.time() > exp_ts:
                    return self._build_verdict(
                        request, "DENY", "REQUEST_EXPIRED",
                        f"Request expired at {expiry}",
                        t0
                    )
            except Exception as e:
                return self._build_verdict(
                    request, "DENY", "INVALID_EXPIRY_FORMAT",
                    f"Malformed expiry timestamp: {e}",
                    t0
                )

        # Disallowed high-privilege commands for autonomous agents (e.g. SHELL_COMMAND, FILE_OPERATION)
        if action in ["SHELL_COMMAND", "FILE_OPERATION"]:
            return self._build_verdict(
                request, "DENY", "DISALLOWED_EXECUTION_PATH",
                f"Execution path '{action}' is strictly forbidden on drone companion interface.",
                t0
            )

        # 5. Cryptographic Identity & Provenance Verification via Ed25519 (Ticket-02)
        # Trust Root Constraint: Public key is retrieved strictly from server-side trusted_keystore.
        if principal not in self.trusted_keystore:
            return self._build_verdict(
                request, "DENY", "UNKNOWN_UNTRUSTED_PRINCIPAL",
                f"Principal '{principal}' is not recognized in authoritative trust keystore.",
                t0
            )

        auth_pubkey_hex = self.trusted_keystore[principal]
        prov_ref = provenance.get("provenance_ref")
        prov_data = provenance.get("data")

        if not prov_data:
            return self._build_verdict(
                request, "DENY", "PROVENANCE_FORGERY_OR_INVALID",
                "Missing structured provenance data or bare self-assertion rejected.",
                t0
            )

        sig_hex = prov_data.get("signature")
        c_type = prov_data.get("credential_type")
        v_status = prov_data.get("verification_status")
        prov_principal = prov_data.get("principal_id")

        if prov_principal != principal:
            return self._build_verdict(
                request, "DENY", "PRINCIPAL_ATTRIBUTION_MISMATCH",
                f"Requesting principal '{principal}' does not match provenance principal '{prov_principal}'",
                t0
            )

        if not sig_hex or c_type == "NONE" or v_status in ["FORGED", "MISSING", "STALE"]:
            return self._build_verdict(
                request, "DENY", "PROVENANCE_FORGERY_OR_INVALID",
                f"Unsigned request, invalid credential type, or flagged status '{v_status}'.",
                t0
            )

        # Hot Revocation Check (Check early before or during crypto verification)
        if capability in self.revoked_capabilities or req_id in self.revoked_capabilities:
            return self._build_verdict(
                request, "DENY", "CAPABILITY_REVOKED",
                f"Capability '{capability}' or request '{req_id}' has been revoked",
                t0
            )

        # Physical cryptographic verification: verify Ed25519 signature over canonical request bytes
        is_sig_valid = verify_execution_signature(request, sig_hex, auth_pubkey_hex)
        if not is_sig_valid:
            return self._build_verdict(
                request, "DENY", "CRYPTOGRAPHIC_SIGNATURE_INVALID",
                f"Ed25519 signature verification failed against authoritative public key for principal '{principal}'.",
                t0
            )

        # 6. Authoritative Server-Side Capability Grant Verification (Ticket-01)
        # Never trusts capability declared by client; checks if principal was granted the required capability.
        required_cap = self.action_capability_map.get(action)
        granted_caps = self.capability_grant_store.get(principal, set())
        if required_cap not in granted_caps:
            return self._build_verdict(
                request, "DENY", "UNAUTHORIZED_CAPABILITY",
                f"Principal '{principal}' has not been granted required capability '{required_cap}' in server grant store.",
                t0
            )

        # Also enforce client-declared capability matches required capability (defense-in-depth)
        if capability != required_cap:
            return self._build_verdict(
                request, "DENY", "UNAUTHORIZED_CAPABILITY",
                f"Action '{action}' requires capability '{required_cap}', but '{capability}' was held",
                t0
            )

        # 8. Runtime Posture Resolution (ATS-007, ATS-010)
        # Agent-asserted posture or unregistered posture_ref is rejected
        if not runtime_posture_ref or runtime_posture_ref not in self.known_postures:
            return self._build_verdict(
                request, "DENY", "UNTRUSTED_POSTURE_REFERENCE",
                f"Runtime posture reference '{runtime_posture_ref}' not found in external authoritative store.",
                t0
            )

        external_posture_obj = self.known_postures[runtime_posture_ref]
        current_posture = external_posture_obj.get("posture")
        trust_level = external_posture_obj.get("trust_level")

        # Evaluate capability vs posture policy (ATS-007)
        if current_posture in ["GPS_UNTRUSTED", "NAVIGATION_UNAVAILABLE"]:
            if action in ["SET_WAYPOINT", "MISSION_UPLOAD"]:
                return self._build_verdict(
                    request, "DENY", "POSTURE_DEGRADATION_DENIAL",
                    f"Action '{action}' denied because external posture is {current_posture}.",
                    t0
                )
        elif current_posture == "GPS_DEGRADED":
            # Only restricted waypoints permitted, or speed limits
            if action == "MISSION_UPLOAD":
                return self._build_verdict(
                    request, "DENY", "POSTURE_DEGRADATION_DENIAL",
                    f"Action '{action}' denied in GPS_DEGRADED mode (restricted navigation only).",
                    t0
                )

        # 9. All PDP Checks Passed -> Dispatch to PEP / SITL Execution
        success, effect = self.sitl.handle_mavlink_command(action, payload)
        
        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
        verdict_res = {
            "verdict": "ALLOW",
            "reason": "POLICY_AUTHORIZED",
            "execution_status": "EXECUTED" if success else "EXECUTION_FAILED",
            "physical_effect": effect,
            "latency_us": elapsed_us,
            "request_id": req_id,
            "principal": principal,
            "action": action,
            "runtime_posture": current_posture,
            "arg_hash": arg_hash,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.audit_log.append(verdict_res)
        return verdict_res

    def evaluate_and_authorize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pure PDP evaluation method for DROS PEP (Milestone M1.1-S2-E).
        Evaluates 6P cryptographic identity, provenance, capabilities, and posture.
        Does NOT execute internal simulated SITL commands.
        Returns pure authorization verdict:
          verdict: ALLOW | DENY | ERROR
          reason: string
          pdp_authorized: True | False
          correlation_meta: dict
        """
        t0 = time.perf_counter_ns()

        if not self.pdp_healthy:
            return self._build_verdict(
                request, "DENY", "PDP_UNAVAILABLE_TIMEOUT",
                "DROS PDP governance engine heartbeat timeout (Fail-Closed)",
                t0
            )

        if not self.pep_healthy:
            return self._build_verdict(
                request, "DENY", "PEP_CRASH_FAIL_CLOSED",
                "DROS PEP enforcement proxy crashed or unreachable (Fail-Closed)",
                t0
            )

        if not isinstance(request, dict):
            return self._build_verdict(request, "DENY", "MALFORMED_REQUEST", "Request payload must be a JSON object", t0)

        req_id = request.get("request_id")
        principal = request.get("principal")
        capability = request.get("capability")
        action = request.get("action")
        target = request.get("target", {})
        payload = request.get("payload", {})
        runtime_posture_ref = request.get("runtime_posture", {}).get("posture_ref")
        provenance = request.get("provenance", {})
        expiry_str = request.get("expiry")
        arg_hash = request.get("arg_hash")

        if not all([req_id, principal, capability, action, target, payload, provenance, expiry_str, arg_hash]):
            return self._build_verdict(
                request, "DENY", "SCHEMA_VIOLATION",
                "Missing required 6P policy attribute fields in execution request.",
                t0
            )

        if req_id in self.seen_request_ids:
            return self._build_verdict(
                request, "DENY", "REPLAY_ATTACK_DETECTED",
                f"Execution request_id '{req_id}' has already been processed.",
                t0
            )
        self.seen_request_ids.add(req_id)

        try:
            from datetime import datetime, timezone
            exp_time = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
            if time.time() > exp_time:
                return self._build_verdict(
                    request, "DENY", "REQUEST_EXPIRED",
                    f"Execution request expired at {expiry_str}",
                    t0
                )
        except Exception:
            return self._build_verdict(
                request, "DENY", "INVALID_TIMESTAMP",
                "Unparseable ISO-8601 expiry timestamp",
                t0
            )

        expected_hash = compute_arg_hash(payload)
        if arg_hash != expected_hash:
            return self._build_verdict(
                request, "DENY", "ARGUMENT_HASH_MISMATCH",
                f"Payload arg_hash '{arg_hash}' does not match computed '{expected_hash}'",
                t0
            )

        if action in self.disallowed_companion_paths:
            return self._build_verdict(
                request, "DENY", "DISALLOWED_EXECUTION_PATH",
                f"Execution path '{action}' is strictly forbidden on drone companion interface.",
                t0
            )

        if principal not in self.trusted_keystore:
            return self._build_verdict(
                request, "DENY", "UNKNOWN_UNTRUSTED_PRINCIPAL",
                f"Principal '{principal}' is not recognized in authoritative trust keystore.",
                t0
            )

        auth_pubkey_hex = self.trusted_keystore[principal]
        prov_ref = provenance.get("provenance_ref")
        prov_data = provenance.get("data")

        if not prov_data:
            return self._build_verdict(
                request, "DENY", "PROVENANCE_FORGERY_OR_INVALID",
                "Missing structured provenance data or bare self-assertion rejected.",
                t0
            )

        sig_hex = prov_data.get("signature")
        c_type = prov_data.get("credential_type")
        v_status = prov_data.get("verification_status")
        prov_principal = prov_data.get("principal_id")

        if prov_principal != principal:
            return self._build_verdict(
                request, "DENY", "PRINCIPAL_ATTRIBUTION_MISMATCH",
                f"Requesting principal '{principal}' does not match provenance principal '{prov_principal}'",
                t0
            )

        if not sig_hex or c_type == "NONE" or v_status in ["FORGED", "MISSING", "STALE"]:
            return self._build_verdict(
                request, "DENY", "PROVENANCE_FORGERY_OR_INVALID",
                f"Unsigned request, invalid credential type, or flagged status '{v_status}'.",
                t0
            )

        if capability in self.revoked_capabilities or req_id in self.revoked_capabilities:
            return self._build_verdict(
                request, "DENY", "CAPABILITY_REVOKED",
                f"Capability '{capability}' or request '{req_id}' has been revoked",
                t0
            )

        is_sig_valid = verify_execution_signature(request, sig_hex, auth_pubkey_hex)
        if not is_sig_valid:
            return self._build_verdict(
                request, "DENY", "CRYPTOGRAPHIC_SIGNATURE_INVALID",
                f"Ed25519 signature verification failed against authoritative public key for principal '{principal}'.",
                t0
            )

        required_cap = self.action_capability_map.get(action)
        granted_caps = self.capability_grant_store.get(principal, set())
        if required_cap not in granted_caps:
            return self._build_verdict(
                request, "DENY", "UNAUTHORIZED_CAPABILITY",
                f"Principal '{principal}' has not been granted required capability '{required_cap}' in server grant store.",
                t0
            )

        if capability != required_cap:
            return self._build_verdict(
                request, "DENY", "UNAUTHORIZED_CAPABILITY",
                f"Action '{action}' requires capability '{required_cap}', but '{capability}' was held",
                t0
            )

        if not runtime_posture_ref or runtime_posture_ref not in self.known_postures:
            return self._build_verdict(
                request, "DENY", "UNTRUSTED_POSTURE_REFERENCE",
                f"Runtime posture reference '{runtime_posture_ref}' not found in external authoritative store.",
                t0
            )

        external_posture_obj = self.known_postures[runtime_posture_ref]
        current_posture = external_posture_obj.get("posture")

        if current_posture in ["GPS_UNTRUSTED", "NAVIGATION_UNAVAILABLE"]:
            if action in ["SET_WAYPOINT", "MISSION_UPLOAD"]:
                return self._build_verdict(
                    request, "DENY", "POSTURE_DEGRADATION_DENIAL",
                    f"Action '{action}' denied because external posture is {current_posture}.",
                    t0
                )
        elif current_posture == "GPS_DEGRADED":
            if action == "MISSION_UPLOAD":
                return self._build_verdict(
                    request, "DENY", "POSTURE_DEGRADATION_DENIAL",
                    f"Action '{action}' denied in GPS_DEGRADED mode (restricted navigation only).",
                    t0
                )

        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
        verdict_res = {
            "verdict": "ALLOW",
            "reason": "POLICY_AUTHORIZED",
            "pdp_authorized": True,
            "latency_us": elapsed_us,
            "request_id": req_id,
            "principal": principal,
            "action": action,
            "runtime_posture": current_posture,
            "arg_hash": arg_hash,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.audit_log.append(verdict_res)
        return verdict_res

    def _build_verdict(
        self,
        request: Dict[str, Any],
        verdict: str,
        reason_code: str,
        description: str,
        start_ns: int
    ) -> Dict[str, Any]:
        elapsed_us = (time.perf_counter_ns() - start_ns) / 1000.0
        rec = {
            "verdict": verdict,
            "reason": reason_code,
            "description": description,
            "execution_status": "NOT_EXECUTED",
            "physical_effect": "No actuator command reaches actuator bus",
            "latency_us": elapsed_us,
            "request_id": request.get("request_id", ""),
            "principal": request.get("principal", ""),
            "action": request.get("action", ""),
            "runtime_posture": request.get("runtime_posture", {}).get("posture_ref", "UNKNOWN"),
            "arg_hash": request.get("arg_hash", ""),
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.audit_log.append(rec)
        return rec
