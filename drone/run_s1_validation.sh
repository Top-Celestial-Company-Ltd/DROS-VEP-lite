#!/usr/bin/env bash
set -e

mkdir -p /home/ai_user/dros_drone_real/reports/evidence/drone/m1_1
EVID_DIR="/home/ai_user/dros_drone_real/reports/evidence/drone/m1_1"
PX4_BIN="/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/bin/px4"
PX4_ETC="/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/etc"
VENV_PY="/home/ai_user/dros_drone_real/venv/bin/python3"

echo "=== M1.1-S1 EXECUTION PATH VALIDATION ==="
echo "Date UTC: $(date -u)"

# 1. Clean previous runs
pkill -9 px4 2>/dev/null || true
pkill -f "pep_proxy.py" 2>/dev/null || true
sleep 1

# 2. Launch real C++ PX4 SITL process
cd /home/ai_user/px4_run
$PX4_BIN -d $PX4_ETC > px4_s1.stdout.log 2> px4_s1.stderr.log &
PX4_PID=$!
sleep 3

echo "PX4_PID: $PX4_PID"
EXE_PATH=$(readlink -f /proc/$PX4_PID/exe)
echo "EXE_PATH: $EXE_PATH"
PX4_HASH=$(sha256sum $EXE_PATH | awk '{print $1}')
echo "PX4_HASH: $PX4_HASH"

# Check sockets
echo "--- Listening sockets of PX4 ---"
ss -lunp | grep "$PX4_PID"

# 3. Test bidirectional MAVLink exchange on 14580 via venv python
echo "--- Testing MAVLink heartbeat exchange on 14580 ---"
$VENV_PY /home/ai_user/probe_px4_comm.py

# Cleanup
kill -9 $PX4_PID 2>/dev/null || true
echo "=== M1.1-S1 RUN FINISHED ==="
