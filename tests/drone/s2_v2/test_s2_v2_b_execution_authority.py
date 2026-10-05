# -*- coding: utf-8 -*-
"""
Milestone M1.1 S2-B (Canonical v2.1 Rev 4):
Command Execution Authority Classification with Independent Observation
and Verified Cross-Session Kernel Socket Ownership.

Invariant Contracts:
  - I-B1: Strict Downstream Consumption from S2-A artifact only.
  - I-B2: Socket Isolation (Sock_attack != Sock_obs; distinct FDs & ephemeral ports).
  - I-B3: Independent Observation Transaction (Req_attack != Req_obs; distinct TxIDs).
  - I-B4: Anti-Self-Attestation (ACK != Mutation Proof; attack socket replies/bytes sent
          are strictly prohibited from proving state mutation).
  - I-B5: Closed Authority Taxonomy (EXECUTION_CAPABLE, NON_EXECUTION, UNREACHABLE, INDETERMINATE).
  - I-B6: No Endpoint Reinterpretation (Original S2-A endpoint_key preserved verbatim).
  - I-B7: Non-flight-critical Reversible Parameter Mutation (SYS_HITL).
  - I-B8: Clean-Room Baseline per Stage (Exact PID lifecycle management).
  - I-B9: Quadruple-Gated Authority:
          (Delta != 0 AND Full Temporal Ordering == True AND Reversibility Verified == True
           AND Current-Session Kernel Ownership Verified == True).
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
S2_B_ARTIFACT = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_authority.json",
)
S2_B_RAW_KERNEL_LOG = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_kernel_ss_raw.log",
)

os.makedirs(EVIDENCE_DIR, exist_ok=True)


def utc_timestamp():
    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(),
    )


def compute_sha256(filepath: str) -> str:
    digest = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


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
        if pid in {current_pid, parent_pid}:
            continue
        px4_conflict = bool(
            re.search(
                r"(?:^|\s|/)(?:px4)(?:\s|$)",
                args,
            )
        )
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
        f"active before S2-B: {conflicts}."
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
    assert os.path.exists(PX4_BIN), f"PX4 binary not found: {PX4_BIN}"
    assert os.path.exists(PX4_ETC), f"PX4 ETC directory not found: {PX4_ETC}"

    proc = subprocess.Popen(
        [PX4_BIN, "-d", PX4_ETC],
        cwd=PX4_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3.0)
    assert proc.poll() is None, "PX4 failed to remain alive during fixture setup."
    proc._s2_precondition = precondition
    yield proc

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


def audit_current_session_px4_udp_sockets(target_pid: int):
    """
    Cross-Session Kernel Ownership Audit:
    Executes raw `ss -u -a -n -p -H` on the active S2-B session host to capture
    current UDP sockets attributed by kernel to target_pid.
    Preserves raw stdout for audit trail.
    """
    ss_cmd = ["ss", "-u", "-a", "-n", "-p", "-H"]
    captured_at = utc_timestamp()
    res = subprocess.run(
        ss_cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    raw_stdout = res.stdout
    raw_bytes = raw_stdout.encode("utf-8")
    with open(S2_B_RAW_KERNEL_LOG, "wb") as f:
        f.write(raw_bytes)
    assert res.returncode == 0, (
        f"S2-B kernel socket audit failed: returncode={res.returncode}, "
        f"stderr={res.stderr!r}"
    )

    discovered = []
    seen = set()
    for line in raw_stdout.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        pids = [
            int(pid)
            for pid in re.findall(r"pid=(\d+)", line_clean)
        ]
        if target_pid not in pids:
            continue
        parts = line_clean.split()
        if len(parts) < 5:
            continue
        socket_state = parts[0]
        local_addr_full = parts[3]
        peer_addr_full = parts[4]
        host, port = parse_local_endpoint(local_addr_full)
        if host is None or port is None:
            continue
        key = (target_pid, local_addr_full, peer_addr_full, socket_state)
        if key in seen:
            continue
        seen.add(key)
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

    metadata = {
        "command": " ".join(ss_cmd),
        "captured_at_iso": captured_at,
        "raw_stdout_file": S2_B_RAW_KERNEL_LOG,
        "raw_stdout_sha256": compute_sha256_bytes(raw_bytes),
        "target_pid": target_pid,
        "active_sockets_count": len(discovered),
    }
    return metadata, discovered


def drain_socket_nonblocking(sock: socket.socket):
    """
    Non-blocking drain to purge any stale packets buffered in kernel UDP queue.
    Guarantees subsequent reads observe only packets arriving strictly after drain.
    """
    sock.setblocking(False)
    while True:
        try:
            sock.recvfrom(4096)
        except (BlockingIOError, socket.error):
            break
    sock.setblocking(True)
    sock.settimeout(1.0)


def query_param_observation(
    obs_sock: socket.socket,
    obs_mav: mavutil.mavlink.MAVLink,
    target_host: str,
    target_port: int,
    param_name: str,
    tx_id: str,
    timeout: float = 2.0,
):
    """
    Independent Observation Transaction:
    Sends PARAM_REQUEST_READ from Observation Socket and captures response.
    Observation response provenance notes:
      - Bound to specific parameter name (param_name).
      - Filtered strictly within temporal freshness window [t_request_ns, t_response_ns].
      - MAVLink does not provide request-matching correlation IDs; correlation
        is established via temporal freshness and parameter identity.
    """
    drain_socket_nonblocking(obs_sock)
    obs_sock.settimeout(0.4)

    req_msg = obs_mav.param_request_read_encode(
        1, 1, param_name.encode("utf-8"), -1
    )
    req_bytes = req_msg.pack(obs_mav)
    req_sha256 = compute_sha256_bytes(req_bytes)

    t_request_ns = time.time_ns()
    obs_sock.sendto(req_bytes, (target_host, target_port))

    t_deadline = time.time() + timeout
    observed_val = None
    observed_type = None
    resp_sha256 = None

    while time.time() < t_deadline:
        try:
            data, _ = obs_sock.recvfrom(4096)
            msgs = obs_mav.parse_buffer(data)
            if msgs:
                for m in msgs:
                    if m.get_type() == "PARAM_VALUE":
                        p_id = m.param_id
                        if isinstance(p_id, bytes):
                            p_id = p_id.decode("utf-8", errors="ignore")
                        p_id = p_id.rstrip("\x00")
                        if p_id == param_name:
                            observed_val = float(m.param_value)
                            observed_type = int(m.param_type)
                            resp_sha256 = compute_sha256_bytes(data)
                            break
            if observed_val is not None:
                break
        except socket.timeout:
            continue
        except Exception:
            break

    t_response_ns = time.time_ns()

    return {
        "tx_id": tx_id,
        "socket_fd": obs_sock.fileno(),
        "local_port": obs_sock.getsockname()[1],
        "parameter_name": param_name,
        "t_request_ns": t_request_ns,
        "t_response_ns": t_response_ns,
        "freshness_window_ms": round((t_response_ns - t_request_ns) / 1e6, 2),
        "observed_value": observed_val,
        "param_type": observed_type,
        "request_sha256": req_sha256,
        "response_sha256": resp_sha256,
        "success": (observed_val is not None),
        "provenance_limitation": (
            "MAVLink lacks protocol request-response correlation tokens; "
            "observation causality is bounded by temporal freshness and parameter identity."
        ),
    }


def send_attack_mutation(
    atk_sock: socket.socket,
    atk_mav: mavutil.mavlink.MAVLink,
    target_host: str,
    target_port: int,
    param_name: str,
    target_value: float,
    param_type: int,
    tx_id: str,
):
    """
    Attack Transaction:
    Sends PARAM_SET from Attack Socket.
    Records transmission timestamp and packet sha256.
    Anti-Self-Attestation invariant: does NOT use incoming packets on atk_sock
    as proof of mutation.
    """
    drain_socket_nonblocking(atk_sock)
    atk_sock.settimeout(0.3)

    mut_msg = atk_mav.param_set_encode(
        1, 1, param_name.encode("utf-8"), float(target_value), int(param_type)
    )
    mut_bytes = mut_msg.pack(atk_mav)
    payload_sha256 = compute_sha256_bytes(mut_bytes)

    t_sent_ns = time.time_ns()
    bytes_sent = atk_sock.sendto(mut_bytes, (target_host, target_port))

    # Unsolicited return packet to atk_sock is logged strictly as raw traffic,
    # never as state mutation proof.
    raw_reply_types = []
    try:
        data, _ = atk_sock.recvfrom(4096)
        msgs = atk_mav.parse_buffer(data)
        if msgs:
            raw_reply_types = [m.get_type() for m in msgs]
    except Exception:
        pass

    t_finished_ns = time.time_ns()

    return {
        "tx_id": tx_id,
        "socket_fd": atk_sock.fileno(),
        "local_port": atk_sock.getsockname()[1],
        "command": "PARAM_SET",
        "parameter_name": param_name,
        "target_value": target_value,
        "param_type": param_type,
        "t_sent_ns": t_sent_ns,
        "t_finished_ns": t_finished_ns,
        "bytes_sent": bytes_sent,
        "payload_sha256": payload_sha256,
        "raw_replies_observed": raw_reply_types,
    }


def evaluate_endpoint_authority(
    endpoint_data: dict,
    current_test_pid: int,
    upstream_s2_a_pid: int,
    current_session_sockets: list,
):
    """
    Rigorous evaluation of execution authority on a single S2-A endpoint.
    Strictly enforces:
      - I-B2: Socket Isolation (obs_sock != atk_sock)
      - I-B3: Independent Observation Transaction (Req_atk != Req_obs)
      - I-B4: Anti-Self-Attestation (ACK/bytes sent != Mutation Proof)
      - I-B5: Closed Authority Taxonomy
      - I-B6: Preserve upstream endpoint_key identity verbatim
      - I-B9: Quadruple-Gated Authority:
              (Delta != 0 AND Full Temporal Ordering == True
               AND Reversibility Verified == True AND Current-Session Ownership == True)
    """
    upstream_key = endpoint_data["endpoint_key"]
    assert upstream_key[0] == upstream_s2_a_pid, (
        f"PID mismatch in upstream endpoint key: key PID={upstream_key[0]} "
        f"!= S2-A recorded PID={upstream_s2_a_pid}"
    )

    protocol_observed = endpoint_data.get("protocol_observed", False)
    liveness_probe = endpoint_data.get("protocol_liveness", {})
    probe_host = liveness_probe.get("probe_host", "127.0.0.1")
    probe_port = liveness_probe.get("probe_port", endpoint_data.get("port"))
    probe_target = liveness_probe.get("probe_target", f"{probe_host}:{probe_port}")
    socket_state = endpoint_data.get("state", "UNKNOWN")
    discovered_local = endpoint_data.get("discovered_local_endpoint", "")
    discovered_peer = endpoint_data.get("discovered_peer_endpoint", "")

    # Cross-Session Kernel Ownership Verification:
    # Check if current_test_pid actually owns this endpoint topology in current session.
    matched_current_socket = None
    for s in current_session_sockets:
        if (
            s["local_address"] == discovered_local
            and s["peer_address"] == discovered_peer
            and s["state"] == socket_state
            and s["owner_pid"] == current_test_pid
        ):
            matched_current_socket = s
            break

    current_session_mapping = {
        "mapping_verified": (matched_current_socket is not None),
        "current_session_owner_pid": current_test_pid,
        "current_session_endpoint_key": (
            matched_current_socket["endpoint_key"]
            if matched_current_socket
            else None
        ),
        "raw_kernel_socket_record": (
            matched_current_socket["raw_socket_record"]
            if matched_current_socket
            else None
        ),
    }

    # Eligibility Check
    if not protocol_observed:
        if socket_state == "ESTAB" or (discovered_peer and discovered_peer != "0.0.0.0:*"):
            return {
                "endpoint_key": upstream_key,
                "current_session_mapping": current_session_mapping,
                "probe_target": probe_target,
                "eligibility": "NON_PROTOCOL_CAPABLE",
                "authority_verdict": "UNREACHABLE",
                "verdict_rationale": (
                    "The discovered endpoint was not protocol-capable under the S2-A probe method, "
                    "and its kernel-observed connected peer state did not expose an independently "
                    "probeable listening ingress surface. No execution-authority mutation probe was attempted."
                ),
                "transactions": None,
                "temporal_ordering_valid": None,
                "state_delta": None,
                "reversibility_verified": None,
            }
        else:
            return {
                "endpoint_key": upstream_key,
                "current_session_mapping": current_session_mapping,
                "probe_target": probe_target,
                "eligibility": "NON_PROTOCOL_CAPABLE",
                "authority_verdict": "INDETERMINATE",
                "verdict_rationale": (
                    "No protocol liveness observed during discovery window; "
                    "insufficient evidence to classify as UNREACHABLE or NON_EXECUTION."
                ),
                "transactions": None,
                "temporal_ordering_valid": None,
                "state_delta": None,
                "reversibility_verified": None,
            }

    # Verify that the active PX4 process in this session actually owns the endpoint before probing
    if not current_session_mapping["mapping_verified"]:
        return {
            "endpoint_key": upstream_key,
            "current_session_mapping": current_session_mapping,
            "probe_target": probe_target,
            "eligibility": "PROTOCOL_CAPABLE",
            "authority_verdict": "INDETERMINATE",
            "verdict_rationale": (
                f"S2-A endpoint {upstream_key} could not be proven owned by current "
                f"session PX4 PID {current_test_pid} via kernel ss audit. Gated closed."
            ),
            "transactions": None,
            "temporal_ordering_valid": None,
            "state_delta": None,
            "reversibility_verified": None,
        }

    # Endpoint is protocol-capable & verified owned by current PID -> execute Dual-Transaction Isolation Probe
    obs_sock = None
    atk_sock = None
    param_to_mutate = "SYS_HITL"
    mutation_rationale = {
        "parameter": param_to_mutate,
        "selection_basis": (
            "Standard PX4 Hardware-In-The-Loop toggle parameter. "
            "In-RAM mutable flag with zero aerodynamic or flight-critical impact. "
            "Fully deterministic and reversible."
        ),
        "flight_critical": False,
        "reversible": True,
        "persistent_write": False,
    }

    try:
        # 1. Open Observation Socket (Ephemeral Port A)
        obs_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        obs_sock.bind(("127.0.0.1", 0))
        obs_mav = mavutil.mavlink.MAVLink(None)
        obs_mav.srcSystem = 254
        obs_mav.srcComponent = 191

        # 2. Open Attack Socket (Ephemeral Port B)
        atk_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        atk_sock.bind(("127.0.0.1", 0))
        atk_mav = mavutil.mavlink.MAVLink(None)
        atk_mav.srcSystem = 254
        atk_mav.srcComponent = 192

        # Sanity check socket isolation
        assert obs_sock.fileno() != atk_sock.fileno(), "Socket FD collision detected"
        assert (
            obs_sock.getsockname()[1] != atk_sock.getsockname()[1]
        ), "Ephemeral port collision detected"

        port_id_suffix = f"{probe_port}_{int(time.time()*1000)%100000}"

        # 3. Transaction A: Baseline Observation (Obs Socket)
        tx_obs_base = query_param_observation(
            obs_sock,
            obs_mav,
            probe_host,
            probe_port,
            param_to_mutate,
            tx_id=f"tx-obs-base-{port_id_suffix}",
        )

        if not tx_obs_base["success"]:
            return {
                "endpoint_key": upstream_key,
                "current_session_mapping": current_session_mapping,
                "probe_target": probe_target,
                "eligibility": "PROTOCOL_CAPABLE",
                "mutation_parameter_selection": mutation_rationale,
                "transactions": {
                    "baseline_observation": tx_obs_base,
                    "attack_mutation": None,
                    "post_mutation_observation": None,
                    "restore_mutation": None,
                    "restore_observation": None,
                },
                "temporal_ordering_valid": False,
                "state_delta": None,
                "reversibility_verified": False,
                "authority_verdict": "INDETERMINATE",
                "verdict_rationale": (
                    "Endpoint is protocol-live but baseline PARAM_REQUEST_READ timed out. "
                    "Insufficient evidence to establish read/write parameter channel."
                ),
            }

        val_baseline = tx_obs_base["observed_value"]
        param_type = tx_obs_base["param_type"]
        val_target = 0.0 if val_baseline == 1.0 else 1.0

        # 4. Transaction B: Attack Mutation (Attack Socket)
        time.sleep(0.05)
        tx_atk_mut = send_attack_mutation(
            atk_sock,
            atk_mav,
            probe_host,
            probe_port,
            param_to_mutate,
            target_value=val_target,
            param_type=param_type,
            tx_id=f"tx-atk-mut-{port_id_suffix}",
        )

        # 5. Transaction C: Independent Post-Mutation Observation (Obs Socket)
        time.sleep(0.05)
        tx_obs_post = query_param_observation(
            obs_sock,
            obs_mav,
            probe_host,
            probe_port,
            param_to_mutate,
            tx_id=f"tx-obs-post-{port_id_suffix}",
        )

        val_post = (
            tx_obs_post["observed_value"] if tx_obs_post["success"] else None
        )
        mutation_confirmed = (
            val_post is not None
            and val_post == val_target
            and val_post != val_baseline
        )

        tx_atk_restore = None
        tx_obs_restore = None
        reversibility_verified = False
        full_temporal_causality_valid = False

        if mutation_confirmed:
            # 6. Transaction D: Restore Mutation (Attack Socket)
            time.sleep(0.05)
            tx_atk_restore = send_attack_mutation(
                atk_sock,
                atk_mav,
                probe_host,
                probe_port,
                param_to_mutate,
                target_value=val_baseline,
                param_type=param_type,
                tx_id=f"tx-atk-restore-{port_id_suffix}",
            )

            # 7. Transaction E: Independent Restore Verification (Obs Socket)
            time.sleep(0.05)
            tx_obs_restore = query_param_observation(
                obs_sock,
                obs_mav,
                probe_host,
                probe_port,
                param_to_mutate,
                tx_id=f"tx-obs-restore-{port_id_suffix}",
            )

            # Strict 5-Phase Temporal Causality Verification
            mutation_temporal_valid = (
                tx_obs_base["t_request_ns"]
                < tx_atk_mut["t_sent_ns"]
                < tx_obs_post["t_request_ns"]
            )
            restore_temporal_valid = (
                tx_obs_post["t_response_ns"] <= tx_atk_restore["t_sent_ns"]
                and tx_atk_restore["t_finished_ns"] <= tx_obs_restore["t_request_ns"]
            )
            full_temporal_causality_valid = (
                mutation_temporal_valid is True
                and restore_temporal_valid is True
                and (
                    tx_obs_base["t_request_ns"]
                    < tx_atk_mut["t_sent_ns"]
                    < tx_obs_post["t_request_ns"]
                    < tx_atk_restore["t_sent_ns"]
                    < tx_obs_restore["t_request_ns"]
                )
            )

            # Triple evidence for reversibility:
            # 1. Restore transmission present
            # 2. Restore temporal causality valid
            # 3. Independent observation equals baseline
            reversibility_verified = (
                tx_atk_restore is not None
                and restore_temporal_valid is True
                and tx_obs_restore["success"] is True
                and tx_obs_restore["observed_value"] == val_baseline
            )

            # STAGE TEARDOWN INVARIANT:
            # No unrecorded cleanup mutation is permitted.
            # Clean fixture teardown will terminate PX4 cleanly.

            # I-B9: Quadruple-Gated Authority Evaluation
            if (
                mutation_confirmed is True
                and full_temporal_causality_valid is True
                and reversibility_verified is True
                and current_session_mapping["mapping_verified"] is True
            ):
                verdict = "EXECUTION_CAPABLE"
                rationale = (
                    f"Quadruple-gated execution verified: Current session PID {current_test_pid} "
                    f"proven owner via kernel ss. Independent Observation Socket (port {obs_sock.getsockname()[1]}, "
                    f"FD {obs_sock.fileno()}) observed state delta: {param_to_mutate} changed "
                    f"{val_baseline} -> {val_post} following Attack Socket (port {atk_sock.getsockname()[1]}, "
                    f"FD {atk_sock.fileno()}) mutation. Full 5-phase temporal causality: valid. "
                    "Reversibility independently verified: True."
                )
            else:
                verdict = "INDETERMINATE"
                rationale = (
                    f"State delta observed ({val_baseline} -> {val_post}), but gating invariant failed "
                    f"(temporal_valid={full_temporal_causality_valid}, reversibility_verified={reversibility_verified}, "
                    f"ownership_verified={current_session_mapping['mapping_verified']}). "
                    "Fail-safe default to INDETERMINATE."
                )
        else:
            verdict = "INDETERMINATE"
            rationale = (
                "Attack transaction sent but post-observation did not confirm intended state delta "
                f"(baseline={val_baseline}, observed_post={val_post}). In the absence of an explicit, "
                "independently verified negative-evidence receipt, this cannot be deterministically "
                "classified as NON_EXECUTION and defaults safely to INDETERMINATE."
            )

        return {
            "endpoint_key": upstream_key,
            "current_session_mapping": current_session_mapping,
            "probe_target": probe_target,
            "eligibility": "PROTOCOL_CAPABLE",
            "mutation_parameter_selection": mutation_rationale,
            "transactions": {
                "baseline_observation": tx_obs_base,
                "attack_mutation": tx_atk_mut,
                "post_mutation_observation": tx_obs_post,
                "restore_mutation": tx_atk_restore,
                "restore_observation": tx_obs_restore,
            },
            "temporal_ordering_valid": full_temporal_causality_valid,
            "state_delta": {
                "baseline_value": val_baseline,
                "target_value": val_target,
                "observed_post_value": val_post,
                "mutation_confirmed": mutation_confirmed,
            },
            "reversibility_verified": reversibility_verified,
            "authority_verdict": verdict,
            "verdict_rationale": rationale,
        }

    finally:
        if obs_sock is not None:
            try:
                obs_sock.close()
            except Exception:
                pass
        if atk_sock is not None:
            try:
                atk_sock.close()
            except Exception:
                pass


def test_s2_v2_b_execution_authority_classification(px4_dynamic_env):
    """
    S2-B Canonical Test Suite.
    Ingests S2-A artifact, performs live cross-session kernel ownership audit,
    applies Dual-Transaction Isolation Engine, and produces machine-auditable evidence.
    """
    px4_proc = px4_dynamic_env
    assert px4_proc.poll() is None, "PX4 died unexpectedly before S2-B test."

    assert os.path.exists(S2_A_ARTIFACT), f"Missing S2-A artifact: {S2_A_ARTIFACT}"
    with open(S2_A_ARTIFACT, "r", encoding="utf-8") as f:
        s2_a_data = json.load(f)

    s2_a_sha256 = compute_sha256(S2_A_ARTIFACT)
    upstream_s2_a_pid = s2_a_data.get("px4_pid")
    assert isinstance(upstream_s2_a_pid, int), "S2-A artifact lacks valid px4_pid."

    discovered_endpoints = s2_a_data.get("discovered_endpoints", [])
    assert discovered_endpoints, "S2-A artifact contains zero discovered endpoints."

    # Live Cross-Session Kernel Ownership Audit
    kernel_meta, current_session_sockets = audit_current_session_px4_udp_sockets(
        px4_proc.pid
    )
    assert current_session_sockets, (
        f"Active PX4 PID {px4_proc.pid} has zero kernel-attributed UDP sockets."
    )

    evaluations = []
    for endpoint in discovered_endpoints:
        evaluation = evaluate_endpoint_authority(
            endpoint,
            current_test_pid=px4_proc.pid,
            upstream_s2_a_pid=upstream_s2_a_pid,
            current_session_sockets=current_session_sockets,
        )
        evaluations.append(evaluation)

    summary_counts = {
        "execution_capable_count": sum(
            1 for e in evaluations if e["authority_verdict"] == "EXECUTION_CAPABLE"
        ),
        "non_execution_count": sum(
            1 for e in evaluations if e["authority_verdict"] == "NON_EXECUTION"
        ),
        "unreachable_count": sum(
            1 for e in evaluations if e["authority_verdict"] == "UNREACHABLE"
        ),
        "indeterminate_count": sum(
            1 for e in evaluations if e["authority_verdict"] == "INDETERMINATE"
        ),
    }

    evidence_payload = {
        "stage": "M1.1-S2-B (Canonical v2.1 Rev 4)",
        "epistemic_boundary": (
            "S2-B evaluates command execution authority of endpoints discovered strictly "
            "by S2-A using isolated Attack and Observation sockets. "
            "Active session kernel ownership of S2-A endpoints is empirically verified via ss. "
            "Execution authority is established solely by verified, reversible state delta "
            "under strict 5-phase temporal causality. S2-B does NOT configure PEP, firewalls, or policy enforcement."
        ),
        "s2_a_source": {
            "artifact_file": S2_A_ARTIFACT,
            "artifact_sha256": s2_a_sha256,
            "discovered_endpoints_count": len(discovered_endpoints),
            "upstream_s2_a_px4_pid": upstream_s2_a_pid,
        },
        "s2_b_execution_context": {
            "current_test_px4_pid": px4_proc.pid,
            "current_session_kernel_audit": kernel_meta,
            "cross_session_topology_verified": all(
                ev["current_session_mapping"]["mapping_verified"]
                for ev in evaluations
                if ev.get("eligibility") == "PROTOCOL_CAPABLE"
            ),
        },
        "tested_endpoints_count": len(evaluations),
        "taxonomy_summary": summary_counts,
        "endpoint_authority_evaluations": evaluations,
        "timestamp_iso": utc_timestamp(),
    }

    with open(S2_B_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(evidence_payload, f, indent=2, ensure_ascii=False)

    assert os.path.exists(S2_B_ARTIFACT), f"Failed to persist {S2_B_ARTIFACT}"
    print(
        f"S2_B_EVALUATION_PERSISTED: tested={len(evaluations)}, "
        f"summary={summary_counts}"
    )
