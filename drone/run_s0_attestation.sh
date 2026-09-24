#!/usr/bin/env bash
set -e

mkdir -p /home/ai_user/px4_run
cd /home/ai_user/px4_run

# 1. Binary identity
echo "=== BINARY IDENTIFICATION ==="
BIN_PATH="/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/bin/px4"
file "$BIN_PATH"
BIN_HASH=$(sha256sum "$BIN_PATH" | awk '{print $1}')
echo "SHA256: $BIN_HASH"

# 2. Launch native daemon process
/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/bin/px4 -d /home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/etc > px4.stdout.log 2> px4.stderr.log &
PX4_PID=$!
sleep 3

echo "=== RUNTIME PROCESS ATTESTATION ==="
echo "PID: $PX4_PID"
EXE_PATH=$(readlink -f /proc/$PX4_PID/exe)
echo "EXE_PATH: $EXE_PATH"
CMDLINE=$(cat /proc/$PX4_PID/cmdline | tr '\0' ' ')
echo "CMDLINE: $CMDLINE"
START_TIME=$(ps -p $PX4_PID -o lstart=)
echo "START_TIME: $START_TIME"

echo "=== LISTENING UDP SOCKETS (SOCKET INVENTORY) ==="
ss -lunp | grep "$PX4_PID"

echo "=== STDOUT SAMPLE ==="
head -n 25 px4.stdout.log

echo "=== STDERR SAMPLE ==="
head -n 25 px4.stderr.log

# Cleanup
kill -9 $PX4_PID 2>/dev/null || true
echo "=== CLEANUP DONE ==="
