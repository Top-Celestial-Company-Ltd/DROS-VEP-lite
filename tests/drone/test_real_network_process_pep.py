# -*- coding: utf-8 -*-
"""
Real OS Process & Network Level Verification Suite.
Spawns independent OS processes:
  1. Real MAVLink Server process on UDP 127.0.0.1:14550
  2. DROS PEP Proxy process on UDP 127.0.0.1:14540
Executes real network injections and process termination:
  - Ticket-02: Cryptographic Identity Attestation via Ed25519 (Rejects forged/untrusted signatures)
  - Ticket-01: Server-Side Capability Grant Store (Rejects ungranted action requests even if declared in request)
  - Ticket-03: Semantically-consistent binary MAVLink compilation (Downstream FC decodes SET_MODE instead of BAD_DATA)
  - Ticket-04: Raw Native Binary MAVLink Packet Injection (Direct unmediated wire bytes blocked)
  - Fault Injection: Hard kill of PEP process (SIGKILL) enforces fail-closed network isolation.
"""

import socket
import subprocess
import time
import os
import sys
import json
import pytest
from pymavlink import mavutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
DRONE_DIR = os.path.join(BASE_DIR, "drone")

from drone.validator import compute_arg_hash, sign_execution_request
from drone.sitl.engine import ExternalNavigationIntegrityService

# Authoritative pre-registered Ed25519 identity keypairs
# 1. agent.mission.planner
PLANNER_PRIVKEY_HEX = "15496b240763c8b70795633c9f50c40272223999db094cb36c36d5ef4b488152"
PLANNER_PUBKEY_HEX = "14fcfd4a2713f2e23d1899cfb69d7a57e391410be74c7372b079597f0c3ab82f"

# 2. onboard-mission-agent
ONBOARD_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"
ONBOARD_PUBKEY_HEX = "8d9214cb7f1262fb1c27e6d5fee11130ba8b21817536b076989f29e2ab0f12f9"

@pytest.fixture(scope="module")
def real_network_env():
    # 1. Start real MAVLink server on 14550
    server_script = os.path.join(DRONE_DIR, "mavlink_server.py")
    proxy_script = os.path.join(DRONE_DIR, "pep_proxy.py")
    
    server_proc = subprocess.Popen([sys.executable, server_script])
    proxy_proc = subprocess.Popen([sys.executable, proxy_script])
    time.sleep(1.5) # allow sockets to bind
    
    yield server_proc, proxy_proc
    
    # Cleanup
    for p in [proxy_proc, server_proc]:
        try:
            p.terminate()
            p.wait(timeout=1.0)
        except Exception:
            p.kill()

def build_signed_request(
    action="SET_MODE",
    capability="SET_MODE",
    principal="agent.mission.planner",
    privkey_hex=PLANNER_PRIVKEY_HEX,
    nonce=None,
    payload=None,
    expiry=None
):
    posture_path = os.path.join(DRONE_DIR, "active_posture.json")
    if os.path.exists(posture_path):
        with open(posture_path, "r", encoding="utf-8") as pf:
            posture_token = json.load(pf)
    else:
        nav_service = ExternalNavigationIntegrityService()
        posture_token = nav_service.generate_posture_token()

    if payload is None:
        payload = {"custom_mode": 4} # AUTO mode
    if nonce is None:
        nonce = f"net-req-{time.time_ns()}"
    if expiry is None:
        expiry = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 300))

    arg_hash = compute_arg_hash(payload)
    
    req = {
        "request_id": nonce,
        "principal": principal,
        "capability": capability,
        "action": action,
        "target": {"interface": "flight_controller.actuator_bus", "endpoint": "udp://127.0.0.1:14550"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_token["posture_ref"]},
        "provenance": {
            "provenance_ref": "prov-claim-auth-99",
            "data": {
                "principal_id": principal,
                "credential_type": "HARDWARE_ATTESTATION",
                "signature": "", # populated below
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "expires_at": expiry,
                "verification_status": "VALID"
            }
        },
        "policy_context": {"version": "v0.3"},
        "expiry": expiry,
        "arg_hash": arg_hash
    }

    if privkey_hex:
        # Physically compute real Ed25519 signature
        sig_hex = sign_execution_request(req, privkey_hex)
        req["provenance"]["data"]["signature"] = sig_hex
    else:
        req["provenance"]["data"]["signature"] = "0" * 128

    return req

def test_real_network_authorized_request_forwarded_and_decoded(real_network_env):
    """
    Test 1: Valid, hash-consistent, Ed25519-signed request is ALLOWED by DROS.
    Ticket-03 Proof: FC downstream receives and successfully decodes a real binary MAVLink message (SET_MODE),
    NOT a BAD_DATA error!
    """
    # Reset fc_audit.log
    fc_log = os.path.join(DRONE_DIR, "fc_audit.log")
    with open(fc_log, "w", encoding="utf-8") as f:
        f.write("PX4_REAL_SOCKET_STARTED\n")

    req = build_signed_request(action="SET_MODE", capability="SET_MODE")
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    # 1. PEP Log verification
    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "FORWARDED:" in pep_content
    assert "POLICY_AUTHORIZED" in pep_content

    # 2. FC Log verification: Downstream MUST decode SET_MODE
    with open(fc_log, "r", encoding="utf-8") as f:
        fc_content = f.read()
    assert "SET_MODE" in fc_content
    assert "BAD_DATA" not in fc_content

def test_real_network_ticket02_forged_cryptographic_signature_blocked(real_network_env):
    """
    Test 2 (Ticket-02 Proof): Attacker provides valid format but fake Ed25519 signature.
    DROS physical cryptography verification fails -> DENY with CRYPTOGRAPHIC_SIGNATURE_INVALID.
    """
    req = build_signed_request()
    # Attack: tamper signature bytes with invalid random hex
    req["provenance"]["data"]["signature"] = "deadbeef" * 16
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "CRYPTOGRAPHIC_SIGNATURE_INVALID" in pep_content

def test_real_network_ticket02_unknown_principal_blocked(real_network_env):
    """
    Test 3 (Ticket-02 Proof): Rogue principal not present in authoritative Server Keystore.
    DROS rejects unknown principal -> DENY with UNKNOWN_UNTRUSTED_PRINCIPAL.
    """
    req = build_signed_request(principal="rogue.external.agent")
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "UNKNOWN_UNTRUSTED_PRINCIPAL" in pep_content

def test_real_network_ticket01_server_grant_store_escalation_blocked(real_network_env):
    """
    Test 4 (Ticket-01 Proof): Attacker signs request with valid Ed25519 key and declares capability='ARM',
    matching action='ARM'. However, Server Capability Grant Store only granted him navigation capabilities!
    DROS rejects -> DENY with UNAUTHORIZED_CAPABILITY (server grant table check).
    """
    # agent.mission.planner only has READ/PLAN/SET_MODE/SET_WAYPOINT/TAKEOFF/LAND/RTL, NOT 'ARM'
    req = build_signed_request(
        action="ARM",
        capability="ARM", # Attacker tries to self-assert matching capability
        payload={"action_name": "ARM_MOTORS"}
    )
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "UNAUTHORIZED_CAPABILITY" in pep_content
    assert "has not been granted required capability 'ARM'" in pep_content

def test_real_network_ticket02_principal_identity_spoofing_blocked(real_network_env):
    """
    Test 4b (Question 1 Proof): Attacker holds planner's private key, signs valid request as
    'agent.mission.planner', and then mutates top-level 'principal' to 'onboard-mission-agent'
    (hoping to inherit onboard agent's ARM grant) without having onboard agent's private key.
    DROS must DENY:
      1. If signature unchanged: canonical_request_bytes includes principal -> Ed25519 verification fails
         against onboard-mission-agent's public key -> CRYPTOGRAPHIC_SIGNATURE_INVALID.
      2. If signed with planner's key for onboard principal: planner's signature does not match
         onboard's pre-registered public key -> CRYPTOGRAPHIC_SIGNATURE_INVALID.
    """
    # Build request where principal is declared as onboard-mission-agent, but signed with planner's key!
    spoofed_req = build_signed_request(
        action="ARM",
        capability="ARM",
        principal="onboard-mission-agent",
        privkey_hex=PLANNER_PRIVKEY_HEX, # ATTACK: Using planner key to sign for onboard principal!
        payload={"action_name": "ARM_MOTORS"}
    )
    raw_packet = json.dumps(spoofed_req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "CRYPTOGRAPHIC_SIGNATURE_INVALID" in pep_content

def test_real_network_ticket03_unmapped_action_translation_fail_closed(real_network_env):
    """
    Test 4c (Question 3 Proof): Attacker sends request for an action that has no binary MAVLink
    translation mapping. PEP translation layer must strictly fail closed (raise ValueError, drop packet,
    audit TRANSLATION_LAYER_FAIL_CLOSED), and FC at 14550 must NOT receive any corrupted or raw bytes.
    """
    fc_log = os.path.join(DRONE_DIR, "fc_audit.log")
    with open(fc_log, "w", encoding="utf-8") as f:
        f.write("CHECK_UNMAPPED_ACTION\n")

    # Construct request with action that has no MAVLink compilation mapping
    # e.g., an experimental action not in compile_action_to_mavlink_frame
    req = build_signed_request(action="SET_WAYPOINT", capability="SET_WAYPOINT")
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    # 1. PEP Log must show translation fail-closed
    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "TRANSLATION_LAYER_FAIL_CLOSED" in pep_content

    # 2. FC Log must remain intact and empty of any bad packets
    with open(fc_log, "r", encoding="utf-8") as f:
        fc_content = f.read()
    assert "SET_WAYPOINT" not in fc_content
    assert "BAD_DATA" not in fc_content

def test_real_network_ticket04_native_binary_mavlink_attack_blocked(real_network_env):
    """
    Test 5 (Ticket-04 Proof): Attacker sends a REAL RAW BINARY MAVLink ARM command frame
    (COMMAND_LONG, param1=1) directly to UDP 14540.
    PEP decodes raw frame, identifies unauthenticated raw command, synthesizes untrusted ExecutionRequest,
    and drops packet -> DENY with PROVENANCE_FORGERY_OR_INVALID / UNTRUSTED_PRINCIPAL.
    Downstream FC at 14550 NEVER receives the malicious ARM packet.
    """
    fc_log = os.path.join(DRONE_DIR, "fc_audit.log")
    with open(fc_log, "w", encoding="utf-8") as f:
        f.write("CHECK_RAW_MAVLINK_ARM\n")

    # Construct genuine binary MAVLink COMMAND_LONG frame using pymavlink
    mav = mavutil.mavlink.MAVLink(None)
    msg = mav.command_long_encode(
        1, 1, 400, 0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    )
    raw_mavlink_packet = msg.pack(mav)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_mavlink_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    # 1. PEP Log must show blocked
    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "BLOCKED:" in pep_content

    # 2. FC Log must NOT contain COMMAND_LONG
    with open(fc_log, "r", encoding="utf-8") as f:
        fc_content = f.read()
    assert "COMMAND_LONG" not in fc_content

def test_real_network_tampered_hash_attack_blocked(real_network_env):
    """Test 6: Attack packet with modified payload/tampered hash is DENIED (ARG_HASH_MISMATCH)."""
    req = build_signed_request()
    req["payload"] = {"custom_mode": 999, "malicious_injection": True}
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "ARG_HASH_MISMATCH" in pep_content

def test_real_network_expired_ttl_attack_blocked(real_network_env):
    """Test 7: Expired command packet is DENIED (REQUEST_EXPIRED)."""
    req = build_signed_request(expiry="2020-01-01T00:00:00Z")
    raw_packet = json.dumps(req).encode("utf-8")

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(raw_packet, ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "REQUEST_EXPIRED" in pep_content

def test_real_network_unparseable_raw_noise_blocked(real_network_env):
    """Test 8: Raw unparseable byte fuzzing is DENIED by default without crashing PEP."""
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(b"\xde\xad\xbe\xef\x00\xff\xfeRANDOM_FUZZING_BYTES", ("127.0.0.1", 14540))
    time.sleep(0.5)

    pep_log = os.path.join(DRONE_DIR, "pep_audit.log")
    with open(pep_log, "r", encoding="utf-8") as f:
        pep_content = f.read()
    assert "MALFORMED_UNPARSEABLE_WIRE_BYTES" in pep_content

def test_real_process_kill_fail_closed(real_network_env):
    """Test 9: Physical architecture proof - PEP process killed (SIGKILL) leads to fail-closed state."""
    server_proc, proxy_proc = real_network_env
    
    # Kill PEP process hard
    proxy_proc.kill()
    proxy_proc.wait(timeout=2.0)
    
    # Try sending after crash
    req = build_signed_request()
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(req).encode("utf-8"), ("127.0.0.1", 14540))
    time.sleep(0.5)
    
    fc_log = os.path.join(DRONE_DIR, "fc_audit.log")
    with open(fc_log, "r", encoding="utf-8") as f:
        fc_content = f.read()
    assert req["request_id"] not in fc_content
