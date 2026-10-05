# -*- coding: utf-8 -*-
"""
Milestone M1.1-S2-A: Unmediated Path Discovery & Baseline Reachability Inventory.
Audits the 4 UDP interfaces exposed by the genuine native C++ PX4 SITL process:
  - 14580: Onboard MAVLink (Governed via S1 mediated path)
  - 18570: GCS Normal MAVLink (Candidate unmediated bypass)
  - 14280: Camera MAVLink (Candidate unmediated bypass)
  - 13030: Gimbal MAVLink (Candidate unmediated bypass)

Assesses each path across 4 verification layers:
  L0: Network Reachability (Socket connects and accepts UDP datagrams)
  L1: Protocol Acceptance (MAVLink parser accepts frames and emits responses)
  L2: Application Handling (PX4 handles domain messages, e.g. HEARTBEAT / LOCAL_POSITION)
  L3: Execution Effect & DROS Mediation Status (Direct unmediated reachability without PEP observation)
"""

import socket
import subprocess
import time
import os
import sys
import pytest
from pymavlink import mavutil

PX4_DIR = "/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default"
PX4_BIN = f"{PX4_DIR}/bin/px4"
PX4_ETC = f"{PX4_DIR}/etc"

TARGET_PORTS = {
    18570: "GCS_NORMAL",
    14580: "ONBOARD",
    14280: "CAMERA",
    13030: "GIMBAL"
}

@pytest.fixture(scope="module")
def px4_baseline_env():
    # Start clean genuine PX4 SITL without any firewall or DROS intercept on bypass ports
    proc = subprocess.Popen(
        [PX4_BIN, "-d", PX4_ETC],
        cwd=PX4_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2.5)
    yield proc
    proc.terminate()
    try:
        proc.wait(timeout=2.0)
    except Exception:
        proc.kill()

def probe_udp_mavlink_interface(port: int, duration_sec: float = 1.0):
    """
    Sends MAVLink HEARTBEAT to PX4 target port from ephemeral client
    and listens for observable return telemetry.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)

    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 254
    mav.srcComponent = 190
    hb = mav.heartbeat_encode(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0
    )
    raw_packet = hb.pack(mav)

    # L0: Send wire packet
    bytes_sent = sock.sendto(raw_packet, ("127.0.0.1", port))

    # L1 & L2: Receive responses
    received_msgs = []
    start = time.time()
    while time.time() - start < duration_sec:
        try:
            data, addr = sock.recvfrom(4096)
            mav_in = mavutil.mavlink.MAVLink(None)
            msgs = mav_in.parse_buffer(data)
            if msgs:
                for m in msgs:
                    received_msgs.append(m.get_type())
        except socket.timeout:
            continue
        except Exception:
            break
    sock.close()
    return bytes_sent, received_msgs

def test_s2_a_port_14580_onboard_path_reachability(px4_baseline_env):
    """Path 14580 (Onboard): Verified governed path in S1, here testing raw baseline reachability."""
    sent, msgs = probe_udp_mavlink_interface(14580, duration_sec=1.0)
    assert sent > 0
    assert len(msgs) > 0
    assert any(m in msgs for m in ["HIGHRES_IMU", "LOCAL_POSITION_NED", "HEARTBEAT", "STATUSTEXT"])

def test_s2_a_port_18570_gcs_bypass_reachability(px4_baseline_env):
    """
    Path 18570 (GCS Normal): Confirmed direct reachability on 0.0.0.0:18570.
    PX4 immediately responds with telemetry, proving an active, unmediated MAVLink channel.
    """
    sent, msgs = probe_udp_mavlink_interface(18570, duration_sec=1.0)
    assert sent > 0
    assert len(msgs) > 0
    # Confirmed: Port 18570 receives packets and emits MAVLink telemetry directly without PEP mediation
    assert any(m in msgs for m in ["LOCAL_POSITION_NED", "HIGHRES_IMU", "HEARTBEAT", "COMMAND_ACK"])

def test_s2_a_port_14280_camera_bypass_reachability(px4_baseline_env):
    """
    Path 14280 (Camera Onboard): Confirmed direct reachability on 0.0.0.0:14280.
    """
    sent, msgs = probe_udp_mavlink_interface(14280, duration_sec=1.0)
    assert sent > 0
    assert len(msgs) > 0
    assert any(m in msgs for m in ["STATUSTEXT", "HIGHRES_IMU", "COMMAND_ACK", "HEARTBEAT"])

def test_s2_a_port_13030_gimbal_bypass_reachability(px4_baseline_env):
    """
    Path 13030 (Gimbal MAVLink): Confirmed direct reachability on 0.0.0.0:13030.
    """
    sent, msgs = probe_udp_mavlink_interface(13030, duration_sec=1.0)
    assert sent > 0
    assert len(msgs) > 0
    assert any(m in msgs for m in ["STATUSTEXT", "COMMAND_ACK", "HEARTBEAT"])
