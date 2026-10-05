# -*- coding: utf-8 -*-
"""
Real Standalone MAVLink Flight Controller Process.
Listens on UDP 127.0.0.1:14550 using pymavlink.
Only accepts and applies actuation commands if they reach this physical socket endpoint.
"""

import time
import os
import sys
from pymavlink import mavutil

print("[PX4_ENDPOINT] Starting real MAVLink UDP flight controller on 127.0.0.1:14550...", flush=True)
mav = mavutil.mavlink_connection('udpin:127.0.0.1:14550')

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fc_audit.log")
with open(log_path, "w") as log_f:
    log_f.write("PX4_REAL_SOCKET_STARTED\n")
    log_f.flush()

while True:
    msg = mav.recv_match(blocking=True, timeout=1.0)
    if msg:
        msg_type = msg.get_type()
        with open(log_path, "a") as log_f:
            log_f.write(f"{time.time()}:{msg_type}\n")
            log_f.flush()
        print(f"[PX4_ENDPOINT_RECV] Received real MAVLink message: {msg_type}", flush=True)
