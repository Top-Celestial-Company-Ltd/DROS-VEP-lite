# -*- coding: utf-8 -*-
"""
DROS Phase P2 Adversarial Test Harness for Loopback IPC Authentication.
Executes the full 15-scenario attack matrix (IPC-001 through IPC-015):
- Payload Spoofing (IPC-001 ~ IPC-002)
- Capability & Principal Mismatch (IPC-003 ~ IPC-004)
- Nonce & Replay Attacks (IPC-005 ~ IPC-006)
- ArgHash Integrity Mutations (IPC-007 ~ IPC-008)
- Expiry & Hot Revocation (IPC-009 ~ IPC-010)
- Endpoint Substitution (IPC-011)
- Same-UID Process Impersonation (IPC-012)
- Session Credential Theft Boundary (IPC-013)
- Inherited Credential Fork (IPC-014)
- Confused Deputy Attack (IPC-015)
Outputs structured evidence JSONL to reports/benchmarks/post_compromise/ipc_p2_evidence.jsonl
"""

import copy
import json
import os
import sys
import time
import pytest

from vep.security.ipc_auth import (
    PeerIdentity,
    CapabilityToken,
    MockPeerIdentityProvider,
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
    "ipc_p2_evidence.jsonl"
)

def log_evidence(test_id: str, payload: dict, ctx, attack_description: str):
    os.makedirs(os.path.dirname(EVIDENCE_LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "test_id": test_id,
        "attack_description": attack_description,
        "platform": sys.platform,
        "peer_identity": {
            "pid": ctx.peer_identity.pid,
            "uid": ctx.peer_identity.uid,
            "transport": ctx.peer_identity.transport
        },
        "principal_claim": payload.get("principal"),
        "authenticated_principal": ctx.authenticated_principal,
        "session_id": payload.get("session_id"),
        "capability_id": payload.get("capability_id"),
        "nonce": payload.get("nonce"),
        "arg_hash": ctx.arguments_hash,
        "decision": ctx.decision,
        "reason_code": ctx.reason_code,
        "error_message": ctx.error_message
    }
    with open(EVIDENCE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

@pytest.fixture
def setup_ipc():
    peer_provider = MockPeerIdentityProvider(PeerIdentity(pid=1001, uid=1000, gid=1000))
    session_manager = InMemorySessionManager()
    capability_store = InMemoryCapabilityStore()
    freshness_verifier = InMemoryFreshnessVerifier()

    pep = DrosHybridIpcPEP(
        peer_provider=peer_provider,
        session_manager=session_manager,
        capability_store=capability_store,
        freshness_verifier=freshness_verifier
    )

    # Register Legitimate Session for Agent-Support (PID 1001)
    legit_peer = PeerIdentity(pid=1001, uid=1000, gid=1000)
    session = session_manager.provision_session(principal="agent-support", peer=legit_peer, ttl=3600.0)

    # Register Legitimate Capability for Agent-Support
    cap = CapabilityToken(
        capability_id="cap-support-read-01",
        principal="agent-support",
        tool="filesystem.read",
        action="read",
        resource="/workspace/data.txt",
        scope=["workspace"],
        argument_constraints={"path_prefix": "/workspace"},
        session_id=session.session_id,
        expires_at=time.time() + 1800.0,
        is_revoked=False,
        delegation_chain=[]
    )
    capability_store.register_capability(cap)

    # Baseline valid payload
    ts = time.time()
    args = {"path": "/workspace/data.txt"}
    arg_hash = compute_canonical_arg_hash(args)
    nonce = "nonce-legit-0001"
    sig = pep.compute_request_signature(session.secret_key, session.session_id, nonce, ts, arg_hash)

    base_payload = {
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

    return {
        "pep": pep,
        "session_manager": session_manager,
        "capability_store": capability_store,
        "freshness_verifier": freshness_verifier,
        "peer_provider": peer_provider,
        "session": session,
        "capability": cap,
        "base_payload": base_payload,
        "legit_peer": legit_peer
    }

# -------------------------------------------------------------------------
# Test Cases IPC-001 ~ IPC-015
# -------------------------------------------------------------------------

def test_ipc_001_principal_spoofing(setup_ipc):
    """IPC-001: Caller changes principal from agent-support to agent-admin. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["principal"] = "agent-admin"  # Attacker self-asserts admin identity

    res = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-001", payload, res, "Principal payload spoofing")

    assert res.decision == "DENY"
    assert res.reason_code == "PRINCIPAL_SPOOFING_DETECTED"
    assert res.authenticated_principal == "agent-support"  # Audit captures true owner

def test_ipc_002_capability_tampering(setup_ipc):
    """IPC-002: Caller requests non-existent or tampered capability. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["capability_id"] = "cap-non-existent"

    res = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-002", payload, res, "Capability tampering / not found")

    assert res.decision == "DENY"
    assert res.reason_code == "CAPABILITY_NOT_FOUND"

def test_ipc_003_cross_principal_capability(setup_ipc):
    """IPC-003: Valid capability belonging to Agent-B presented by Agent-A. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    cap_store = ctx_data["capability_store"]

    # Register billing capability belonging to billing-service
    cap_billing = CapabilityToken(
        capability_id="cap-billing-modify",
        principal="billing-service",
        tool="filesystem.read",
        action="read",
        resource="/workspace/data.txt",
        scope=["billing"],
        argument_constraints={},
        session_id=None,
        expires_at=time.time() + 1800.0
    )
    cap_store.register_capability(cap_billing)

    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["capability_id"] = "cap-billing-modify"

    res = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-003", payload, res, "Cross-principal capability theft")

    assert res.decision == "DENY"
    assert res.reason_code == "CAPABILITY_PRINCIPAL_MISMATCH"

def test_ipc_004_session_peer_mismatch(setup_ipc):
    """IPC-004: Valid session used by another process PID. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])

    rogue_peer = PeerIdentity(pid=9999, uid=1000, gid=1000)  # Same UID, different PID
    res = pep.evaluate_ipc_request(rogue_peer, payload)
    log_evidence("IPC-004", payload, res, "Session used by different process PID")

    assert res.decision == "DENY"
    assert res.reason_code == "SESSION_PEER_MISMATCH"

def test_ipc_005_replay_attack(setup_ipc):
    """IPC-005: Captured request replay with identical nonce. Expected: DENY on 2nd run"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])

    # First attempt: ALLOW
    res1 = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    assert res1.decision == "ALLOW"

    # Second duplicate attempt: DENY
    res2 = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-005", payload, res2, "Exact request replay")

    assert res2.decision == "DENY"
    assert res2.reason_code == "REPLAY_DETECTED"

def test_ipc_006_nonce_replay_with_mutated_args(setup_ipc):
    """IPC-006: Reused nonce with mutated arguments. Expected: DENY (Sig mismatch or replay)"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])

    # Execute first valid request
    pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)

    # Mutate argument but retain nonce
    payload2 = copy.deepcopy(payload)
    payload2["arguments"] = {"path": "/workspace/malicious.txt"}
    res2 = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload2)
    log_evidence("IPC-006", payload2, res2, "Nonce replay with modified arguments")

    assert res2.decision == "DENY"
    # Fails signature because ArgHash changed without recomputing valid HMAC
    assert res2.reason_code in ["INVALID_SIGNATURE", "REPLAY_DETECTED"]

def test_ipc_007_arghash_argument_mutation(setup_ipc):
    """IPC-007: Arguments modified while keeping original signature. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["arguments"] = {"path": "/workspace/unauthorized_exfil.txt"}

    res = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-007", payload, res, "Argument mutation against signature")

    assert res.decision == "DENY"
    assert res.reason_code == "INVALID_SIGNATURE"

def test_ipc_008_argument_constraint_prefix_violation(setup_ipc):
    """IPC-008: Valid HMAC computed for argument outside path_prefix constraint. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    session = ctx_data["session"]

    args = {"path": "/etc/shadow"}  # Outside /workspace
    arg_hash = compute_canonical_arg_hash(args)
    nonce = "nonce-prefix-viol-01"
    ts = time.time()
    sig = pep.compute_request_signature(session.secret_key, session.session_id, nonce, ts, arg_hash)

    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["arguments"] = args
    payload["nonce"] = nonce
    payload["timestamp"] = ts
    payload["signature"] = sig

    res = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-008", payload, res, "Argument prefix constraint violation")

    assert res.decision == "DENY"
    assert res.reason_code == "ARGUMENT_CONSTRAINT_VIOLATION"

def test_ipc_009_expired_capability(setup_ipc):
    """IPC-009: Capability token whose expires_at is in the past. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    cap_store = ctx_data["capability_store"]
    session = ctx_data["session"]

    # Register expired capability
    cap_expired = CapabilityToken(
        capability_id="cap-expired-01",
        principal="agent-support",
        tool="filesystem.read",
        action="read",
        resource="/workspace/data.txt",
        scope=["workspace"],
        argument_constraints={},
        session_id=session.session_id,
        expires_at=time.time() - 100.0  # Already expired
    )
    cap_store.register_capability(cap_expired)

    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["capability_id"] = "cap-expired-01"
    payload["nonce"] = "nonce-exp-01"
    payload["signature"] = pep.compute_request_signature(
        session.secret_key, session.session_id, payload["nonce"], payload["timestamp"], compute_canonical_arg_hash(payload["arguments"])
    )

    res = pep.evaluate_ipc_request(ctx_data["legit_peer"], payload)
    log_evidence("IPC-009", payload, res, "Expired capability reuse")

    assert res.decision == "DENY"
    assert res.reason_code == "CAPABILITY_EXPIRED"

def test_ipc_010_hot_revocation_on_live_connection(setup_ipc):
    """IPC-010: Session/Capability revoked in real-time over open connection. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    cap_store = ctx_data["capability_store"]

    # Step 1: Valid initial request
    p1 = copy.deepcopy(ctx_data["base_payload"])
    p1["nonce"] = "nonce-before-rev"
    p1["signature"] = pep.compute_request_signature(
        ctx_data["session"].secret_key, ctx_data["session"].session_id, p1["nonce"], p1["timestamp"], compute_canonical_arg_hash(p1["arguments"])
    )
    res1 = pep.evaluate_ipc_request(ctx_data["legit_peer"], p1)
    assert res1.decision == "ALLOW"

    # Step 2: Trigger administrative revocation event
    cap_store.revoke_capability(ctx_data["capability"].capability_id)

    # Step 3: Second request over same connection
    p2 = copy.deepcopy(ctx_data["base_payload"])
    p2["nonce"] = "nonce-after-rev"
    p2["signature"] = pep.compute_request_signature(
        ctx_data["session"].secret_key, ctx_data["session"].session_id, p2["nonce"], p2["timestamp"], compute_canonical_arg_hash(p2["arguments"])
    )
    res2 = pep.evaluate_ipc_request(ctx_data["legit_peer"], p2)
    log_evidence("IPC-010", p2, res2, "Immediate hot revocation over live connection")

    assert res2.decision == "DENY"
    assert res2.reason_code == "CAPABILITY_REVOKED"

def test_ipc_011_rogue_endpoint_substitution(setup_ipc):
    """IPC-011: Attempt connection from invalid or uninitialized transport peer. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])

    unresolved_peer = PeerIdentity(pid=-1, uid=-1, transport="unresolved_rogue")
    res = pep.evaluate_ipc_request(unresolved_peer, payload)
    log_evidence("IPC-011", payload, res, "Rogue endpoint substitution")

    assert res.decision == "DENY"
    assert res.reason_code == "SESSION_PEER_MISMATCH"

def test_ipc_012_same_uid_malicious_process(setup_ipc):
    """IPC-012: Malicious process running under exact same UID attempts execution without key. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    payload = copy.deepcopy(ctx_data["base_payload"])

    # Rogue sibling process (same UID 1000, distinct PID 8888)
    same_uid_peer = PeerIdentity(pid=8888, uid=1000, gid=1000)
    # Rogue attempts to forge HMAC signature using guessed dummy key
    payload["signature"] = "deadbeef" * 8

    res = pep.evaluate_ipc_request(same_uid_peer, payload)
    log_evidence("IPC-012", payload, res, "Same-UID malicious process execution attempt")

    assert res.decision == "DENY"
    # Blocked by PID mismatch first, or invalid signature
    assert res.reason_code in ["SESSION_PEER_MISMATCH", "INVALID_SIGNATURE"]

def test_ipc_013_session_credential_theft_boundary(setup_ipc):
    """
    IPC-013: Critical Boundary Test - Malicious process steals legitimate session secret.
    Evaluates whether credential theft grants execution authority or if PID binding blocks it.
    """
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    session = ctx_data["session"]

    # Attacker process (PID 7777) obtains stolen secret_key
    stolen_key = session.secret_key
    ts = time.time()
    args = {"path": "/workspace/data.txt"}
    arg_hash = compute_canonical_arg_hash(args)
    nonce = "nonce-theft-attempt"
    # Attacker correctly signs payload using stolen secret
    stolen_sig = pep.compute_request_signature(stolen_key, session.session_id, nonce, ts, arg_hash)

    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["nonce"] = nonce
    payload["timestamp"] = ts
    payload["signature"] = stolen_sig

    # Attacker connects from its own process PID 7777
    attacker_peer = PeerIdentity(pid=7777, uid=1000, gid=1000)
    res = pep.evaluate_ipc_request(attacker_peer, payload)
    log_evidence("IPC-013", payload, res, "Session credential theft with distinct caller PID")

    # In Candidate C, PID binding at the OS transport layer successfully blocks this!
    assert res.decision == "DENY"
    assert res.reason_code == "SESSION_PEER_MISMATCH"

def test_ipc_014_forked_child_process_inheritance(setup_ipc):
    """IPC-014: Forked child process (new PID 5555) inherits secret key. Expected: DENY (must negotiate new session)"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    session = ctx_data["session"]

    child_peer = PeerIdentity(pid=5555, uid=1000, gid=1000)
    ts = time.time()
    nonce = "nonce-child-01"
    sig = pep.compute_request_signature(session.secret_key, session.session_id, nonce, ts, compute_canonical_arg_hash(ctx_data["base_payload"]["arguments"]))

    payload = copy.deepcopy(ctx_data["base_payload"])
    payload["nonce"] = nonce
    payload["timestamp"] = ts
    payload["signature"] = sig

    res = pep.evaluate_ipc_request(child_peer, payload)
    log_evidence("IPC-014", payload, res, "Forked child process using parent session key")

    assert res.decision == "DENY"
    assert res.reason_code == "SESSION_PEER_MISMATCH"

def test_ipc_015_confused_deputy_without_delegation(setup_ipc):
    """IPC-015: Agent-Support invokes privileged action via deputy without signed delegation chain. Expected: DENY"""
    ctx_data = setup_ipc
    pep = ctx_data["pep"]
    cap_store = ctx_data["capability_store"]
    session_mgr = ctx_data["session_manager"]

    # Provision Deputy Session (PID 2000)
    deputy_peer = PeerIdentity(pid=2000, uid=1000, gid=1000)
    deputy_session = session_mgr.provision_session(principal="shared-deputy", peer=deputy_peer)

    # Capability belonging to agent-support (not shared-deputy)
    cap = ctx_data["capability"]

    # Deputy calls PEP presenting capability of agent-support without valid delegation chain
    ts = time.time()
    args = {"path": "/workspace/data.txt"}
    arg_hash = compute_canonical_arg_hash(args)
    nonce = "nonce-deputy-ambient"
    sig = pep.compute_request_signature(deputy_session.secret_key, deputy_session.session_id, nonce, ts, arg_hash)

    payload = {
        "principal": "shared-deputy",
        "session_id": deputy_session.session_id,
        "capability_id": cap.capability_id,
        "tool": "filesystem.read",
        "action": "read",
        "resource": "/workspace/data.txt",
        "arguments": args,
        "nonce": nonce,
        "timestamp": ts,
        "signature": sig,
        "delegation_chain": []  # Missing proof of delegation
    }

    res = pep.evaluate_ipc_request(deputy_peer, payload)
    log_evidence("IPC-015", payload, res, "Confused deputy ambient invocation")

    assert res.decision == "DENY"
    assert res.reason_code == "CAPABILITY_PRINCIPAL_MISMATCH"
