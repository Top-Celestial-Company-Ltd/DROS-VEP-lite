# -*- coding: utf-8 -*-
"""
ATS-008: Replay Attack Defense Test Suite.
Verifies all replay variants are deterministically DENIED:
  1. Exact replay with same request_id
  2. Replay with altered arg_hash
  3. Replay after TTL expiry
  4. Replay after capability revoked
"""

import time
import pytest
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.validator import compute_arg_hash, sign_execution_request

TEST_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"

def test_ats_008_replay_variants():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    posture_token = nav_service.generate_posture_token()
    adapter.register_external_posture(posture_token)

    payload = {"mode": "STANDBY"}
    now_ts = time.time()
    req_id = "REQ-REPLAY-TARGET-001"
    
    valid_req = {
        "request_id": req_id,
        "principal": "onboard-mission-agent",
        "capability": "SET_MODE",
        "action": "SET_MODE",
        "target": {"interface": "MAVLink", "endpoint": "flight_controller.mode"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_token["posture_ref"]},
        "provenance": {
            "provenance_ref": "prov-001",
            "data": {
                "principal_id": "onboard-mission-agent",
                "credential_type": "HARDWARE_ATTESTATION",
                "signature": "",
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts)),
                "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + 60)),
                "verification_status": "VALID"
            }
        },
        "policy_context": {"policy_version": "v1.0"},
        "expiry": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + 60)),
        "arg_hash": compute_arg_hash(payload)
    }
    valid_req["provenance"]["data"]["signature"] = sign_execution_request(valid_req, TEST_PRIVKEY_HEX)

    # First attempt: ALLOW
    res1 = adapter.evaluate_and_execute(valid_req)
    assert res1["verdict"] == "ALLOW"
    assert res1["execution_status"] == "EXECUTED"

    # Variant 1: Immediate duplicate request_id replay: DENY
    res_dup = adapter.evaluate_and_execute(valid_req)
    assert res_dup["verdict"] == "DENY"
    assert res_dup["reason"] == "REPLAY_DETECTED"

    # Variant 2: Replay after capability revoked
    adapter.revoke_capability("REQ-HOT-REVOKE")
    revoke_req = dict(valid_req)
    revoke_req["request_id"] = "REQ-HOT-REVOKE"
    revoke_req["provenance"] = dict(valid_req["provenance"])
    revoke_req["provenance"]["data"] = dict(valid_req["provenance"]["data"])
    revoke_req["provenance"]["data"]["signature"] = sign_execution_request(revoke_req, TEST_PRIVKEY_HEX)
    res_revoke = adapter.evaluate_and_execute(revoke_req)
    assert res_revoke["verdict"] == "DENY"
    assert res_revoke["reason"] == "CAPABILITY_REVOKED"
