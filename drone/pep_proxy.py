# -*- coding: utf-8 -*-
"""
DROS Real Network MAVLink PEP Proxy Process.
Listens on UDP 127.0.0.1:14540 (Target exposed to agent / companion computer).
Evaluates incoming serialized DroneExecutionRequest / MAVLink payloads strictly
through the DROS DroneExecutionAdapter policy engine (6P validation).
Only forwards authorized commands to real flight controller at 127.0.0.1:14550.
"""

import socket
import time
import os
import sys
import json
from typing import Optional, Dict, Any
from pymavlink import mavutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter
from drone.sitl.engine import ExternalNavigationIntegrityService

print("[DROS_PEP_PROXY] Initializing DROS MAVLink PEP Proxy on UDP 127.0.0.1:14540...", flush=True)

# 1. Initialize Upstream Socket (Receives execution requests from Agent)
proxy_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
proxy_in.bind(("127.0.0.1", 14540))

# 2. Downstream MAVLink Connection to Flight Controller (default 127.0.0.1:14550; configurable for PX4 SITL 14580)
FC_HOST = os.environ.get("DROS_FC_HOST", "127.0.0.1")
FC_PORT = int(os.environ.get("DROS_FC_PORT", "14550"))
downstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"[DROS_PEP_PROXY] Downstream Flight Controller target configured as UDP {FC_HOST}:{FC_PORT}", flush=True)

# 3. Instantiate Policy Decision & Enforcement Engine
adapter = DroneExecutionAdapter()
nav_service = ExternalNavigationIntegrityService()
# Register legitimate external authoritative navigation posture
posture_token = nav_service.generate_posture_token()
adapter.register_external_posture(posture_token)

# Persist active posture reference for clients to legitimately discover authoritative posture
posture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "active_posture.json")
with open(posture_path, "w", encoding="utf-8") as pf:
    json.dump(posture_token, pf)

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pep_audit.log")
with open(log_path, "w", encoding="utf-8") as f:
    f.write("DROS_PEP_PROXY_STARTED\n")
    f.flush()

def parse_packet_to_execution_request(raw_data: bytes) -> Optional[Dict[str, Any]]:
    """
    Parses incoming raw bytes into a DroneExecutionRequest structure.
    Supports:
      1. Structured JSON DroneExecutionRequest envelope containing MAVLink/actuation payload.
      2. Direct MAVLink packet translation into synthetic ExecutionRequest.
    """
    # Attempt 1: Direct JSON-serialized ExecutionRequest envelope
    try:
        req = json.loads(raw_data.decode("utf-8"))
        if isinstance(req, dict) and "action" in req and "principal" in req:
            return req
    except Exception:
        pass

    # Attempt 2: Direct raw MAVLink packet -> Extract command & construct untrusted ExecutionRequest
    try:
        mav = mavutil.mavlink.MAVLink(None)
        msgs = mav.parse_buffer(raw_data)
        if msgs and len(msgs) > 0:
            msg = msgs[0]
            msg_type = msg.get_type()
            # Synthesize minimal ExecutionRequest for raw unauthenticated MAVLink packet
            return {
                "request_id": f"raw-mavlink-{time.time_ns()}",
                "principal": "agent.unauthenticated.companion",
                "capability": f"MAVLINK_{msg_type}",
                "action": "ARM" if msg_type == "COMMAND_LONG" and getattr(msg, "command", None) == 400 else msg_type,
                "target": {"interface": "mavlink.udp", "endpoint": "127.0.0.1:14550"},
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
    """
    Ticket-03 Translation Layer:
    Deterministically compiles an authorized DROS action and payload into a
    valid, syntactically and semantically compliant binary MAVLink frame.
    Enforces strict 1-to-1 semantic binding to prevent command translation skew.
    """
    mav = mavutil.mavlink.MAVLink(None)
    mav.srcSystem = 254 # Ground/Companion control system ID
    mav.srcComponent = 190

    if action == "SET_MODE":
        custom_mode = int(payload.get("custom_mode", 4))
        # MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = 1
        msg = mav.set_mode_encode(1, custom_mode, 0)
        return msg.pack(mav)

    elif action == "ARM":
        # MAV_CMD_COMPONENT_ARM_DISARM = 400, param1=1 to arm
        msg = mav.command_long_encode(
            1, 1, # target system, component
            400,  # MAV_CMD_COMPONENT_ARM_DISARM
            0,    # confirmation
            1.0,  # param1 = 1 (ARM)
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        )
        return msg.pack(mav)

    elif action == "DISARM":
        msg = mav.command_long_encode(
            1, 1, 400, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # param1 = 0 (DISARM)
        )
        return msg.pack(mav)

    elif action == "TAKEOFF":
        alt = float(payload.get("altitude", 10.0))
        # MAV_CMD_NAV_TAKEOFF = 22
        msg = mav.command_long_encode(
            1, 1, 22, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, alt
        )
        return msg.pack(mav)

    elif action == "LAND":
        # MAV_CMD_NAV_LAND = 21
        msg = mav.command_long_encode(
            1, 1, 21, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        )
        return msg.pack(mav)

    elif action == "RTL":
        # MAV_CMD_NAV_RETURN_TO_LAUNCH = 20
        msg = mav.command_long_encode(
            1, 1, 20, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        )
        return msg.pack(mav)

    elif action == "READ_TELEMETRY":
        # Standard HEARTBEAT message
        msg = mav.heartbeat_encode(
            mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0, 0
        )
        return msg.pack(mav)

    elif action == "PARAMETER_WRITE":
        p_name = payload.get("param_id", "")
        p_val = float(payload.get("param_value", 0.0))
        p_type = int(payload.get("param_type", mavutil.mavlink.MAV_PARAM_TYPE_REAL32))
        msg = mav.param_set_encode(1, 1, p_name.encode("ascii") if isinstance(p_name, str) else p_name, p_val, p_type)
        return msg.pack(mav)

    else:
        # Strictly reject unmapped actions at translation boundary (fail-closed, no silent fallback)
        raise ValueError(f"UNSUPPORTED_MAVLINK_TRANSLATION: Action '{action}' has no deterministic binary MAVLink mapping")

print("[DROS_PEP_PROXY] Ready. Enforcing 6P policy engine on every network packet...", flush=True)

while True:
    try:
        data, addr = proxy_in.recvfrom(65535)
        if not data:
            continue
        
        t_recv = time.time()
        req = parse_packet_to_execution_request(data)
        
        if not req:
            # Unparseable wire bytes -> Deny by default
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"BLOCKED:{t_recv}:MALFORMED_UNPARSEABLE_WIRE_BYTES\n")
                f.flush()
            print("[DROS_PEP_PROXY] BLOCKED malformed unparseable wire bytes!", flush=True)
            continue

        # CRITICAL: Invoke full DROS Policy Engine (evaluate_and_authorize)
        # Separates PDP authorization verification from downstream execution forwarding
        verdict = adapter.evaluate_and_authorize(req)
        
        if verdict.get("verdict") == "ALLOW":
            # Policy explicitly permitted the execution request -> Forward to real FC
            action = verdict.get("action", "")
            # TOCTOU Defense: Use the identical verified payload object from req
            payload = req.get("payload", {})

            try:
                # Compile into semantically validated binary MAVLink message frame
                mavlink_bytes = compile_action_to_mavlink_frame(action, payload)
                downstream.sendto(mavlink_bytes, (FC_HOST, FC_PORT))
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"FORWARDED:{t_recv}:{action}:{verdict.get('reason')}\n")
                    f.flush()
                print(f"[DROS_PEP_PROXY] FORWARDED authorized packet: {action}", flush=True)
            except ValueError as ve:
                # Fail-closed on translation gap: Drop packet, audit translation failure
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"BLOCKED:{t_recv}:TRANSLATION_LAYER_FAIL_CLOSED:{ve}\n")
                    f.flush()
                print(f"[DROS_PEP_PROXY] BLOCKED: Translation layer failed closed: {ve}", flush=True)
                continue
        else:
            # Policy engine DENIED execution -> Drop packet, audit denial reason
            reason = verdict.get("reason", "UNKNOWN_DENIAL")
            desc = verdict.get("description", "")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"BLOCKED:{t_recv}:{reason}:{desc}\n")
                f.flush()
            print(f"[DROS_PEP_PROXY] BLOCKED by DROS Engine! Reason: {reason} ({desc})", flush=True)
            continue

    except Exception as e:
        print(f"[DROS_PEP_PROXY] Fatal loop exception: {e}", flush=True)
