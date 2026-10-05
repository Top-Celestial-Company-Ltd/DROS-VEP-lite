# -*- coding: utf-8 -*-
"""
M1.1-S1 Test Suite: End-to-End Governance over Real C++ PX4 SITL.
Physical Execution Path: Client -> DROS PEP (14540) -> Downstream Tap (14588) -> Real PX4 SITL (14580)
Verifies:
  1. S1-A (Authorized): Valid request forwarded to real PX4 SITL binary.
  2. S1-B (Unauthorized): Forged / unauthenticated requests drop immediately; 0 bytes reach downstream.
  3. S1-C (PEP Termination): OS SIGKILL of PEP closes path; 0 bytes reach downstream.
"""
import socket
import subprocess
import time
import os
import sys
import json
import threading
import pytest
from pymavlink import mavutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from drone.validator import compute_arg_hash, sign_execution_request

PX4_DIR = "/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default"
PX4_BIN = f"{PX4_DIR}/bin/px4"
PX4_ETC = f"{PX4_DIR}/etc"

DRONE_DIR = os.path.join(BASE_DIR, "drone")
PEP_SCRIPT = os.path.join(DRONE_DIR, "pep_proxy.py")
PEP_LOG = os.path.join(DRONE_DIR, "pep_audit.log")
POSTURE_FILE = os.path.join(DRONE_DIR, "active_posture.json")

TAP_PORT = 14588
PX4_PORT = 14580
PEP_PORT = 14540

# TEST-ONLY / NON-PRODUCTION Cryptographic Fixtures (Ticket-02)
# Explicitly scoped to VEP testing; NOT for production deployments.
TEST_FIXTURE_ONBOARD_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"
TEST_FIXTURE_ONBOARD_PUBKEY_HEX = "8d9214cb7f1262fb1c27e6d5fee11130ba8b21817536b076989f29e2ab0f12f9"
TEST_FIXTURE_PLANNER_PRIVKEY_HEX = "15496b240763c8b70795633c9f50c40272223999db094cb36c36d5ef4b488152"

class DownstreamTap:
    """
    Instrumented downstream observation point (UDP Tap on 14588).
    Captures byte-level frames emitted by DROS PEP on the downstream path
    and forwards them to the real PX4 SITL autopilot (14580).
    """
    def __init__(self, tap_port=TAP_PORT, fwd_port=PX4_PORT):
        self.tap_port = tap_port
        self.fwd_port = fwd_port
        self.packets = []
        self.running = False
        self.thread = None
        self.sock = None
        self.fwd = None

    def start(self):
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.tap_port))
        self.sock.settimeout(0.5)
        self.fwd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        mav = mavutil.mavlink.MAVLink(None)
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
                msgs = mav.parse_buffer(data)
                msg_name = "UNKNOWN"
                if msgs:
                    msg_name = msgs[0].get_type()
                self.packets.append({
                    "time": time.time(),
                    "len": len(data),
                    "type": msg_name,
                    "raw": data
                })
                # Forward to actual PX4 SITL binary
                self.fwd.sendto(data, ("127.0.0.1", self.fwd_port))
            except socket.timeout:
                continue
            except Exception:
                pass

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.sock:
            self.sock.close()
        if self.fwd:
            self.fwd.close()

def get_log_offset(log_file: str) -> int:
    """Returns current byte offset of log file for per-test isolation."""
    if os.path.exists(log_file):
        return os.path.getsize(log_file)
    return 0

def read_log_delta(log_file: str, offset: int) -> str:
    """Reads only new content appended to log file after offset."""
    if not os.path.exists(log_file):
        return ""
    with open(log_file, "r", encoding="utf-8") as f:
        f.seek(offset)
        return f.read()

@pytest.fixture(scope="module")
def s1_test_environment():
    # 1. Start Instrumented Downstream Tap
    tap = DownstreamTap()
    tap.start()

    # 2. Start PX4 SITL C++ binary
    px4_proc = subprocess.Popen(
        [PX4_BIN, "-d", PX4_ETC],
        cwd=PX4_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2.5)

    # 3. Start DROS PEP Proxy targeting the tap
    env = os.environ.copy()
    env["DROS_FC_PORT"] = str(TAP_PORT)
    pep_proc = subprocess.Popen(
        [sys.executable, PEP_SCRIPT],
        env=env
    )
    time.sleep(2.0)

    yield tap, px4_proc, pep_proc

    # Teardown
    tap.stop()
    for p in [pep_proc, px4_proc]:
        try:
            p.terminate()
            p.wait(timeout=2.0)
        except Exception:
            p.kill()

def build_valid_signed_arm_request(req_id=None):
    with open(POSTURE_FILE, "r", encoding="utf-8") as f:
        posture_token = json.load(f)
    payload = {"action_name": "ARM_MOTORS"}
    expiry = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 300))
    if req_id is None:
        req_id = f"s1-req-{time.time_ns()}"
    req = {
        "request_id": req_id,
        "principal": "onboard-mission-agent",
        "capability": "ARM",
        "action": "ARM",
        "target": {"interface": "flight_controller.actuator_bus", "endpoint": f"udp://127.0.0.1:{TAP_PORT}"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_token["posture_ref"]},
        "provenance": {
            "provenance_ref": "prov-claim-auth-99",
            "data": {
                "principal_id": "onboard-mission-agent",
                "credential_type": "HARDWARE_ATTESTATION",
                "signature": "",
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "expires_at": expiry,
                "verification_status": "VALID"
            }
        },
        "policy_context": {"version": "v0.3"},
        "expiry": expiry,
        "arg_hash": compute_arg_hash(payload)
    }
    req["provenance"]["data"]["signature"] = sign_execution_request(req, TEST_FIXTURE_ONBOARD_PRIVKEY_HEX)
    return req

def test_s1_a_authorized_request_observed_at_downstream_tap(s1_test_environment):
    """
    S1-A: Authorized execution request produces the expected binary MAVLink COMMAND_LONG frame
    observed at the instrumented downstream observation point (UDP 14588 Tap).
    """
    tap, px4_proc, pep_proc = s1_test_environment
    tap.packets.clear()
    log_offset = get_log_offset(PEP_LOG)

    req = build_valid_signed_arm_request()
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(req).encode("utf-8"), ("127.0.0.1", PEP_PORT))
    client.close()
    time.sleep(1.0)

    # 1. Assert isolated PEP audit log recorded FORWARDED in this execution window
    new_log = read_log_delta(PEP_LOG, log_offset)
    assert "FORWARDED:" in new_log
    assert "ARM:POLICY_AUTHORIZED" in new_log

    # 2. Assert Downstream Tap observed the binary MAVLink COMMAND_LONG emitted toward PX4
    assert len(tap.packets) == 1
    delivered = tap.packets[0]
    assert delivered["type"] == "COMMAND_LONG"
    assert delivered["len"] == 41

def test_s1_b_forged_signature_zero_observed_downstream_packets(s1_test_environment):
    """
    S1-B: Forged signature is rejected and produces zero observed downstream packets
    on the tested mediated path.
    """
    tap, px4_proc, pep_proc = s1_test_environment
    tap.packets.clear()
    log_offset = get_log_offset(PEP_LOG)

    req = build_valid_signed_arm_request()
    # Attack: tamper signature
    req["provenance"]["data"]["signature"] = "deadbeef" * 16

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(req).encode("utf-8"), ("127.0.0.1", PEP_PORT))
    client.close()
    time.sleep(1.0)

    # Assert exactly 0 packets / 0 bytes observed at downstream Tap
    assert len(tap.packets) == 0

    # Assert isolated PEP audit log recorded cryptographic failure in this window
    new_log = read_log_delta(PEP_LOG, log_offset)
    assert "CRYPTOGRAPHIC_SIGNATURE_INVALID" in new_log

def test_s1_b_unauthorized_capability_zero_observed_downstream_packets(s1_test_environment):
    """
    S1-B: Unauthorized capability request is denied by DROS policy engine and produces
    zero observed downstream packets on the tested mediated path.
    """
    tap, px4_proc, pep_proc = s1_test_environment
    tap.packets.clear()
    log_offset = get_log_offset(PEP_LOG)

    with open(POSTURE_FILE, "r", encoding="utf-8") as f:
        posture_token = json.load(f)
    payload = {"action_name": "ARM_MOTORS"}
    expiry = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 300))
    req = {
        "request_id": f"s1-esc-{time.time_ns()}",
        "principal": "agent.mission.planner",
        "capability": "ARM",
        "action": "ARM",
        "target": {"interface": "flight_controller.actuator_bus", "endpoint": f"udp://127.0.0.1:{TAP_PORT}"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_token["posture_ref"]},
        "provenance": {
            "provenance_ref": "prov-claim-auth-99",
            "data": {
                "principal_id": "agent.mission.planner",
                "credential_type": "HARDWARE_ATTESTATION",
                "signature": "",
                "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "expires_at": expiry,
                "verification_status": "VALID"
            }
        },
        "policy_context": {"version": "v0.3"},
        "expiry": expiry,
        "arg_hash": compute_arg_hash(payload)
    }
    req["provenance"]["data"]["signature"] = sign_execution_request(req, TEST_FIXTURE_PLANNER_PRIVKEY_HEX)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(req).encode("utf-8"), ("127.0.0.1", PEP_PORT))
    client.close()
    time.sleep(1.0)

    # 0 downstream bytes observed
    assert len(tap.packets) == 0

    new_log = read_log_delta(PEP_LOG, log_offset)
    assert "UNAUTHORIZED_CAPABILITY" in new_log

def test_s1_b_malformed_wire_input_zero_observed_downstream_packets(s1_test_environment):
    """
    S1-B: A tested malformed/unparseable wire input is rejected and produces zero
    observed downstream packets across the tested PEP UDP 14540 ingress path.
    (Note: scoped test of malformed wire handling, not a fuzzing campaign claim.)
    """
    tap, px4_proc, pep_proc = s1_test_environment
    tap.packets.clear()
    log_offset = get_log_offset(PEP_LOG)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(b"\xde\xad\xbe\xef\x00\xff\xfeRANDOM_WIRE_ATTACK", ("127.0.0.1", PEP_PORT))
    client.close()
    time.sleep(1.0)

    # 0 downstream bytes observed
    assert len(tap.packets) == 0

    new_log = read_log_delta(PEP_LOG, log_offset)
    assert "MALFORMED_UNPARSEABLE_WIRE_BYTES" in new_log

def test_s1_c_pep_termination_zero_downstream_bytes_on_mediated_path(s1_test_environment):
    """
    S1-C: After OS-level SIGKILL of the tested PEP process, a subsequent request sent
    to the PEP ingress produced zero observed downstream bytes on the tested mediated path.
    """
    tap, px4_proc, pep_proc = s1_test_environment
    tap.packets.clear()

    # Hard kill of PEP process via OS SIGKILL
    pep_proc.kill()
    pep_proc.wait(timeout=2.0)

    # Attempt to transmit valid request to dead PEP socket
    req = build_valid_signed_arm_request()
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(req).encode("utf-8"), ("127.0.0.1", PEP_PORT))
    client.close()
    time.sleep(1.0)

    # Zero bytes delivered downstream to observation tap
    assert len(tap.packets) == 0

