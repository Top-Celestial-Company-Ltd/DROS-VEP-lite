# -*- coding: utf-8 -*-
"""
Milestone M1.1 S2-A (Canonical v2.1):
Dynamic PX4 UDP Endpoint Discovery without Predefined Ingress Enumeration.
Invariant Contract:
  - I1: No Predefined Ingress Enumeration.
  - I8: Clean-Room Baseline per Stage.
  - I10: Empirically Bounded Claims.
Evidence properties:
  - Complete raw `ss -u -a -n -p -H` observation is preserved.
  - `ss` command success/failure is recorded.
  - PX4-attributed endpoints are derived from the raw kernel observation.
  - No port-only deduplication.
  - Endpoint identity includes owner PID, local endpoint, peer endpoint, and state.
  - Protocol liveness is reported as `protocol_observed` only.
  - Wildcard bind addresses are explicitly distinguished from actual probe targets.
  - Execution authority is NOT inferred here; that belongs to S2-B.
"""
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
import pytest
from pymavlink import mavutil
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
PX4_DIR = (
    "/home/ai_user/px4_build/PX4-Autopilot/"
    "build/px4_sitl_default"
)
PX4_BIN = f"{PX4_DIR}/bin/px4"
PX4_ETC = f"{PX4_DIR}/etc"
EVIDENCE_DIR = os.path.join(
    BASE_DIR,
    "reports",
    "evidence",
    "drone",
    "m1_1",
    "s2_v2",
)
S2_A_ARTIFACT = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_discovery.json",
)
S2_A_RAW_KERNEL_LOG = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_kernel_ss_raw.log",
)
os.makedirs(EVIDENCE_DIR, exist_ok=True)
def utc_timestamp():
    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(),
    )
def compute_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def check_precondition_cleanliness():
    """
    Clean-room precondition.
    No destructive process cleanup is performed.
    Fail closed if an independently running PX4 or DROS PEP process
    is already present before this stage starts.
    """
    res = subprocess.run(
        ["ps", "-eo", "pid=,args="],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, (
        "Unable to establish clean-room process precondition: "
        f"ps returncode={res.returncode}, stderr={res.stderr!r}"
    )
    current_pid = os.getpid()
    parent_pid = os.getppid()
    conflicts = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^(\d+)\s+(.*)$", line)
        if not match:
            continue
        pid = int(match.group(1))
        args = match.group(2)
        # Never classify this test process or its immediate shell ancestry
        # merely because the source path contains a protected process name.
        if pid in {current_pid, parent_pid}:
            continue
        # PX4 executable invocation.
        px4_conflict = bool(
            re.search(
                r"(?:^|\s|/)(?:px4)(?:\s|$)",
                args,
            )
        )
        # Explicit PEP process names.
        pep_conflict = (
            "pep_proxy.py" in args
            or "multi_pep_proxy.py" in args
        )
        if px4_conflict or pep_conflict:
            conflicts.append(
                {
                    "pid": pid,
                    "args": args,
                }
            )
    assert not conflicts, (
        "PRECONDITION VIOLATION: conflicting PX4/PEP process already "
        f"active before S2-A: {conflicts}. "
        "Test must execute from a verified clean baseline."
    )
    return {
        "ps_command": "ps -eo pid=,args=",
        "ps_returncode": res.returncode,
        "checked_at_iso": utc_timestamp(),
        "conflicts": conflicts,
    }
@pytest.fixture(scope="module")
def px4_dynamic_env():
    """
    Starts exactly one genuine PX4 SITL process after clean-room validation.
    No pkill / pattern-kill is permitted.
    Teardown only targets the exact PID created by this fixture.
    """
    precondition = check_precondition_cleanliness()
    assert os.path.exists(PX4_BIN), (
        f"PX4 binary not found: {PX4_BIN}"
    )
    assert os.path.exists(PX4_ETC), (
        f"PX4 ETC directory not found: {PX4_ETC}"
    )
    proc = subprocess.Popen(
        [PX4_BIN, "-d", PX4_ETC],
        cwd=PX4_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3.0)
    assert proc.poll() is None, (
        "PX4 failed to remain alive during fixture setup."
    )
    # Expose the precondition as an attribute for the test artifact.
    proc._s2_precondition = precondition
    yield proc
    # Exact-PID teardown only.
    try:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=2.0)
    except Exception:
        try:
            proc.kill()
            proc.wait(timeout=2.0)
        except Exception:
            pass
def parse_local_endpoint(local_address: str):
    """
    Parse an `ss -n` local endpoint.
    Supported examples:
      127.0.0.1:18570
      0.0.0.0:18570
      [::]:18570
      [::1]:18570
      *:18570
    """
    if local_address.startswith("["):
        close_bracket = local_address.find("]")
        if close_bracket == -1:
            return None, None
        host = local_address[1:close_bracket]
        remainder = local_address[close_bracket + 1:]
        if not remainder.startswith(":"):
            return None, None
        port_str = remainder[1:]
    else:
        if ":" not in local_address:
            return None, None
        host, port_str = local_address.rsplit(":", 1)
    try:
        port = int(port_str)
    except ValueError:
        return None, None
    return host, port
def capture_and_parse_kernel_udp_sockets(target_pid: int):
    """
    Complete kernel observation + deterministic PX4 attribution.
    The complete stdout of:
        ss -u -a -n -p -H
    is preserved verbatim before any filtering occurs.
    """
    ss_cmd = [
        "ss",
        "-u",
        "-a",
        "-n",
        "-p",
        "-H",
    ]
    captured_at = utc_timestamp()
    res = subprocess.run(
        ss_cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    raw_stdout = res.stdout
    raw_stderr = res.stderr
    raw_bytes = raw_stdout.encode("utf-8")
    raw_sha256 = compute_sha256_bytes(raw_bytes)
    # Preserve complete stdout exactly as returned.
    with open(
        S2_A_RAW_KERNEL_LOG,
        "wb",
    ) as f:
        f.write(raw_bytes)
    assert res.returncode == 0, (
        "Kernel socket audit failed: "
        f"returncode={res.returncode}, stderr={raw_stderr!r}. "
        f"Raw stdout preserved at {S2_A_RAW_KERNEL_LOG}"
    )
    discovered = []
    seen_endpoints = set()
    for line in raw_stdout.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        # Extract every PID attributed by ss on this socket record.
        pids = [
            int(pid)
            for pid in re.findall(
                r"pid=(\d+)",
                line_clean,
            )
        ]
        if target_pid not in pids:
            continue
        parts = line_clean.split()
        # Expected `ss -H` UDP structure:
        # State Recv-Q Send-Q Local Address:Port Peer Address:Port Process
        if len(parts) < 5:
            continue
        socket_state = parts[0]
        local_addr_full = parts[3]
        peer_addr_full = parts[4]
        host, port = parse_local_endpoint(
            local_addr_full
        )
        if host is None or port is None:
            continue
        endpoint_key = (
            target_pid,
            local_addr_full,
            peer_addr_full,
            socket_state,
        )
        if endpoint_key in seen_endpoints:
            continue
        seen_endpoints.add(endpoint_key)
        discovered.append(
            {
                "endpoint_key": [
                    target_pid,
                    local_addr_full,
                    peer_addr_full,
                    socket_state,
                ],
                "local_address": local_addr_full,
                "peer_address": peer_addr_full,
                "host": host,
                "port": port,
                "state": socket_state,
                "owner_pid": target_pid,
                "raw_socket_record": line_clean,
            }
        )
    kernel_metadata = {
        "command": " ".join(ss_cmd),
        "captured_at_iso": captured_at,
        "returncode": res.returncode,
        "stderr": raw_stderr,
        "raw_stdout_file": S2_A_RAW_KERNEL_LOG,
        "raw_stdout_sha256": raw_sha256,
        "raw_stdout_bytes": len(raw_bytes),
        "total_kernel_lines_observed": len(
            raw_stdout.splitlines()
        ),
        "px4_attributed_socket_count": len(discovered),
        "target_pid": target_pid,
    }
    return kernel_metadata, discovered
def resolve_probe_target(
    host_part: str,
    port: int,
):
    """
    Convert discovered local bind address into an explicit probe target.
    Important epistemic distinction:
      discovered_local_endpoint
            !=
      actual_probe_target
    Wildcard bindings are probed through loopback but remain recorded
    as wildcard bindings in the discovery inventory.
    """
    clean_host = host_part.strip("[]")
    is_ipv6 = ":" in clean_host
    if is_ipv6:
        address_family = socket.AF_INET6
        if clean_host in {
            "",
            "::",
            "*",
        }:
            probe_host = "::1"
        else:
            probe_host = clean_host
    else:
        address_family = socket.AF_INET
        if clean_host in {
            "",
            "0.0.0.0",
            "*",
        }:
            probe_host = "127.0.0.1"
        else:
            probe_host = clean_host
    return {
        "address_family": (
            "AF_INET6"
            if address_family == socket.AF_INET6
            else "AF_INET"
        ),
        "address_family_numeric": address_family,
        "probe_host": probe_host,
        "probe_port": port,
        "probe_target": f"{probe_host}:{port}",
    }
def probe_endpoint_protocol_liveness(
    host_part: str,
    port: int,
    duration_sec: float = 1.0,
):
    """
    Protocol liveness observation only.
    This function does NOT classify execution authority.
    That classification belongs to S2-B.
    """
    probe = resolve_probe_target(
        host_part,
        port,
    )
    sock = None
    try:
        sock = socket.socket(
            probe["address_family_numeric"],
            socket.SOCK_DGRAM,
        )
        sock.settimeout(0.3)
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 254
        mav.srcComponent = 190
        hb = mav.heartbeat_encode(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0,
            0,
            0,
        )
        raw_packet = hb.pack(mav)
        bytes_sent = sock.sendto(
            raw_packet,
            (
                probe["probe_host"],
                port,
            ),
        )
        received_types = []
        received_bytes = 0
        start = time.time()
        while time.time() - start < duration_sec:
            try:
                data, _addr = sock.recvfrom(4096)
                received_bytes += len(data)
                mav_in = mavutil.mavlink.MAVLink(None)
                msgs = mav_in.parse_buffer(data)
                if msgs:
                    for message in msgs:
                        received_types.append(
                            message.get_type()
                        )
            except socket.timeout:
                continue
            except Exception:
                break
        return {
            "probe_target": probe["probe_target"],
            "probe_host": probe["probe_host"],
            "probe_port": probe["probe_port"],
            "address_family": probe["address_family"],
            "bytes_sent": bytes_sent,
            "received_bytes": received_bytes,
            "protocol_observed": bool(received_types),
            "observed_message_types": sorted(
                list(set(received_types))
            ),
        }
    except Exception as exc:
        return {
            "probe_target": probe["probe_target"],
            "probe_host": probe["probe_host"],
            "probe_port": probe["probe_port"],
            "address_family": probe["address_family"],
            "bytes_sent": 0,
            "received_bytes": 0,
            "protocol_observed": False,
            "observed_message_types": [],
            "probe_error": str(exc),
        }
    finally:
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass
def test_s2_v2_a_dynamic_kernel_socket_discovery(
    px4_dynamic_env,
):
    """
    S2-A Canonical Verification.
    1. Clean-room precondition.
    2. Genuine PX4 SITL startup.
    3. Complete kernel UDP observation.
    4. Deterministic PX4 PID attribution.
    5. Endpoint-level identity preservation.
    6. Address-family-aware protocol observation.
    7. No execution-authority conclusion.
    8. Canonical empirical artifact generation.
    """
    px4_proc = px4_dynamic_env
    assert px4_proc.poll() is None, (
        "PX4 process died unexpectedly before discovery."
    )
    kernel_metadata, discovered_endpoints = (
        capture_and_parse_kernel_udp_sockets(
            px4_proc.pid
        )
    )
    assert discovered_endpoints, (
        f"Dynamic discovery yielded zero UDP endpoints "
        f"for PX4 PID {px4_proc.pid}. "
        f"Raw observation preserved at "
        f"{S2_A_RAW_KERNEL_LOG}"
    )
    probed_inventory = []
    for endpoint in discovered_endpoints:
        liveness = probe_endpoint_protocol_liveness(
            endpoint["host"],
            endpoint["port"],
            duration_sec=1.0,
        )
        probed_inventory.append(
            {
                "endpoint_key": endpoint[
                    "endpoint_key"
                ],
                "discovered_local_endpoint": endpoint[
                    "local_address"
                ],
                "discovered_peer_endpoint": endpoint[
                    "peer_address"
                ],
                "host": endpoint["host"],
                "port": endpoint["port"],
                "state": endpoint["state"],
                "owner_pid": endpoint["owner_pid"],
                "raw_socket_record": endpoint[
                    "raw_socket_record"
                ],
                "protocol_liveness": liveness,
                "protocol_observed": liveness[
                    "protocol_observed"
                ],
            }
        )
    evidence_payload = {
        "stage": "M1.1-S2-A (Canonical v2.1)",
        "discovery_method": (
            "DYNAMIC_KERNEL_AUDIT_WITHOUT_PREDEFINED_PORT_LIST"
        ),
        "epistemic_boundary": (
            "S2-A observes kernel-attributed PX4 UDP endpoints "
            "and protocol liveness only. It does not classify "
            "execution authority. Execution-capability proof "
            "belongs to S2-B."
        ),
        "px4_pid": px4_proc.pid,
        "px4_binary_path": PX4_BIN,
        "clean_room_precondition": getattr(
            px4_proc,
            "_s2_precondition",
            {},
        ),
        "kernel_observation": kernel_metadata,
        "discovered_endpoints_count": len(
            probed_inventory
        ),
        "discovered_endpoints": probed_inventory,
        "timestamp_iso": utc_timestamp(),
    }
    with open(
        S2_A_ARTIFACT,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            evidence_payload,
            f,
            indent=2,
            ensure_ascii=False,
        )
    assert os.path.exists(
        S2_A_ARTIFACT
    ), (
        f"Failed to persist {S2_A_ARTIFACT}"
    )
    assert os.path.exists(
        S2_A_RAW_KERNEL_LOG
    ), (
        f"Failed to persist {S2_A_RAW_KERNEL_LOG}"
    )
