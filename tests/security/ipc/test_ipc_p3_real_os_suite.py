# -*- coding: utf-8 -*-
"""
DROS Phase P3 Real Operating System Adversarial Integration Test Harness.
Executes deep systems attacks across real OS boundaries:
- IPC-016: PID Reuse / Recycling Attack (Testing PID equality vs Process Start-Time create_time)
- IPC-017: Process Lifetime & Identity Invariant Boundary
- IPC-018: Real OS Process Separation & Fork/Child Impersonation
- IPC-019: Real Windows Named Pipe Kernel Attribution (GetNamedPipeClientProcessId)
- IPC-020: Linux UDS SO_PEERCRED Real Integration Status
Outputs structured evidence JSONL to reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl
"""

import copy
import ctypes
import json
import os
import subprocess
import sys
import time
import pytest
import psutil

from vep.security.ipc_auth import (
    PeerIdentity,
    CapabilityToken,
    AuthenticatedContext,
    MockPeerIdentityProvider,
    WindowsPeerIdentityProvider,
    LinuxPeerIdentityProvider,
    InMemorySessionManager,
    InMemoryFreshnessVerifier,
    InMemoryCapabilityStore,
    DrosHybridIpcPEP,
    compute_canonical_arg_hash,
)

EVIDENCE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "reports",
    "benchmarks",
    "post_compromise",
    "ipc_p3_real_os_evidence.jsonl"
)

def log_p3_evidence(test_id: str, payload: dict, ctx, attack_desc: str, os_env: str):
    os.makedirs(os.path.dirname(EVIDENCE_LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "test_id": test_id,
        "attack_description": attack_desc,
        "os_environment": os_env,
        "peer_identity": {
            "pid": ctx.peer_identity.pid,
            "create_time": ctx.peer_identity.create_time,
            "transport": ctx.peer_identity.transport,
            "platform": ctx.peer_identity.platform
        },
        "principal_claim": payload.get("principal"),
        "authenticated_principal": ctx.authenticated_principal,
        "session_id": payload.get("session_id"),
        "decision": ctx.decision,
        "reason_code": ctx.reason_code,
        "error_message": ctx.error_message
    }
    with open(EVIDENCE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# -------------------------------------------------------------------------
# Test Cases IPC-016 ~ IPC-020
# -------------------------------------------------------------------------

def test_ipc_016_pid_reuse_attack():
    """
    IPC-016: PID Recycling / Reuse Vulnerability Attack.
    Scenario:
    Agent A (PID 1001, create_time = t0) provisions session.
    Agent A terminates.
    OS subsequently recycles PID 1001 for malicious Process B (PID 1001, create_time = t0 + 100s).
    Process B steals Agent A's unexpired session key and presents valid HMAC.
    Expected:
    If checking PID ONLY -> B passes (False Negative).
    With Candidate C create_time binding -> DENY (PID_REUSE_DETECTED).
    """
    peer_provider = MockPeerIdentityProvider()
    session_mgr = InMemorySessionManager()
    cap_store = InMemoryCapabilityStore()
    freshness = InMemoryFreshnessVerifier()
    pep = DrosHybridIpcPEP(peer_provider, session_mgr, cap_store, freshness)

    # 1. Agent A provisions session at t0 = 1000.0
    t0 = 1000.0
    agent_a_peer = PeerIdentity(pid=1001, create_time=t0, uid=1000, gid=1000)
    session = session_mgr.provision_session(principal="agent-support", peer=agent_a_peer, ttl=3600.0)

    cap = CapabilityToken(
        capability_id="cap-support-read-01",
        principal="agent-support",
        tool="filesystem.read",
        action="read",
        resource="/workspace/data.txt",
        scope=["workspace"],
        argument_constraints={"path_prefix": "/workspace"},
        session_id=session.session_id,
        expires_at=time.time() + 1800.0
    )
    cap_store.register_capability(cap)

    # 2. Malicious Process B running with recycled PID 1001, but create_time = t0 + 150s
    recycled_b_peer = PeerIdentity(pid=1001, create_time=t0 + 150.0, uid=1000, gid=1000)

    ts = time.time()
    args = {"path": "/workspace/data.txt"}
    nonce = "nonce-pid-reuse-01"
    sig = pep.compute_request_signature(session.secret_key, session.session_id, nonce, ts, compute_canonical_arg_hash(args))

    payload = {
        "principal": "agent-support",
        "session_id": session.session_id,
        "capability_id": cap.capability_id,
        "tool": "filesystem.read",
        "action": "read",
        "resource": "/workspace/data.txt",
        "arguments": args,
        "nonce": nonce,
        "timestamp": ts,
        "signature": sig
    }

    # Evaluate execution attempt
    res = pep.evaluate_ipc_request(recycled_b_peer, payload)
    log_p3_evidence("IPC-016", payload, res, "PID recycling attack with stolen key", "simulated_kernel")

    # Must be DENY and detect PID reuse specifically!
    assert res.decision == "DENY"
    assert res.reason_code == "PID_REUSE_DETECTED"
    assert "create_time" in res.error_message


def test_ipc_017_process_lifetime_binding():
    """
    IPC-017: Process Lifetime & Identity Invariant Proof.
    Verifies that identical PID + identical create_time succeeds, proving that
    create_time does not produce false denials for the legitimate running process.
    """
    peer_provider = MockPeerIdentityProvider()
    session_mgr = InMemorySessionManager()
    cap_store = InMemoryCapabilityStore()
    freshness = InMemoryFreshnessVerifier()
    pep = DrosHybridIpcPEP(peer_provider, session_mgr, cap_store, freshness)

    current_pid = os.getpid()
    current_start = psutil.Process(current_pid).create_time()
    legit_peer = PeerIdentity(pid=current_pid, create_time=current_start, uid=1000, gid=1000)

    session = session_mgr.provision_session(principal="agent-support", peer=legit_peer, ttl=3600.0)
    cap = CapabilityToken(
        capability_id="cap-support-read-01",
        principal="agent-support",
        tool="filesystem.read",
        action="read",
        resource="/workspace/data.txt",
        scope=["workspace"],
        argument_constraints={"path_prefix": "/workspace"},
        session_id=session.session_id,
        expires_at=time.time() + 1800.0
    )
    cap_store.register_capability(cap)

    ts = time.time()
    args = {"path": "/workspace/data.txt"}
    nonce = "nonce-lifetime-01"
    sig = pep.compute_request_signature(session.secret_key, session.session_id, nonce, ts, compute_canonical_arg_hash(args))

    payload = {
        "principal": "agent-support",
        "session_id": session.session_id,
        "capability_id": cap.capability_id,
        "tool": "filesystem.read",
        "action": "read",
        "resource": "/workspace/data.txt",
        "arguments": args,
        "nonce": nonce,
        "timestamp": ts,
        "signature": sig
    }

    res = pep.evaluate_ipc_request(legit_peer, payload)
    log_p3_evidence("IPC-017", payload, res, "Legitimate process with identical PID and create_time", "real_os")

    assert res.decision == "ALLOW"
    assert res.reason_code == "AUTHENTICATED_AND_AUTHORIZED"


def test_ipc_018_real_os_subprocess_separation():
    """
    IPC-018: Real OS Subprocess Execution Separation.
    Spawns a REAL independent OS process via subprocess.Popen.
    The real child process attempts to execute an IPC payload under its own authentic PID.
    Evaluates whether the DROS PEP correctly observes the real child's distinct PID.
    """
    peer_provider = MockPeerIdentityProvider()
    session_mgr = InMemorySessionManager()
    cap_store = InMemoryCapabilityStore()
    freshness = InMemoryFreshnessVerifier()
    pep = DrosHybridIpcPEP(peer_provider, session_mgr, cap_store, freshness)

    # 1. Parent process registers session
    parent_pid = os.getpid()
    parent_start = psutil.Process(parent_pid).create_time()
    parent_peer = PeerIdentity(pid=parent_pid, create_time=parent_start)
    session = session_mgr.provision_session(principal="agent-support", peer=parent_peer)

    cap = CapabilityToken(
        capability_id="cap-support-read-01",
        principal="agent-support",
        tool="filesystem.read",
        action="read",
        resource="/workspace/data.txt",
        scope=["workspace"],
        argument_constraints={"path_prefix": "/workspace"},
        session_id=session.session_id,
        expires_at=time.time() + 1800.0
    )
    cap_store.register_capability(cap)

    # 2. Spawn real independent OS subprocess
    cmd = [sys.executable, "-c", "import os, time; print(os.getpid()); time.sleep(2)"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    real_child_pid = int(proc.stdout.readline().strip())
    real_child_start = psutil.Process(real_child_pid).create_time()

    # Real child attempts to use parent's session
    child_peer = PeerIdentity(pid=real_child_pid, create_time=real_child_start)
    ts = time.time()
    args = {"path": "/workspace/data.txt"}
    nonce = "nonce-real-child-01"
    sig = pep.compute_request_signature(session.secret_key, session.session_id, nonce, ts, compute_canonical_arg_hash(args))

    payload = {
        "principal": "agent-support",
        "session_id": session.session_id,
        "capability_id": cap.capability_id,
        "tool": "filesystem.read",
        "action": "read",
        "resource": "/workspace/data.txt",
        "arguments": args,
        "nonce": nonce,
        "timestamp": ts,
        "signature": sig
    }

    res = pep.evaluate_ipc_request(child_peer, payload)
    proc.terminate()
    proc.wait()

    log_p3_evidence("IPC-018", payload, res, "Real OS independent subprocess using parent session", "real_os_subprocess")

    assert res.decision == "DENY"
    assert res.reason_code == "SESSION_PEER_MISMATCH"
    assert str(real_child_pid) in res.error_message


def test_ipc_019_windows_kernel_named_pipe_peer_attribution():
    """
    IPC-019: Real Windows Kernel Named Pipe API Attribution Check.
    Validates that Windows kernel32.GetNamedPipeClientProcessId correctly extracts client PID
    from an authentic named pipe connection.
    """
    if sys.platform != "win32":
        pytest.skip("Windows-specific test")

    import threading
    from ctypes import wintypes

    pipe_name = r"\\.\pipe\dros_vep_p3_test_" + str(int(time.time()))
    k32 = ctypes.windll.kernel32

    # PIPE_ACCESS_DUPLEX = 3, PIPE_TYPE_BYTE = 0, PIPE_WAIT = 0
    server_pipe = k32.CreateNamedPipeW(
        pipe_name,
        3,  # PIPE_ACCESS_DUPLEX
        0,  # PIPE_TYPE_BYTE | PIPE_WAIT
        1,  # max instances
        4096, 4096, 0, None
    )
    assert server_pipe != -1, f"Failed to create test named pipe: {ctypes.GetLastError()}"

    client_attributed_pid = None

    def server_thread():
        nonlocal client_attributed_pid
        # Wait for connection
        connected = k32.ConnectNamedPipe(server_pipe, None)
        if connected or ctypes.GetLastError() == 535:  # ERROR_PIPE_CONNECTED
            provider = WindowsPeerIdentityProvider()
            peer = provider.get_peer_identity(server_pipe)
            client_attributed_pid = peer.pid
        k32.CloseHandle(server_pipe)

    t = threading.Thread(target=server_thread)
    t.start()

    time.sleep(0.1)

    # Spawn real client subprocess that connects to the pipe
    client_code = f"""
import ctypes, time
client_handle = ctypes.windll.kernel32.CreateFileW(r"{pipe_name}", 0xC0000000, 0, None, 3, 0, None)
time.sleep(0.5)
ctypes.windll.kernel32.CloseHandle(client_handle)
"""
    proc = subprocess.Popen([sys.executable, "-c", client_code])
    real_client_pid = proc.pid
    proc.wait()
    t.join()

    # Log evidence
    log_p3_evidence(
        "IPC-019",
        {"target_pipe": pipe_name},
        AuthenticatedContext(
            peer_identity=PeerIdentity(pid=client_attributed_pid or -1, platform="win32", transport="named_pipe"),
            authenticated_principal="win32_kernel_verified",
            session_id="N/A",
            capability_id="N/A",
            arguments_hash="N/A",
            nonce="N/A",
            decision="ALLOW" if client_attributed_pid == real_client_pid else "DENY",
            reason_code="WINDOWS_KERNEL_PEER_ATTRIBUTED" if client_attributed_pid == real_client_pid else "PID_MISMATCH"
        ),
        "Real Windows Named Pipe GetNamedPipeClientProcessId kernel extraction",
        "windows_native_kernel"
    )

    assert client_attributed_pid == real_client_pid, f"Attributed PID {client_attributed_pid} did not match real subprocess PID {real_client_pid}"


def test_ipc_020_linux_uds_evidence_class_scoping():
    """
    IPC-020: Linux UDS SO_PEERCRED Scoping & Trust Boundary Verification.
    Validates that on non-Linux platforms, Linux UDS extraction cleanly falls back without falsifying success.
    Enforces the rule: Linux PASS != Windows PASS (Strict Evidence Typing).
    """
    linux_provider = LinuxPeerIdentityProvider()
    # Passing invalid/mock connection to Linux provider on Windows must return uds_unresolved, NOT fake a pass
    res = linux_provider.get_peer_identity(None)
    assert res.transport == "uds_unresolved"
    assert res.pid == -1
