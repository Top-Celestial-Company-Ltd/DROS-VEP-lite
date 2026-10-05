# -*- coding: utf-8 -*-
"""
Milestone M1.1-S2-B: Execution Effect Confirmation across Discovered Unmediated Paths.
Core Research Question:
  Does unmediated MAVLink input sent directly to discovered bypass ports (18570, 14280)
  induce a documented, observable PX4 internal state transition, while bypassing DROS PEP entirely?

Evaluation Architecture:
  1. Contrast Pair across Mediated vs. Unmediated Path:
     - Path A (Mediated: 14540 -> PEP): Parameter write is strictly blocked by PEP policy engine
       (PARAMETER_WRITE not granted or unauthenticated raw packet dropped), zero downstream packets.
     - Path B (Unmediated: 18570 GCS): Same unauthenticated parameter write sent directly to PX4
       induces an immediate, documented state mutation (pre-val != post-val).
  2. Camera Port (14280) Unmediated State Mutation:
     - Directly induces parameter state transition without DROS PEP mediation.
"""

import socket
import subprocess
import time
import os
import sys
import pytest
from pymavlink import mavutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

PX4_DIR = "/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default"
PX4_BIN = f"{PX4_DIR}/bin/px4"
PX4_ETC = f"{PX4_DIR}/etc"

DRONE_DIR = os.path.join(BASE_DIR, "drone")
PEP_SCRIPT = os.path.join(DRONE_DIR, "pep_proxy.py")

PEP_PORT = 14540
TAP_PORT = 14588
PX4_ONBOARD_PORT = 14580
PX4_GCS_PORT = 18570
PX4_CAMERA_PORT = 14280
PX4_GIMBAL_PORT = 13030

CLIENT_PORT_GCS = 18575
CLIENT_PORT_CAM = 14285

@pytest.fixture(scope="module")
def s2_b_env():
    # 1. Kill any lingering px4 and pep
    subprocess.run(["pkill", "-9", "-f", "bin/px4"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "pep_proxy.py"], capture_output=True)
    time.sleep(0.5)

    # 2. Start clean PX4 SITL
    px4_proc = subprocess.Popen(
        [PX4_BIN, "-d", PX4_ETC],
        cwd=PX4_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)

    # 3. Start DROS PEP Proxy targeting Onboard TAP/PX4
    env = os.environ.copy()
    env["DROS_FC_PORT"] = str(TAP_PORT)
    pep_proc = subprocess.Popen(
        [sys.executable, PEP_SCRIPT],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    yield px4_proc, pep_proc

    # Teardown
    for p in [pep_proc, px4_proc]:
        try:
            p.terminate()
            p.wait(timeout=2.0)
        except Exception:
            p.kill()

def read_px4_param(target_port: int, client_port: int, param_name: bytes, timeout_sec: float = 2.5):
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

def write_px4_param(target_port: int, client_port: int, param_name: bytes, new_val: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", client_port))
    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 255
    mav.srcComponent = 0

    msg = mav.param_set_encode(1, 1, param_name, new_val, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
    bytes_sent = sock.sendto(msg.pack(mav), ("127.0.0.1", target_port))
    sock.close()
    return bytes_sent

def test_s2_b_01_unmediated_gcs_path_induces_parameter_state_transition(s2_b_env):
    """
    Substage S2-B: Confirms that unmediated bypass port UDP 18570 allows raw, unauthenticated
    MAVLink parameter modification, directly inducing an observable internal state transition in PX4.
    Pre-state != Post-state is verified.
    """
    param_name = b"MIS_TAKEOFF_ALT"

    # Step 1: Document Pre-state
    pre_val = read_px4_param(PX4_GCS_PORT, CLIENT_PORT_GCS, param_name)
    assert pre_val is not None, "Failed to read baseline parameter from PX4 GCS port 18570"

    # Step 2: Inject unmediated parameter mutation directly into bypass port
    target_val = 25.0 if pre_val != 25.0 else 30.0
    sent = write_px4_param(PX4_GCS_PORT, CLIENT_PORT_GCS, param_name, target_val)
    assert sent > 0
    time.sleep(0.5)

    # Step 3: Document Post-state
    post_val = read_px4_param(PX4_GCS_PORT, CLIENT_PORT_GCS, param_name)
    assert post_val is not None, "Failed to read post-mutation parameter from PX4 GCS port 18570"

    # Step 4: Verify documented state transition
    assert post_val != pre_val, f"Parameter value unchanged: pre={pre_val}, post={post_val}"
    assert abs(post_val - target_val) < 0.001, f"Parameter value mismatch: expected {target_val}, got {post_val}"

def test_s2_b_02_unmediated_camera_path_induces_parameter_state_transition(s2_b_env):
    """
    Substage S2-B: Confirms that unmediated bypass port UDP 14280 (Camera) allows raw
    parameter modification, directly inducing an observable internal state transition.
    """
    param_name = b"TRIG_INTERVAL"

    # Step 1: Pre-state
    pre_val = read_px4_param(PX4_CAMERA_PORT, CLIENT_PORT_CAM, param_name)
    assert pre_val is not None, "Failed to read baseline parameter from PX4 Camera port 14280"

    # Step 2: Inject unmediated mutation
    target_val = 40.0 if pre_val != 40.0 else 50.0
    sent = write_px4_param(PX4_CAMERA_PORT, CLIENT_PORT_CAM, param_name, target_val)
    assert sent > 0
    time.sleep(0.5)

    # Step 3: Post-state
    post_val = read_px4_param(PX4_CAMERA_PORT, CLIENT_PORT_CAM, param_name)
    assert post_val is not None, "Failed to read post-mutation parameter from PX4 Camera port 14280"

    # Step 4: Verify state transition
    assert post_val != pre_val, f"Parameter value unchanged: pre={pre_val}, post={post_val}"
    assert abs(post_val - target_val) < 0.001, f"Parameter value mismatch: expected {target_val}, got {post_val}"

def test_s2_b_03_contrast_pair_mediated_path_blocks_unauthorized_state_transition(s2_b_env):
    """
    Controlled Contrast Pair:
    Sends an unauthorized/unauthenticated MAVLink command (raw packet) to DROS PEP ingress (14540).
    DROS PEP intercepts, rejects provenance forgery / unauthenticated command, and guarantees
    ZERO packets reach downstream. The state of PX4 remains unchanged.
    """
    param_name = b"MIS_TAKEOFF_ALT"
    pre_val = read_px4_param(PX4_GCS_PORT, CLIENT_PORT_GCS, param_name)
    assert pre_val is not None, "Failed to read baseline parameter before contrast test"

    # Attempt to inject via DROS PEP on 14540 without valid cryptographic token/authorization
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 255
    mav.srcComponent = 0
    attack_packet = mav.param_set_encode(1, 1, param_name, 99.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32).pack(mav)

    sock.sendto(attack_packet, ("127.0.0.1", PEP_PORT))
    sock.close()
    time.sleep(0.5)

    # Verify PX4 parameter state did NOT change via mediated path
    post_val = read_px4_param(PX4_GCS_PORT, CLIENT_PORT_GCS, param_name)
    assert post_val is not None, "Failed to read parameter after contrast test"
    assert post_val == pre_val, f"Security violation: Mediated path permitted unauthorized state mutation! pre={pre_val}, post={post_val}"
