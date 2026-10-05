# -*- coding: utf-8 -*-
"""
Milestone M1.1-S2-E: Governance Transfer / Multi-Ingress PEP Ownership Validation.
Evaluates:
  S2-E-00: Pre-flight Socket Topology & Exclusive Ownership Verification:
           (Measures Linux socket table via ss -ulpn -H. Parses exact local address and port.
           Confirms 4 public ingresses are exclusively owned by multi_pep_proc.pid and
           backend ports are exclusively owned by px4_proc.pid.
           Emits empirical artifact: /tmp/dros_evidence_e00.json).
  S2-E-01: Unauthorized Execution Attempts Blocked Across All Ingresses:
           (Intercepted by DROS PEP; Multi-Channel Instrumented Relay records
           delta_frames == 0, delta_bytes == 0 across all ingresses.
           Emits empirical artifact: /tmp/dros_evidence_e01.json).
  S2-E-02: Authorized Forwarding & Downstream Observation Across All 4 Ingresses:
           (Validates that authorized requests on all 4 ingresses are forwarded and observed
           at the instrumented relay with matching MAVLink message types.
           Transaction-specific temporal filtering enforces len(matched) == 1.
           Avoids polluting E-04's parameter contrast pair.
           Emits empirical artifact: /tmp/dros_evidence_e02.json).
  S2-E-03: Full 4-Ingress Cryptographic Transaction Correlation:
           (Independently demonstrates 1-to-1 cryptographic ownership across ALL 4 ingresses:
            Request[id, principal, signature] -> PEP Log[FORWARDED, frame_sha256] -> Relay Observed Datagram Bytes[sha256].
            Asserts len(matched) == 1 and frame_sha256 == observed_datagram_sha256 for all 4 raw wire datagrams.
            Emits empirical artifact: /tmp/dros_evidence_e03.json).
  S2-E-04: Real State Mutation Observed After Authorized PEP Execution:
           (Clean Contrast Pair on unpolluted parameter MIS_TAKEOFF_ALT:
            Baseline read -> Raw attack fails (0 mutation) -> Authorized PEP execution succeeds (pre != post).
            Emits empirical artifact: /tmp/dros_evidence_e04.json).
  S2-E-05: Multi-Ingress Governance Topology Reconciliation:
           (Derived strictly by comparing the measured ingress inventory from E-00 against
           the observed sets in E-01, E-02, E-03, E-04. Zero hardcoded numeric constants).
"""

import socket
import subprocess
import time
import os
import sys
import json
import hashlib
import re
import threading
from datetime import datetime, timezone
import pytest
from pymavlink import mavutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from drone.validator import compute_arg_hash, sign_execution_request

PX4_DIR = "/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default"
PX4_BIN = f"{PX4_DIR}/bin/px4"
PX4_GOVERNED_ETC = "/home/ai_user/px4_governed_etc"

DRONE_DIR = os.path.join(BASE_DIR, "drone")
MULTI_PEP_SCRIPT = os.path.join(DRONE_DIR, "multi_pep_proxy.py")
MULTI_PEP_LOG = os.path.join(DRONE_DIR, "multi_pep_audit.log")
POSTURE_FILE = os.path.join(DRONE_DIR, "active_posture.json")
E05_FILE = os.path.join(DRONE_DIR, "s2_e_empirical_results.json")

# 4 Ingress Ports (Exclusively bound by DROS Multi-PEP)
ONBOARD_INGRESS = 14540
GCS_INGRESS = 18570
CAMERA_INGRESS = 14280
GIMBAL_INGRESS = 13030

# Downstream Multi-Channel Instrumented Relay Ports
TAP_ONBOARD = 14588
TAP_GCS = 18578
TAP_CAMERA = 14288
TAP_GIMBAL = 13038

# Downstream PX4 Backend Ports (Internal, non-colliding loopback)
PX4_ONBOARD_BACKEND = 14580
PX4_GCS_BACKEND = 18571
PX4_CAMERA_BACKEND = 14281
PX4_GIMBAL_BACKEND = 13031

# Canonical Downstream Channel Identifiers
ONBOARD_CHANNEL = "ONBOARD"
GCS_CHANNEL = "GCS"
CAMERA_CHANNEL = "CAMERA"
GIMBAL_CHANNEL = "GIMBAL"

TEST_FIXTURE_ONBOARD_PRIVKEY_HEX = "e5933ab83d0ee642a9848cd7623067d5a546a98ec0e2827ac4a21235321d186f"
TEST_FIXTURE_PLANNER_PRIVKEY_HEX = "15496b240763c8b70795633c9f50c40272223999db094cb36c36d5ef4b488152"

# Evidence artifact filepaths (Disk-based for order-independent evaluation)
E00_ARTIFACT = "/tmp/dros_evidence_e00.json"
E01_ARTIFACT = "/tmp/dros_evidence_e01.json"
E02_ARTIFACT = "/tmp/dros_evidence_e02.json"
E03_ARTIFACT = "/tmp/dros_evidence_e03.json"
E04_ARTIFACT = "/tmp/dros_evidence_e04.json"

class MultiChannelDownstreamRelay:
    """
    Multi-channel instrumented relay intercepting ALL 4 forwarding channels between
    DROS Multi-PEP and PX4 isolated backend:
      - 14588 -> 14580 (Onboard)
      - 18578 -> 18571 (GCS)
      - 14288 -> 14281 (Camera)
      - 13038 -> 13031 (Gimbal)
    """
    def __init__(self):
        self.channels = {
            TAP_ONBOARD: {"fwd_port": PX4_ONBOARD_BACKEND, "name": ONBOARD_CHANNEL, "ingress": ONBOARD_INGRESS},
            TAP_GCS: {"fwd_port": PX4_GCS_BACKEND, "name": GCS_CHANNEL, "ingress": GCS_INGRESS},
            TAP_CAMERA: {"fwd_port": PX4_CAMERA_BACKEND, "name": CAMERA_CHANNEL, "ingress": CAMERA_INGRESS},
            TAP_GIMBAL: {"fwd_port": PX4_GIMBAL_BACKEND, "name": GIMBAL_CHANNEL, "ingress": GIMBAL_INGRESS}
        }
        self.packets = []
        self.total_bytes = 0
        self.running = False
        self.socks = {}
        self.threads = []

    def start(self):
        self.running = True
        for tap_port, cfg in self.channels.items():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", tap_port))
            s.settimeout(0.2)
            fwd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socks[tap_port] = (s, fwd, cfg["fwd_port"], cfg["name"], cfg["ingress"])
            t = threading.Thread(target=self._channel_loop, args=(s, fwd, cfg["fwd_port"], cfg["name"], cfg["ingress"]), daemon=True)
            self.threads.append(t)
            t.start()

    def _channel_loop(self, s, fwd, fwd_port, name, ingress):
        mav = mavutil.mavlink.MAVLink(None)
        while self.running:
            try:
                data, addr = s.recvfrom(65535)
                recv_ns = time.time_ns()
                self.total_bytes += len(data)
                datagram_sha256 = hashlib.sha256(data).hexdigest()
                msgs = mav.parse_buffer(data)
                msg_types = [m.get_type() for m in msgs] if msgs else []

                self.packets.append({
                    "channel": name,
                    "ingress": ingress,
                    "types": msg_types,
                    "len": len(data),
                    "raw": data,
                    "sha256": datagram_sha256,
                    "timestamp_ns": recv_ns
                })
                fwd.sendto(data, ("127.0.0.1", fwd_port))
            except socket.timeout:
                continue
            except Exception:
                break

    def stop(self):
        self.running = False
        for t in self.threads:
            t.join(timeout=0.5)
        for s, fwd, _, _, _ in self.socks.values():
            try:
                s.close()
                fwd.close()
            except Exception:
                pass

def get_log_offset(log_file: str) -> int:
    if os.path.exists(log_file):
        return os.path.getsize(log_file)
    return 0

def read_log_delta(log_file: str, offset: int) -> str:
    if not os.path.exists(log_file):
        return ""
    with open(log_file, "r", encoding="utf-8") as f:
        f.seek(offset)
        return f.read()

def read_px4_param(target_port: int, client_port: int, param_name: bytes, timeout_sec: float = 2.5):
    """Independent observation path: direct MAVLink query to PX4 backend."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", client_port))
    sock.settimeout(0.3)
    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 255
    mav.srcComponent = 0

    param_val = None
    start = time.time()
    last_send = 0
    while time.time() - start < timeout_sec:
        now = time.time()
        if now - last_send > 0.3:
            hb = mav.heartbeat_encode(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            sock.sendto(hb.pack(mav), ("127.0.0.1", target_port))
            req = mav.param_request_read_encode(1, 1, param_name, -1)
            sock.sendto(req.pack(mav), ("127.0.0.1", target_port))
            last_send = now

        try:
            data, addr = sock.recvfrom(4096)
            mav_in = mavutil.mavlink.MAVLink(None)
            msgs = mav_in.parse_buffer(data)
            if msgs:
                for m in msgs:
                    if m.get_type() == "PARAM_VALUE" and param_name.decode("ascii") in m.param_id:
                        param_val = m.param_value
                        break
            if param_val is not None:
                break
        except socket.timeout:
            continue
        except Exception:
            break
    sock.close()
    return param_val

@pytest.fixture(scope="module")
def s2_e_env():
    # 1. Clean previous lingering processes and evidence files (Patch 5)
    subprocess.run(["pkill", "-9", "-f", "bin/px4"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "pep_proxy.py"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "multi_pep_proxy.py"], capture_output=True)
    for art in [E00_ARTIFACT, E01_ARTIFACT, E02_ARTIFACT, E03_ARTIFACT, E04_ARTIFACT, E05_FILE]:
        if os.path.exists(art):
            try:
                os.remove(art)
            except Exception:
                pass
    time.sleep(0.5)

    # 2. Start Multi-Channel Downstream Relay (covering all 4 channels)
    relay = MultiChannelDownstreamRelay()
    relay.start()

    # 3. Start PX4 SITL with governed isolated configuration (listeners on backend ports 18571, 14281, 13031, 14580)
    px4_proc = subprocess.Popen(
        [PX4_BIN, "-d", PX4_GOVERNED_ETC],
        cwd=PX4_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)

    # 4. Start DROS Multi-PEP Proxy (exclusively binding 14540, 18570, 14280, 13030)
    env = os.environ.copy()
    env["DROS_FC_ONBOARD_TAP_PORT"] = str(TAP_ONBOARD)
    env["DROS_FC_GCS_TAP_PORT"] = str(TAP_GCS)
    env["DROS_FC_CAMERA_TAP_PORT"] = str(TAP_CAMERA)
    env["DROS_FC_GIMBAL_TAP_PORT"] = str(TAP_GIMBAL)

    multi_pep_proc = subprocess.Popen(
        [sys.executable, MULTI_PEP_SCRIPT],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    yield relay, px4_proc, multi_pep_proc

    relay.stop()
    for p in [multi_pep_proc, px4_proc]:
        try:
            p.terminate()
            p.wait(timeout=2.0)
        except Exception:
            p.kill()

def build_signed_request(action: str, capability: str, payload: dict, ingress_port: int, privkey_hex: str, req_id: str = None):
    with open(POSTURE_FILE, "r", encoding="utf-8") as f:
        posture_token = json.load(f)
    expiry = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 300))
    if req_id is None:
        req_id = f"s2e-tx-{ingress_port}-{time.time_ns()}"
    req = {
        "request_id": req_id,
        "principal": "onboard-mission-agent",
        "capability": capability,
        "action": action,
        "target": {"interface": "flight_controller.mavlink", "endpoint": f"udp://127.0.0.1:{ingress_port}"},
        "payload": payload,
        "runtime_posture": {"posture_ref": posture_token["posture_ref"]},
        "provenance": {
            "provenance_ref": "prov-claim-multi-pep-01",
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
    req["provenance"]["data"]["signature"] = sign_execution_request(req, privkey_hex)
    return req

def test_s2_e_00_preflight_socket_topology_verification(s2_e_env):
    """
    S2-E-00: Pre-flight Socket Topology & Exclusive Ownership Verification (Patch 4)
    Parses exact Local Address:Port column from 'ss -ulpn -H'.
    Rigorously verifies:
      1. Every public ingress port maps to EXACTLY ONE owner PID, which equals multi_pep_proc.pid.
      2. PX4 does not own any public ingress port.
      3. Every backend port maps to EXACTLY ONE owner PID, which equals px4_proc.pid.
      4. Emits measured topology artifact: E00_ARTIFACT.
    """
    relay, px4_proc, multi_pep_proc = s2_e_env

    res = subprocess.run(["ss", "-ulpn", "-H"], capture_output=True, text=True)
    ss_lines = res.stdout.splitlines()

    expected_ingresses = [ONBOARD_INGRESS, GCS_INGRESS, CAMERA_INGRESS, GIMBAL_INGRESS]
    expected_backends = [PX4_ONBOARD_BACKEND, PX4_GCS_BACKEND, PX4_CAMERA_BACKEND, PX4_GIMBAL_BACKEND]

    # Map port -> list of detailed socket records
    measured_ingress_records = {p: [] for p in expected_ingresses}
    measured_backend_records = {p: [] for p in expected_backends}

    # ss output columns: State, Recv-Q, Send-Q, Local Address:Port, Peer Address:Port, Process
    # e.g., UNCONN 0 0 127.0.0.1:18570 0.0.0.0:* users:(("python",pid=1234,fd=3))
    for line in ss_lines:
        parts = line.strip().split()
        if len(parts) >= 4:
            local_addr = parts[3]
            if ":" in local_addr:
                try:
                    port_str = local_addr.rsplit(":", 1)[1]
                    port = int(port_str)
                except ValueError:
                    continue

                pids = [int(x) for x in re.findall(r'pid=(\d+)', line)]
                record = {
                    "local_address": local_addr,
                    "owner_pids": pids,
                    "raw_line": line
                }

                if port in measured_ingress_records:
                    measured_ingress_records[port].append(record)
                if port in measured_backend_records:
                    measured_backend_records[port].append(record)

    ingress_topology_summary = {}
    for port in expected_ingresses:
        records = measured_ingress_records[port]
        assert len(records) >= 1, f"Ingress {port} not found in kernel socket table!"
        all_pids = set()
        for r in records:
            all_pids.update(r["owner_pids"])

        assert len(all_pids) == 1, f"Ingress {port} does not have exactly one owner PID! Observed: {all_pids}"
        assert all_pids == {multi_pep_proc.pid}, (
            f"Ingress {port} owner mismatch! Expected multi_pep={multi_pep_proc.pid}, got {all_pids}"
        )
        assert px4_proc.pid not in all_pids, f"CRITICAL: PX4 directly owns ingress {port}!"

        assert records[0]["local_address"].startswith("127.0.0.1:") or records[0]["local_address"].startswith("[::1]:"), (
            f"Ingress {port} not bound to loopback! Observed: {records[0]['local_address']}"
        )

        ingress_topology_summary[str(port)] = {
            "local_address": records[0]["local_address"],
            "owner_pids": list(all_pids),
            "socket_records": [r["raw_line"] for r in records]
        }

    backend_topology_summary = {}
    for port in expected_backends:
        records = measured_backend_records[port]
        assert len(records) >= 1, f"Backend port {port} not found in kernel socket table!"
        all_pids = set()
        for r in records:
            all_pids.update(r["owner_pids"])

        assert len(all_pids) == 1, f"Backend port {port} does not have exactly one owner PID! Observed: {all_pids}"
        assert all_pids == {px4_proc.pid}, (
            f"Backend port {port} owner mismatch! Expected px4={px4_proc.pid}, got {all_pids}"
        )
        assert records[0]["local_address"].startswith("127.0.0.1:") or records[0]["local_address"].startswith("[::1]:"), (
            f"Backend port {port} not bound to loopback! Observed: {records[0]['local_address']}"
        )

        backend_topology_summary[str(port)] = {
            "local_address": records[0]["local_address"],
            "owner_pids": list(all_pids),
            "socket_records": [r["raw_line"] for r in records]
        }

    topology_record = {
        "test": "S2-E-00",
        "ingress_topology": ingress_topology_summary,
        "backend_topology": backend_topology_summary,
        "multi_pep_pid": multi_pep_proc.pid,
        "px4_pid": px4_proc.pid,
        "exclusive_ingress_ownership_verified": True,
        "exclusive_backend_ownership_verified": True
    }

    with open(E00_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(topology_record, f, indent=2)

def test_s2_e_01_unauthorized_execution_blocked_across_all_ingresses(s2_e_env):
    """
    S2-E-01: Proves that unauthorized / unauthenticated execution requests sent to ALL
    4 ingresses (14540, 18570, 14280, 13030) are intercepted and dropped by DROS PEP.
    Rigorously verifies:
      1. Isolated PEP audit log records BLOCKED for that specific ingress.
      2. Multi-Channel Instrumented Relay frame delta == 0.
      3. Multi-Channel Instrumented Relay byte delta == 0.
    Writes empirical artifact: E01_ARTIFACT.
    """
    relay, px4_proc, multi_pep_proc = s2_e_env

    evidence_records = []
    for ingress_port in [ONBOARD_INGRESS, GCS_INGRESS, CAMERA_INGRESS, GIMBAL_INGRESS]:
        frames_before = len(relay.packets)
        bytes_before = relay.total_bytes
        log_offset = get_log_offset(MULTI_PEP_LOG)

        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 255
        mav.srcComponent = 0
        raw_attack = mav.param_set_encode(1, 1, b"MIS_TAKEOFF_ALT", 99.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32).pack(mav)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(raw_attack, ("127.0.0.1", ingress_port))
        sock.close()
        time.sleep(0.5)

        frames_after = len(relay.packets)
        bytes_after = relay.total_bytes
        new_log = read_log_delta(MULTI_PEP_LOG, log_offset)

        delta_frames = frames_after - frames_before
        delta_bytes = bytes_after - bytes_before

        assert "BLOCKED:" in new_log, f"Ingress {ingress_port} failed to block raw unauthorized packet"
        assert f":{ingress_port}:" in new_log
        assert delta_frames == 0, f"Ingress {ingress_port} leaked {delta_frames} downstream frames to relay!"
        assert delta_bytes == 0, f"Ingress {ingress_port} leaked {delta_bytes} downstream bytes to relay!"

        evidence_records.append({
            "ingress_port": ingress_port,
            "blocked": True,
            "delta_frames": delta_frames,
            "delta_bytes": delta_bytes
        })

    with open(E01_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump({"test": "S2-E-01", "records": evidence_records}, f, indent=2)

def test_s2_e_02_authorized_forwarding_and_downstream_observation_across_all_ingresses(s2_e_env):
    """
    S2-E-02: Authorized Forwarding & Downstream Observation Across All 4 Ingresses (Patch 2)
    Rigorously verifies:
      1. Cryptographically authorized execution request on each ingress passes DROS PEP.
      2. MAVLink frame is forwarded to the corresponding channel on the downstream relay.
      3. Patch 2: Enforces len(matched) == 1 within transaction observation window.
      * Note: Uses MPC_LAND_SPEED for GCS to avoid polluting E-04's MIS_TAKEOFF_ALT contrast pair.
    Writes empirical artifact: E02_ARTIFACT.
    """
    relay, px4_proc, multi_pep_proc = s2_e_env

    ingress_test_cases = [
        {"port": ONBOARD_INGRESS, "action": "ARM", "cap": "ARM", "payload": {"action_name": "ARM_MOTORS"}, "expected_msg": "COMMAND_LONG"},
        {"port": GCS_INGRESS, "action": "PARAMETER_WRITE", "cap": "PARAMETER_WRITE", "payload": {"param_id": "MPC_LAND_SPEED", "param_value": 0.8, "param_type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}, "expected_msg": "PARAM_SET"},
        {"port": CAMERA_INGRESS, "action": "CAMERA_TRIGGER", "cap": "CAMERA_TRIGGER", "payload": {"trigger": 1}, "expected_msg": "COMMAND_LONG"},
        {"port": GIMBAL_INGRESS, "action": "GIMBAL_CONTROL", "cap": "GIMBAL_CONTROL", "payload": {"pitch": 0.0, "yaw": 0.0}, "expected_msg": "COMMAND_LONG"}
    ]

    forwarding_records = []
    for tc in ingress_test_cases:
        ingress_port = tc["port"]
        action = tc["action"]
        cap = tc["cap"]
        payload = tc["payload"]
        expected_msg = tc["expected_msg"]

        log_offset = get_log_offset(MULTI_PEP_LOG)
        tx_id = f"tx-s2e-fwd-{ingress_port}-{time.time_ns()}"

        auth_req = build_signed_request(
            action=action,
            capability=cap,
            payload=payload,
            ingress_port=ingress_port,
            privkey_hex=TEST_FIXTURE_ONBOARD_PRIVKEY_HEX,
            req_id=tx_id
        )

        t_send_ns = time.time_ns()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(auth_req).encode("utf-8"), ("127.0.0.1", ingress_port))
        sock.close()
        time.sleep(0.6)

        # 1. Assert PEP recorded FORWARDED
        new_log = read_log_delta(MULTI_PEP_LOG, log_offset)
        assert "FORWARDED:" in new_log, f"Ingress {ingress_port} failed to forward authorized {action}"
        assert tx_id in new_log
        assert action in new_log
        assert "POLICY_AUTHORIZED" in new_log

        # 2. Patch 2: Enforce len(matched) == 1 within transaction observation window
        matched_packets = [
            p for p in relay.packets
            if p["ingress"] == ingress_port and p["timestamp_ns"] >= t_send_ns and expected_msg in p["types"]
        ]
        assert len(matched_packets) == 1, (
            f"Expected exactly 1 matching datagram for tx {tx_id} on ingress {ingress_port}, got {len(matched_packets)}!"
        )

        obs = matched_packets[0]
        forwarding_records.append({
            "tx_id": tx_id,
            "ingress_port": ingress_port,
            "action": action,
            "expected_msg": expected_msg,
            "forwarded_and_observed": True,
            "t_send_ns": t_send_ns,
            "observed_at_ns": obs["timestamp_ns"],
            "observed_sha256": obs["sha256"],
            "observed_len": obs["len"],
            "observed_types": obs["types"]
        })

    with open(E02_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump({"test": "S2-E-02", "records": forwarding_records}, f, indent=2)

def test_s2_e_03_transaction_correlation_proof_across_all_ingresses(s2_e_env):
    """
    S2-E-03: Full 4-Ingress Cryptographic Transaction Correlation Proof (Patch 1)
    Independently demonstrates 1-to-1 cryptographic ownership across ALL 4 ingresses:
      Request(request_id, principal, arg_hash, signature)
        -> PEP Audit Log (FORWARDED, timestamp_ns, ingress, target_port, frame_sha256)
        -> Relay Observed Raw Datagram Bytes (observed_datagram_sha256).
    Patch 1: Enforces len(matched) == 1 and verifies full routing correlation:
      target_port, channel, ingress, and frame_sha256 == observed_sha256.
    Writes empirical artifact: E03_ARTIFACT.
    """
    relay, px4_proc, multi_pep_proc = s2_e_env

    correlation_test_cases = [
        {"port": ONBOARD_INGRESS, "target": TAP_ONBOARD, "channel": "ONBOARD", "action": "ARM", "cap": "ARM", "payload": {"action_name": "ARM_MOTORS"}},
        {"port": GCS_INGRESS, "target": TAP_GCS, "channel": "GCS", "action": "PARAMETER_WRITE", "cap": "PARAMETER_WRITE", "payload": {"param_id": "MPC_XY_VEL_MAX", "param_value": 11.5, "param_type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32}},
        {"port": CAMERA_INGRESS, "target": TAP_CAMERA, "channel": "CAMERA", "action": "CAMERA_TRIGGER", "cap": "CAMERA_TRIGGER", "payload": {"trigger": 1}},
        {"port": GIMBAL_INGRESS, "target": TAP_GIMBAL, "channel": "GIMBAL", "action": "GIMBAL_CONTROL", "cap": "GIMBAL_CONTROL", "payload": {"pitch": 10.0, "yaw": 5.0}}
    ]

    correlation_records = []
    for tc in correlation_test_cases:
        ingress_port = tc["port"]
        expected_target_port = tc["target"]
        expected_channel = tc["channel"]
        action = tc["action"]
        cap = tc["cap"]
        payload = tc["payload"]

        log_offset = get_log_offset(MULTI_PEP_LOG)
        tx_id = f"tx-corr-4in-{ingress_port}-{time.time_ns()}"

        auth_req = build_signed_request(
            action=action,
            capability=cap,
            payload=payload,
            ingress_port=ingress_port,
            privkey_hex=TEST_FIXTURE_ONBOARD_PRIVKEY_HEX,
            req_id=tx_id
        )

        t_send_ns = time.time_ns()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(auth_req).encode("utf-8"), ("127.0.0.1", ingress_port))
        sock.close()
        time.sleep(0.7)

        new_log = read_log_delta(MULTI_PEP_LOG, log_offset)
        assert "FORWARDED:" in new_log
        assert tx_id in new_log

        matching_line = [line for line in new_log.splitlines() if tx_id in line][0]
        parts = matching_line.split(":")
        log_ts_ns = int(parts[1])
        log_ingress = int(parts[2])
        log_req_id = parts[3]
        log_principal = parts[4]
        log_action = parts[5]
        log_target_port = int(parts[6])
        log_frame_sha256 = parts[7]

        # Verify PEP log attributes
        assert log_ingress == ingress_port
        assert log_target_port == expected_target_port
        assert log_action == action
        assert log_req_id == tx_id
        assert log_principal == "onboard-mission-agent"

        # Patch 1: Filter exactly 1 matching datagram from relay observation stream
        matched_datagrams = [
            p for p in relay.packets
            if p["ingress"] == ingress_port
            and p["timestamp_ns"] >= t_send_ns
            and p["channel"] == expected_channel
            and p["sha256"] == log_frame_sha256
        ]
        assert len(matched_datagrams) == 1, (
            f"Expected exactly 1 correlated datagram for tx {tx_id} on ingress {ingress_port}, got {len(matched_datagrams)}!"
        )

        obs = matched_datagrams[0]
        correlation_records.append({
            "request_id": tx_id,
            "ingress": log_ingress,
            "principal": log_principal,
            "action": log_action,
            "target_port": log_target_port,
            "channel": expected_channel,
            "arg_hash": auth_req["arg_hash"],
            "compiled_sha256": log_frame_sha256,
            "observed_sha256": obs["sha256"],
            "observed_at_ns": obs["timestamp_ns"],
            "correlation_verified": True
        })

    with open(E03_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump({"test": "S2-E-03", "records": correlation_records}, f, indent=2)

def test_s2_e_04_real_state_mutation_observed_after_authorized_pep_execution(s2_e_env):
    """
    S2-E-04: Real State Mutation Observed After Authorized PEP Execution
    Clean Contrast Pair on unpolluted parameter MIS_TAKEOFF_ALT:
      1. Baseline read: MIS_TAKEOFF_ALT = initial_val (via independent observation path).
      2. Raw unauthenticated attack to Ingress 18570 -> Blocked by PEP -> Post-attack val == initial_val.
      3. Authorized request to Ingress 18570 -> Forwarded by PEP to PX4 backend ->
         Live PX4 parameter MUTATES to 22.5 (pre != post and post == 22.5).
    Writes empirical artifact: E04_ARTIFACT.
    """
    relay, px4_proc, multi_pep_proc = s2_e_env

    # 1. Independent baseline read
    initial_val = read_px4_param(PX4_GCS_BACKEND, 18590, b"MIS_TAKEOFF_ALT", timeout_sec=3.0)
    assert initial_val is not None, "Failed to connect and query live PX4 backend parameter"

    # 2. Raw unauthenticated attack directly to Ingress 18570 (Attempt to mutate to 99.0)
    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 255
    mav.srcComponent = 0
    attack_packet = mav.param_set_encode(1, 1, b"MIS_TAKEOFF_ALT", 99.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32).pack(mav)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(attack_packet, ("127.0.0.1", GCS_INGRESS))
    sock.close()
    time.sleep(0.8)

    # Verify state DID NOT change after attack
    post_attack_val = read_px4_param(PX4_GCS_BACKEND, 18591, b"MIS_TAKEOFF_ALT", timeout_sec=2.0)
    assert post_attack_val == initial_val, f"Parameter changed unexpectedly after unauthenticated attack! {initial_val} -> {post_attack_val}"

    # 3. Legitimate, signed PARAMETER_WRITE request to Ingress 18570 via DROS PEP (Target 22.5)
    target_val = 22.5
    t_send_ns = time.time_ns()
    tx_id = f"tx-param-mutation-{t_send_ns}"
    auth_req = build_signed_request(
        action="PARAMETER_WRITE",
        capability="PARAMETER_WRITE",
        payload={"param_id": "MIS_TAKEOFF_ALT", "param_value": target_val, "param_type": mavutil.mavlink.MAV_PARAM_TYPE_REAL32},
        ingress_port=GCS_INGRESS,
        privkey_hex=TEST_FIXTURE_ONBOARD_PRIVKEY_HEX,
        req_id=tx_id
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(auth_req).encode("utf-8"), ("127.0.0.1", GCS_INGRESS))
    sock.close()
    time.sleep(1.0)

    # 4. Strict Transaction Correlation: Verify PEP forward log
    with open(MULTI_PEP_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()

    assert f"FORWARDED" in log_content, f"PEP did not forward authorized request {tx_id}!"
    matching_lines = [l for l in log_content.splitlines() if f":{tx_id}:" in l and "FORWARDED" in l]
    assert len(matching_lines) == 1, f"Expected 1 FORWARDED log for {tx_id}, got {len(matching_lines)}"

    # Parse log format: FORWARDED:timestamp_ns:ingress_port:req_id:principal:action:target_port:frame_sha256:POLICY_AUTHORIZED
    log_parts = matching_lines[0].split(":")
    log_ts = int(log_parts[1])
    log_ingress = int(log_parts[2])
    log_req_id = log_parts[3]
    log_principal = log_parts[4]
    log_action = log_parts[5]
    log_target_port = int(log_parts[6])
    log_frame_sha256 = log_parts[7]

    assert log_ingress == GCS_INGRESS, f"Expected ingress {GCS_INGRESS}, got {log_ingress}"
    assert log_target_port == TAP_GCS, f"Expected downstream target {TAP_GCS}, got {log_target_port}"
    assert log_action == "PARAMETER_WRITE"
    assert log_req_id == tx_id
    assert log_principal == "onboard-mission-agent"

    # 5. Strict Wire Correlation: Exactly 1 matching datagram captured by downstream relay
    matched_datagrams = [
        p for p in relay.packets
        if p["ingress"] == GCS_INGRESS
        and p["timestamp_ns"] >= t_send_ns
        and p["channel"] == GCS_CHANNEL
        and p["sha256"] == log_frame_sha256
    ]
    assert len(matched_datagrams) == 1, (
        f"Expected exactly 1 correlated datagram for {tx_id} on GCS relay, got {len(matched_datagrams)}!"
    )
    observed_datagram = matched_datagrams[0]

    # 6. Independent observation: Verify live PX4 parameter mutated to 22.5
    mutated_val = read_px4_param(PX4_GCS_BACKEND, 18592, b"MIS_TAKEOFF_ALT", timeout_sec=3.0)
    assert mutated_val is not None, "Failed to read parameter after PEP authorized execution"
    assert abs(mutated_val - target_val) < 0.01, f"Parameter mutation failed to manifest in PX4! Expected {target_val}, got {mutated_val}"

    mutation_evidence = {
        "parameter": "MIS_TAKEOFF_ALT",
        "initial_val": initial_val,
        "post_attack_val": post_attack_val,
        "target_val": target_val,
        "mutated_val": mutated_val,
        "unauthenticated_attack_mutated": False,
        "authorized_pep_execution_mutated": True,
        "transaction_correlation": {
            "request_id": tx_id,
            "t_send_ns": t_send_ns,
            "ingress": log_ingress,
            "target_port": log_target_port,
            "channel": GCS_CHANNEL,
            "compiled_sha256": log_frame_sha256,
            "observed_sha256": observed_datagram["sha256"],
            "observed_at_ns": observed_datagram["timestamp_ns"],
            "correlation_verified": True
        }
    }

    with open(E04_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump({"test": "S2-E-04", "record": mutation_evidence}, f, indent=2)

def test_s2_e_05_empirical_governance_reconciliation(s2_e_env):
    """
    S2-E-05: Multi-Ingress Governance Topology Reconciliation
    DERIVED STRICTLY FROM MEASURED EVIDENCE: Reconciles E-00 measured ingress inventory against
    the observed sets from E-01, E-02, E-03, E-04.
    ZERO HARDCODED NUMERIC EXPECTATIONS.
    """
    for art in [E00_ARTIFACT, E01_ARTIFACT, E02_ARTIFACT, E03_ARTIFACT, E04_ARTIFACT]:
        assert os.path.exists(art), f"Missing required evidence artifact: {art}"

    with open(E00_ARTIFACT, "r", encoding="utf-8") as f:
        e00_data = json.load(f)
    with open(E01_ARTIFACT, "r", encoding="utf-8") as f:
        e01_data = json.load(f)
    with open(E02_ARTIFACT, "r", encoding="utf-8") as f:
        e02_data = json.load(f)
    with open(E03_ARTIFACT, "r", encoding="utf-8") as f:
        e03_data = json.load(f)
    with open(E04_ARTIFACT, "r", encoding="utf-8") as f:
        e04_data = json.load(f)

    # 1. Base measured inventory from E-00 kernel socket audit
    measured_ingress_set = set(int(p) for p in e00_data.get("ingress_topology", {}).keys())
    assert len(measured_ingress_set) > 0, "No ingress ports measured in E-00!"

    # 2. Blocked ingresses set from E-01
    blocked_ingress_set = set([r["ingress_port"] for r in e01_data.get("records", []) if r.get("blocked")])
    total_leakage_frames = sum([r.get("delta_frames", 0) for r in e01_data.get("records", [])])

    # 3. Authorized forwarding set from E-02
    authorized_ingress_set = set([r["ingress_port"] for r in e02_data.get("records", []) if r.get("forwarded_and_observed")])

    # 4. Correlated ingresses set from E-03
    correlated_ingress_set = set([r["ingress"] for r in e03_data.get("records", []) if r.get("correlation_verified")])

    # 5. Mutation outcome from E-04
    state_mutated = e04_data.get("record", {}).get("authorized_pep_execution_mutated", False)
    attack_blocked = not e04_data.get("record", {}).get("unauthenticated_attack_mutated", True)

    # Reconcile sets: all empirical sets must match the measured ingress inventory exactly
    assert blocked_ingress_set == measured_ingress_set, (
        f"Blocked set mismatch! Measured={measured_ingress_set} vs Blocked={blocked_ingress_set}"
    )
    assert total_leakage_frames == 0, f"Downstream leakage frames detected: {total_leakage_frames}"

    assert authorized_ingress_set == measured_ingress_set, (
        f"Authorized set mismatch! Measured={measured_ingress_set} vs Authorized={authorized_ingress_set}"
    )

    assert correlated_ingress_set == measured_ingress_set, (
        f"Correlation set mismatch! Measured={measured_ingress_set} vs Correlated={correlated_ingress_set}"
    )

    assert state_mutated is True, "State mutation was not achieved via PEP in E-04"
    assert attack_blocked is True, "Direct unauthenticated attack mutated state in E-04!"

    reconciliation_summary = {
        "measured_ingress_inventory": sorted(list(measured_ingress_set)),
        "blocked_ingress_inventory": sorted(list(blocked_ingress_set)),
        "authorized_ingress_inventory": sorted(list(authorized_ingress_set)),
        "correlated_ingress_inventory": sorted(list(correlated_ingress_set)),
        "total_downstream_leakage_frames": total_leakage_frames,
        "state_mutation_verified": state_mutated,
        "unauthenticated_mutation_prevented": attack_blocked,
        "sets_perfectly_reconciled": True
    }

    with open(E05_FILE, "w", encoding="utf-8") as f:
        json.dump(reconciliation_summary, f, indent=2)
