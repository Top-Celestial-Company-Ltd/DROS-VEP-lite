# -*- coding: utf-8 -*-
"""
ATS-009: Provenance Forgery Defense Test Suite.
Verifies that bare self-assertions, forged signatures, or expired credentials are denied.
"""

import time
import pytest
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.validator import compute_arg_hash

def test_ats_009_provenance_enforcement():
    sitl = PX4SITLEngine()
    nav_service = ExternalNavigationIntegrityService()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    posture_token = nav_service.generate_posture_token()
    adapter.register_external_posture(posture_token)

    payload = {"altitude": 10.0}
    now_ts = time.time()
    
    # 1. Bare self-assertion: DENY
    req_bare = {
        "request_id": "REQ-PROV-BARE",
        "principal": "onboard-mission-agent",
        "capability": "TAKEOFF",
        "action": "TAKEOFF",
        "target": {"interface": "MAVLink"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_token["posture_ref"]},
        "provenance": {"provenance_ref": "self-asserted-i-am-trusted"},
        "policy_context": {"policy_version": "v1.0"},
        "expiry": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + 60)),
        "arg_hash": compute_arg_hash(payload)
    }
    res_bare = adapter.evaluate_and_execute(req_bare)
    assert res_bare["verdict"] == "DENY"
    assert res_bare["reason"] == "PROVENANCE_FORGERY_OR_INVALID"

    # 2. Forged signature: DENY
    req_forged = dict(req_bare)
    req_forged["request_id"] = "REQ-PROV-FORGED"
    req_forged["provenance"] = {
        "provenance_ref": "prov-forged",
        "data": {
            "principal_id": "onboard-mission-agent",
            "credential_type": "HARDWARE_ATTESTATION",
            "signature": "deadbeef" * 16, # Invalid signature
            "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts)),
            "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_ts + 60)),
            "verification_status": "VALID" # Even if attacker declares VALID, crypto verification catches it!
        }
    }
    res_forged = adapter.evaluate_and_execute(req_forged)
    assert res_forged["verdict"] == "DENY"
    assert res_forged["reason"] == "CRYPTOGRAPHIC_SIGNATURE_INVALID"
