# -*- coding: utf-8 -*-
"""
T4 / T5 / T8 Verification Test Suite.
T4: Path mediation & bypass enumeration.
T5: Fail-closed & safe degradation behavior.
T8: Deterministic replay of execution requests.
"""

import os
import json
import time
import pytest
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.validator import compute_arg_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_t4_execution_path_inventory_consistency():
    path_inv_file = os.path.join(BASE_DIR, "DRONE_EXECUTION_PATH_INVENTORY.json")
    with open(path_inv_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    paths = {p["path_id"]: p for p in data["paths"]}
    
    assert "PATH-MAVLINK" in paths
    assert "PATH-SHELL" in paths
    assert "PATH-UXRCE-DDS" in paths

def test_t5_01_pdp_timeout_fail_closed():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    token = nav_service.generate_posture_token()
    adapter.register_external_posture(token)

    # Induce PDP timeout
    adapter.trigger_pdp_timeout()

    req = {
        "request_id": "REQ-PDP-TIMEOUT-01",
        "principal": "agent-1",
        "capability": "TAKEOFF",
        "action": "TAKEOFF",
        "target": {"interface": "MAVLink"},
        "payload": {"altitude": 10.0},
        "runtime_posture": {"posture_ref": token["posture_ref"]},
        "provenance": {"provenance_ref": "prov-valid", "data": {"principal_id": "agent-1", "credential_type": "HARDWARE_ATTESTATION", "signature": "s", "issued_at": "2026-09-24T00:00:00Z", "expires_at": "2026-09-25T00:00:00Z", "verification_status": "VALID"}},
        "policy_context": {"policy_version": "v1.0"},
        "expiry": "2026-09-25T00:00:00Z",
        "arg_hash": compute_arg_hash({"altitude": 10.0})
    }

    res = adapter.evaluate_and_execute(req)
    assert res["verdict"] == "DENY"
    assert res["reason"] == "PDP_TIMEOUT_FAIL_CLOSED"
    assert res["execution_status"] == "NOT_EXECUTED"
    assert sitl.armed is False

def test_t5_02_pep_crash_fail_closed():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    token = nav_service.generate_posture_token()
    adapter.register_external_posture(token)

    # Induce PEP crash
    adapter.trigger_pep_crash()

    req = {
        "request_id": "REQ-PEP-CRASH-01",
        "principal": "agent-1",
        "capability": "ARM",
        "action": "ARM",
        "target": {"interface": "MAVLink"},
        "payload": {"action": "ARM"},
        "runtime_posture": {"posture_ref": token["posture_ref"]},
        "provenance": {"provenance_ref": "prov-valid", "data": {"principal_id": "agent-1", "credential_type": "HARDWARE_ATTESTATION", "signature": "s", "issued_at": "2026-09-24T00:00:00Z", "expires_at": "2026-09-25T00:00:00Z", "verification_status": "VALID"}},
        "policy_context": {"policy_version": "v1.0"},
        "expiry": "2026-09-25T00:00:00Z",
        "arg_hash": compute_arg_hash({"action": "ARM"})
    }

    res = adapter.evaluate_and_execute(req)
    assert res["verdict"] == "DENY"
    assert res["reason"] == "PEP_CRASH_FAIL_CLOSED"
    assert res["execution_status"] == "NOT_EXECUTED"
    assert sitl.armed is False

def test_t5_03_malformed_input_fail_closed():
    sitl = PX4SITLEngine()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    
    # Missing all authorization context
    res = adapter.evaluate_and_execute({})
    assert res["verdict"] == "DENY"
    assert res["execution_status"] == "NOT_EXECUTED"
    assert sitl.armed is False

def test_t8_deterministic_replay():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter1 = DroneExecutionAdapter(sitl_engine=sitl)
    adapter2 = DroneExecutionAdapter(sitl_engine=PX4SITLEngine())

    token = nav_service.generate_posture_token()
    adapter1.register_external_posture(token)
    adapter2.register_external_posture(token)

    from drone.validator import sign_execution_request
    privkey = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"
    principal = "onboard-mission-agent"

    payload = {"mode": "STANDBY"}
    req = {
        "request_id": "REQ-DET-REPLAY-1",
        "principal": principal,
        "capability": "SET_MODE",
        "action": "SET_MODE",
        "target": {"interface": "MAVLink"},
        "payload": payload,
        "runtime_posture": {"posture_ref": token["posture_ref"]},
        "provenance": {
            "provenance_ref": "prov-1",
            "data": {
                "principal_id": principal,
                "credential_type": "HARDWARE_ATTESTATION",
                "signature": "",
                "issued_at": "2026-09-24T00:00:00Z",
                "expires_at": "2026-09-25T00:00:00Z",
                "verification_status": "VALID"
            }
        },
        "policy_context": {"policy_version": "v1.0"},
        "expiry": "2026-09-25T00:00:00Z",
        "arg_hash": compute_arg_hash(payload)
    }
    req["provenance"]["data"]["signature"] = sign_execution_request(req, privkey)

    res1 = adapter1.evaluate_and_execute(req)
    res2 = adapter2.evaluate_and_execute(req)

    # Identical immutable input must yield identical verdict & reason
    assert res1["verdict"] == res2["verdict"] == "ALLOW"
    assert res1["reason"] == res2["reason"] == "POLICY_AUTHORIZED"
    assert res1["execution_status"] == res2["execution_status"] == "EXECUTED"
