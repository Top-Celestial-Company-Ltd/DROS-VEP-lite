#!/usr/bin/env python3
import socket
import time
import sys
from pymavlink import mavutil

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind(('127.0.0.1', 14540))
except Exception as e:
    print(f"FAILED TO BIND 14540: {e}")
    sys.exit(1)

mav = mavutil.mavlink.MAVLink(None)
# Send heartbeat from onboard computer to PX4 on 14580
msg = mav.heartbeat_encode(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
sock.sendto(msg.pack(mav), ('127.0.0.1', 14580))
print("SENT HEARTBEAT TO PX4 AT 127.0.0.1:14580")

sock.settimeout(2.5)
try:
    data, addr = sock.recvfrom(2048)
    print(f"SUCCESS: Received {len(data)} bytes from PX4 at {addr}")
    m = mav.parse_buffer(data)
    if m:
        for item in m:
            print("Decoded message from PX4:", item.get_type())
except Exception as e:
    print("RECV TIMEOUT OR ERROR:", e)
finally:
    sock.close()
