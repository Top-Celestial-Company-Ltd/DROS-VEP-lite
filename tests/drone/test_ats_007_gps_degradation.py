# -*- coding: utf-8 -*-
"""
ATS-007: GPS Spoofing / Navigation Trust Degradation Test Suite.
Verifies deterministic capability restriction upon receiving external posture signals:
  - GPS_TRUSTED -> ALLOW SET_WAYPOINT
  - GPS_DEGRADED -> RESTRICT / DENY MISSION_UPLOAD
  - GPS_UNTRUSTED -> DENY SET_WAYPOINT & MISSION_UPLOAD
"""

import time
import pytest
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.validator import compute_arg_hash, sign_execution_request

TEST_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"

def _build_waypoint_request(posture_ref: str, action="SET_WAYPOINT", capability="SET_WAYPOINT"):
    payload = {"latitude": 25.0400, "longitude": 121.5700, "altitude": 20.0}
    now_ts = time.time()
    expiry_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + 60))
    req = {
        "request_id": f"REQ-WP-{now_ts}",
        "principal": "onboard-mission-agent",
        "capability": capability,
        "action": action,
        "target": {"interface": "MAVLink", "endpoint": "flight_controller.waypoint"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_ref},
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
        "policy_context": {"policy_version": "v1.0"},
        "expiry": expiry_str,
        "arg_hash": compute_arg_hash(payload)
    }
    req["provenance"]["data"]["signature"] = sign_execution_request(req, TEST_PRIVKEY_HEX)
    return req

def test_ats_007_transitions():
    sitl = PX4SITLEngine()
    sitl.armed = True # Pre-arm vehicle
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)

    # 1. State: GPS_TRUSTED -> SET_WAYPOINT should be ALLOWed
    nav_service.set_posture("GPS_TRUSTED", trust_level="HIGH")
    token_trusted = nav_service.generate_posture_token()
    adapter.register_external_posture(token_trusted)

    req_trusted = _build_waypoint_request(token_trusted["posture_ref"], action="SET_WAYPOINT")
    res1 = adapter.evaluate_and_execute(req_trusted)
    assert res1["verdict"] == "ALLOW"
    assert res1["execution_status"] == "EXECUTED"
    assert sitl.flight_mode == "MISSION"

    # 2. State: GPS_DEGRADED -> MISSION_UPLOAD should be DENIED
    nav_service.set_posture("GPS_DEGRADED", trust_level="MEDIUM")
    token_degraded = nav_service.generate_posture_token()
    adapter.register_external_posture(token_degraded)

    req_degraded = _build_waypoint_request(token_degraded["posture_ref"], action="MISSION_UPLOAD", capability="MISSION_UPLOAD")
    res2 = adapter.evaluate_and_execute(req_degraded)
    assert res2["verdict"] == "DENY"
    assert res2["reason"] == "POSTURE_DEGRADATION_DENIAL"

    # 3. State: GPS_UNTRUSTED -> SET_WAYPOINT should be DENIED
    nav_service.set_posture("GPS_UNTRUSTED", trust_level="UNTRUSTED")
    token_untrusted = nav_service.generate_posture_token()
    adapter.register_external_posture(token_untrusted)

    req_untrusted = _build_waypoint_request(token_untrusted["posture_ref"], action="SET_WAYPOINT")
    res3 = adapter.evaluate_and_execute(req_untrusted)
    assert res3["verdict"] == "DENY"
    assert res3["reason"] == "POSTURE_DEGRADATION_DENIAL"
