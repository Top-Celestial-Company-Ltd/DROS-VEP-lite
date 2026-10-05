# -*- coding: utf-8 -*-
"""
DROS Multi-Ingress MAVLink PEP Proxy Process (Milestone M1.1-S2-E).
Listens on all 4 vehicle execution ingresses concurrently:
  - 14540 (Onboard Ingress) -> Downstream mediated Tap 14588 -> PX4 14580
  - 18570 (GCS Ingress)     -> Downstream mediated Tap 18578 -> PX4 internal backend 18571
  - 14280 (Camera Ingress)  -> Downstream mediated Tap 14288 -> PX4 internal backend 14281
  - 13030 (Gimbal Ingress)  -> Downstream mediated Tap 13038 -> PX4 internal backend 13031

Full-Coverage Instrumented Boundary:
  - 100% of PEP forwarding traffic to PX4 passes through the multi-channel Downstream Tap.
  - Uses pure PDP evaluation: adapter.evaluate_and_authorize(req).
  - No internal SITL simulation execution inside adapter.
  - Deterministically compiles authorized requests to binary MAVLink frames.
  - Computes frame_sha256 on actual wire bytes before socket send.
  - Emits cryptographically correlated transaction log:
    FORWARDED:timestamp_ns:ingress_port:req_id:principal:action:target_port:frame_sha256:POLICY_AUTHORIZED
"""

import socket
import select
import time
import os
import sys
import json
import hashlib
from typing import Optional, Dict, Any
from pymavlink import mavutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.sitl.engine import ExternalNavigationIntegrityService

FC_HOST = os.environ.get("DROS_FC_HOST", "127.0.0.1")
# All 4 downstream destinations point to the Multi-Channel Tap
FC_ONBOARD_TAP_PORT = int(os.environ.get("DROS_FC_ONBOARD_TAP_PORT", "14588"))
FC_GCS_TAP_PORT = int(os.environ.get("DROS_FC_GCS_TAP_PORT", "18578"))
FC_CAMERA_TAP_PORT = int(os.environ.get("DROS_FC_CAMERA_TAP_PORT", "14288"))
FC_GIMBAL_TAP_PORT = int(os.environ.get("DROS_FC_GIMBAL_TAP_PORT", "13038"))

INGRESS_CONFIG = {
    14540: {"target_host": FC_HOST, "target_port": FC_ONBOARD_TAP_PORT, "name": "ONBOARD_INGRESS"},
    18570: {"target_host": FC_HOST, "target_port": FC_GCS_TAP_PORT, "name": "GCS_INGRESS"},
    14280: {"target_host": FC_HOST, "target_port": FC_CAMERA_TAP_PORT, "name": "CAMERA_INGRESS"},
    13030: {"target_host": FC_HOST, "target_port": FC_GIMBAL_TAP_PORT, "name": "GIMBAL_INGRESS"}
}

adapter = DroneExecutionAdapter()
nav_service = ExternalNavigationIntegrityService()
posture_token = nav_service.generate_posture_token()
adapter.register_external_posture(posture_token)

posture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "active_posture.json")
with open(posture_path, "w", encoding="utf-8") as pf:
    json.dump(posture_token, pf)

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi_pep_audit.log")
with open(log_path, "w", encoding="utf-8") as f:
    f.write("DROS_MULTI_PEP_STARTED\n")
    f.flush()

sockets = {}
for port, cfg in INGRESS_CONFIG.items():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    sockets[s] = (port, cfg)

downstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"[DROS_MULTI_PEP] Successfully bound 4 ingresses: {list(INGRESS_CONFIG.keys())}", flush=True)

def parse_packet_to_execution_request(raw_data: bytes, ingress_port: int) -> Optional[Dict[str, Any]]:
    try:
        req = json.loads(raw_data.decode("utf-8"))
        if isinstance(req, dict) and "action" in req and "principal" in req:
            return req
    except Exception:
        pass

    try:
        mav = mavutil.mavlink.MAVLink(None)
        msgs = mav.parse_buffer(raw_data)
        if msgs and len(msgs) > 0:
            msg = msgs[0]
            msg_type = msg.get_type()
            action = msg_type
            if msg_type == "COMMAND_LONG" and getattr(msg, "command", None) == 400:
                action = "ARM"
            elif msg_type == "PARAM_SET":
                action = "PARAMETER_WRITE"

            return {
                "request_id": f"raw-mavlink-{ingress_port}-{time.time_ns()}",
                "principal": "agent.unauthenticated.companion",
                "capability": f"MAVLINK_{action}",
                "action": action,
                "target": {"interface": "mavlink.udp", "endpoint": f"127.0.0.1:{ingress_port}"},
                "payload": msg.to_dict(),
                "runtime_posture": {"posture_ref": "self-asserted-untrusted"},
                "provenance": {"provenance_ref": "self-asserted-none"},
                "policy_context": {"version": "v0.3"},
                "expiry": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 60)),
                "arg_hash": "uncomputed"
            }
    except Exception:
        pass

    return None

def compile_action_to_mavlink_frame(action: str, payload: Dict[str, Any]) -> bytes:
    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 254
    mav.srcComponent = 190

    if action == "ARM":
        msg = mav.command_long_encode(1, 1, 400, 0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return msg.pack(mav)
    elif action == "DISARM":
        msg = mav.command_long_encode(1, 1, 400, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return msg.pack(mav)
    elif action == "PARAMETER_WRITE":
        p_name = payload.get("param_id", "")
        p_val = float(payload.get("param_value", 0.0))
        p_type = int(payload.get("param_type", mavutil.mavlink.MAV_PARAM_TYPE_REAL32))
        msg = mav.param_set_encode(1, 1, p_name.encode("ascii") if isinstance(p_name, str) else p_name, p_val, p_type)
        return msg.pack(mav)
    elif action == "READ_TELEMETRY":
        msg = mav.heartbeat_encode(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        return msg.pack(mav)
    elif action == "CAMERA_TRIGGER":
        msg = mav.command_long_encode(1, 1, 203, 0, 0, 0, 0, 0, 1, 0, 0)
        return msg.pack(mav)
    elif action == "GIMBAL_CONTROL":
        msg = mav.command_long_encode(1, 1, 205, 0, 0, 0, 0, 0, 0, 0, 2)
        return msg.pack(mav)
    else:
        raise ValueError(f"UNSUPPORTED_MAVLINK_TRANSLATION: Action '{action}' has no deterministic binary MAVLink mapping")

while True:
    try:
        readable, _, _ = select.select(list(sockets.keys()), [], [], 0.5)
        for s in readable:
            data, addr = s.recvfrom(65535)
            if not data:
                continue

            ingress_port, cfg = sockets[s]
            t_recv = time.time_ns()
            req = parse_packet_to_execution_request(data, ingress_port)

            if not req:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"BLOCKED:{t_recv}:{ingress_port}:none:none:none:none:none:MALFORMED_UNPARSEABLE_WIRE_BYTES\n")
                    f.flush()
                continue

            req_id = req.get("request_id", "unknown")
            action = req.get("action", "unknown")
            principal = req.get("principal", "unknown")

            verdict = adapter.evaluate_and_authorize(req)

            if verdict.get("verdict") == "ALLOW":
                target_host = cfg["target_host"]
                target_port = cfg["target_port"]
                try:
                    mavlink_bytes = compile_action_to_mavlink_frame(action, req.get("payload", {}))
                    frame_sha256 = hashlib.sha256(mavlink_bytes).hexdigest()
                    downstream_sock.sendto(mavlink_bytes, (target_host, target_port))
                    with open(log_path, "a", encoding="utf-8") as f:
                        # Transaction Correlation Format:
                        # FORWARDED:timestamp_ns:ingress_port:req_id:principal:action:target_port:frame_sha256:POLICY_AUTHORIZED
                        f.write(f"FORWARDED:{t_recv}:{ingress_port}:{req_id}:{principal}:{action}:{target_port}:{frame_sha256}:POLICY_AUTHORIZED\n")
                        f.flush()
                except Exception as ve:
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"BLOCKED:{t_recv}:{ingress_port}:{req_id}:{principal}:{action}:{target_port}:none:TRANSLATION_FAILED:{ve}\n")
                        f.flush()
            else:
                reason = verdict.get("reason", "UNKNOWN_DENIAL")
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"BLOCKED:{t_recv}:{ingress_port}:{req_id}:{principal}:{action}:none:none:{reason}\n")
                    f.flush()

    except Exception as e:
        print(f"[DROS_MULTI_PEP] Loop error: {e}", flush=True)
