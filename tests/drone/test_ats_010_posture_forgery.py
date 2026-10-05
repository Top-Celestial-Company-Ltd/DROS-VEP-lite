# -*- coding: utf-8 -*-
"""
ATS-010: Runtime Posture Forgery Defense Test Suite.
Verifies that agent self-asserted or unregistered postures are rejected.
"""

import time
import pytest
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.validator import compute_arg_hash, sign_execution_request

TEST_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"

def test_ats_010_posture_forgery_rejection():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)

    # External actual posture is UNTRUSTED
    nav_service.set_posture("GPS_UNTRUSTED", trust_level="UNTRUSTED")
    token_untrusted = nav_service.generate_posture_token()
    adapter.register_external_posture(token_untrusted)

    payload = {"altitude": 15.0}
    now_ts = time.time()
    
    # 1. Agent invents its own unregistered posture ref: DENY
    req_self_assert = {
        "request_id": "REQ-POSTURE-FAKE-01",
        "principal": "onboard-mission-agent",
        "capability": "TAKEOFF",
        "action": "TAKEOFF",
        "target": {"interface": "MAVLink"},
        "payload": payload,
        "runtime_posture": {"posture_ref": "agent-crafted-fake-posture-trusted"},
        "provenance": {
            "provenance_ref": "prov-valid",
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
    req_self_assert["provenance"]["data"]["signature"] = sign_execution_request(req_self_assert, TEST_PRIVKEY_HEX)

    res = adapter.evaluate_and_execute(req_self_assert)
    assert res["verdict"] == "DENY"
    assert res["reason"] == "UNTRUSTED_POSTURE_REFERENCE"
