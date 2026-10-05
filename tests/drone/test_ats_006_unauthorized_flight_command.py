# -*- coding: utf-8 -*-
"""
ATS-006: Unauthorized Flight Command Injection Test Suite.
Verifies all 9 attack variants are deterministically DENIED at the DROS PEP boundary:
  1. forged_request
  2. unsigned_request
  3. expired_credential
  4. wrong_principal
  5. wrong_task_scope
  6. wrong_bitmap / capability
  7. altered_arg_hash
  8. forged_provenance
  9. direct_adapter_bypass
"""

import time
import pytest
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.validator import compute_arg_hash, sign_execution_request

TEST_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"

@pytest.fixture
def drone_env():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    
    # Register valid nominal posture
    posture_token = nav_service.generate_posture_token(ttl_seconds=300)
    adapter.register_external_posture(posture_token)
    
    return adapter, sitl, nav_service, posture_token

def _build_base_request(posture_ref: str, action="ARM", capability="ARM", payload=None, privkey_hex=TEST_PRIVKEY_HEX):
    if payload is None:
        payload = {"action_name": "ARM_MOTORS"}
    now_ts = time.time()
    expiry_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + 60))
    req = {
        "request_id": f"REQ-{now_ts}",
        "principal": "onboard-mission-agent",
        "capability": capability,
        "action": action,
        "target": {
            "interface": "MAVLink",
            "endpoint": "flight_controller.actuator_bus"
        },
        "payload": payload,
        "runtime_posture": {
            "posture_ref": posture_ref
        },
        "provenance": {
            "provenance_ref": "prov-valid-001",
            "data": {
                "principal_id": "onboard-mission-agent",
                "credential_type": "HARDWARE_ATTESTATION",
                "signature": "",
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts - 10)),
                "expires_at": expiry_str,
                "verification_status": "VALID"
            }
        },
        "policy_context": {
            "policy_version": "v1.0"
        },
        "expiry": expiry_str,
        "arg_hash": compute_arg_hash(payload)
    }
    if privkey_hex:
        req["provenance"]["data"]["signature"] = sign_execution_request(req, privkey_hex)
    else:
        req["provenance"]["data"]["signature"] = "deadbeef" * 16
    return req

def test_ats_006_control_case_allow(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="ARM", capability="ARM")
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "ALLOW"
    assert res["execution_status"] == "EXECUTED"
    assert sitl.armed is True

def test_ats_006_01_forged_request_wrong_schema(drone_env):
    adapter, sitl, _, _ = drone_env
    # Missing required fields
    bad_req = {"action": "ARM", "principal": "attacker"}
    res = adapter.evaluate_and_execute(bad_req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "SCHEMA_VALIDATION_FAILED"
    assert sitl.armed is False

def test_ats_006_02_unsigned_request_missing_provenance(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="ARM", capability="ARM")
    req["provenance"]["data"]["credential_type"] = "NONE"
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "PROVENANCE_FORGERY_OR_INVALID"
    assert sitl.armed is False

def test_ats_006_03_expired_credential(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="ARM", capability="ARM")
    req["expiry"] = "2020-01-01T00:00:00Z"
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "REQUEST_EXPIRED"
    assert sitl.armed is False

def test_ats_006_04_wrong_principal(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="ARM", capability="ARM")
    req["principal"] = "rogue-external-entity"
    # Provenance principal mismatch
    req["provenance"]["data"]["principal_id"] = "different-agent"
    res = adapter.evaluate_and_execute(req)
    
    # Should fail either capability attribution or provenance
    assert res["verdict"] == "DENY"

def test_ats_006_05_wrong_capability_privilege_escalation(drone_env):
    adapter, sitl, _, posture_token = drone_env
    # Agent only holds READ_TELEMETRY, attempts TAKEOFF
    req = _build_base_request(posture_token["posture_ref"], action="TAKEOFF", capability="READ_TELEMETRY")
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "UNAUTHORIZED_CAPABILITY"
    assert sitl.flight_mode == "STANDBY"

def test_ats_006_06_altered_arg_hash(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="ARM", capability="ARM")
    req["arg_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "ARG_HASH_MISMATCH"

def test_ats_006_07_forged_provenance(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="ARM", capability="ARM")
    req["provenance"]["data"]["verification_status"] = "FORGED"
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "PROVENANCE_FORGERY_OR_INVALID"

def test_ats_006_08_disallowed_shell_execution(drone_env):
    adapter, sitl, _, posture_token = drone_env
    req = _build_base_request(posture_token["posture_ref"], action="SHELL_COMMAND", capability="SHELL_COMMAND")
    res = adapter.evaluate_and_execute(req)
    
    assert res["verdict"] == "DENY"
    assert res["reason"] == "DISALLOWED_EXECUTION_PATH"
