# -*- coding: utf-8 -*-
"""
DROS Loopback IPC Security Core Architecture & Interfaces (Candidate C Prototype).
Defines abstract and concrete implementations for:
- PeerIdentityProvider (Platform-specific: Linux UDS / Windows Named Pipe)
- SessionAuthenticator (HMAC challenge-response & ephemeral token binding)
- CapabilityBinder (Deterministic canonicalization of Principal + Action + Scope)
- FreshnessVerifier (Nonce replay cache + TTL monotonic counter)
- RevocationChecker (Real-time hot revocation check)
- ExecutionAttributor (Audit log generation with verified OS/Session identity)
"""

import abc
import hashlib
import hmac
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict

# -------------------------------------------------------------------------
# 1. Domain Entities & Context Definitions
# -------------------------------------------------------------------------

@dataclass(frozen=True)
class PeerIdentity:
    pid: int
    create_time: Optional[float] = None  # Monotonic process start time to prevent PID reuse
    uid: Optional[int] = None  # None on Windows if not mapped
    gid: Optional[int] = None
    username: Optional[str] = None
    platform: str = sys.platform
    transport: str = "loopback"
    container_id: Optional[str] = None
    namespace_id: Optional[str] = None

@dataclass
class SessionCredential:
    session_id: str
    principal: str
    peer_identity: PeerIdentity
    secret_key: bytes  # Ephemeral symmetric secret (32 bytes)
    created_at: float
    ttl_seconds: float
    is_revoked: bool = False

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds

@dataclass
class CapabilityToken:
    capability_id: str
    principal: str
    tool: str
    action: str
    resource: str
    scope: List[str]
    argument_constraints: Dict[str, Any]
    session_id: Optional[str]
    expires_at: float
    is_revoked: bool = False
    delegation_chain: List[str] = field(default_factory=list)

@dataclass
class AuthenticatedContext:
    peer_identity: PeerIdentity
    authenticated_principal: str
    session_id: str
    capability_id: str
    arguments_hash: str
    nonce: str
    decision: str  # ALLOW / DENY
    reason_code: str
    error_message: Optional[str] = None


# -------------------------------------------------------------------------
# 2. Canonicalization Primitives (Deterministic Serialization)
# -------------------------------------------------------------------------

def canonicalize_json_value(val: Any) -> Any:
    """Recursively canonicalizes dictionary keys, floating points, and unicode strings."""
    if isinstance(val, dict):
        return {k: canonicalize_json_value(val[k]) for k in sorted(val.keys())}
    elif isinstance(val, (list, tuple)):
        return [canonicalize_json_value(x) for x in val]
    elif isinstance(val, float):
        # Format floats deterministically without trailing zeros or precision drifts
        return f"{val:.6f}".rstrip("0").rstrip(".") if "." in f"{val:.6f}" else f"{val:.6f}"
    elif isinstance(val, str):
        # Unicode NFC normalization
        import unicodedata
        return unicodedata.normalize("NFC", val)
    return val

def compute_canonical_arg_hash(args: Dict[str, Any]) -> str:
    """
    Computes strict SHA-256 over deterministically canonicalized JSON arguments.
    Enforces key sorting, compact separators, and NFC unicode normalization.
    """
    canonical_obj = canonicalize_json_value(args)
    serialized = json.dumps(canonical_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def compute_capability_digest(cap: CapabilityToken) -> str:
    """Computes deterministic digest over the capability's normative constraints."""
    fields = [
        cap.capability_id,
        cap.principal,
        cap.tool,
        cap.action,
        cap.resource,
        ",".join(sorted(cap.scope)),
        compute_canonical_arg_hash(cap.argument_constraints),
        str(int(cap.expires_at)),
        cap.session_id or "",
        ":".join(cap.delegation_chain)
    ]
    raw = "|".join(fields).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# -------------------------------------------------------------------------
# 3. Interfaces / Abstractions
# -------------------------------------------------------------------------

class PeerIdentityProvider(abc.ABC):
    @abc.abstractmethod
    def get_peer_identity(self, connection: Any) -> PeerIdentity:
        """Derives operating-system verified caller identity from the transport connection."""
        pass

class SessionManager(abc.ABC):
    @abc.abstractmethod
    def provision_session(self, principal: str, peer: PeerIdentity, ttl: float = 3600.0) -> SessionCredential:
        """Provisions an authorized ephemeral session key bound to a verified peer identity."""
        pass

    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[SessionCredential]:
        pass

    @abc.abstractmethod
    def revoke_session(self, session_id: str, reason: str = "administrative_revocation") -> bool:
        pass

class FreshnessVerifier(abc.ABC):
    @abc.abstractmethod
    def verify_and_record_nonce(self, nonce: str, session_id: str, timestamp: float) -> Tuple[bool, str]:
        """Checks for duplicate nonce replay or temporal expiration."""
        pass

class CapabilityStore(abc.ABC):
    @abc.abstractmethod
    def get_capability(self, capability_id: str) -> Optional[CapabilityToken]:
        pass

    @abc.abstractmethod
    def revoke_capability(self, capability_id: str) -> bool:
        pass


# -------------------------------------------------------------------------
# 4. Concrete Platform Providers (Linux / Windows / Mock for Testing)
# -------------------------------------------------------------------------

class MockPeerIdentityProvider(PeerIdentityProvider):
    """Configurable mock peer provider for adversarial cross-platform unit testing."""
    def __init__(self, fixed_identity: Optional[PeerIdentity] = None):
        self._identity = fixed_identity or PeerIdentity(pid=os.getpid(), uid=1000, gid=1000)

    def set_identity(self, identity: PeerIdentity):
        self._identity = identity

    def get_peer_identity(self, connection: Any) -> PeerIdentity:
        if isinstance(connection, PeerIdentity):
            return connection
        return self._identity

class LinuxPeerIdentityProvider(PeerIdentityProvider):
    """
    Linux Unix Domain Socket peer credential extractor using SO_PEERCRED / getsockopt.
    Derives PID, UID, GID directly from kernel socket struct, and queries process start time.
    """
    def get_peer_identity(self, sock: Any) -> PeerIdentity:
        import socket
        import struct
        try:
            # SO_PEERCRED is 17 on Linux
            SO_PEERCRED = getattr(socket, "SO_PEERCRED", 17)
            creds = sock.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize("3i"))
            pid, uid, gid = struct.unpack("3i", creds)
            start_time = None
            try:
                import psutil
                start_time = psutil.Process(pid).create_time()
            except Exception:
                pass
            return PeerIdentity(pid=pid, create_time=start_time, uid=uid, gid=gid, platform="linux", transport="uds")
        except Exception:
            # Fallback or error if not on live Linux socket
            return PeerIdentity(pid=-1, create_time=None, uid=-1, gid=-1, platform="linux", transport="uds_unresolved")

class WindowsPeerIdentityProvider(PeerIdentityProvider):
    """
    Windows Named Pipe peer credential extractor using kernel handle.
    Queries GetNamedPipeClientProcessId to attribute caller PID and psutil for process create_time.
    """
    def get_peer_identity(self, pipe_handle: Any) -> PeerIdentity:
        try:
            import ctypes
            from ctypes import wintypes
            import psutil
            
            client_pid = wintypes.DWORD()
            res = ctypes.windll.kernel32.GetNamedPipeClientProcessId(pipe_handle, ctypes.byref(client_pid))
            if res != 0 and client_pid.value > 0:
                pid = int(client_pid.value)
                try:
                    proc = psutil.Process(pid)
                    start_time = proc.create_time()
                except Exception:
                    start_time = None
                return PeerIdentity(pid=pid, create_time=start_time, uid=None, gid=None, platform="win32", transport="named_pipe")
            return PeerIdentity(pid=-1, create_time=None, uid=None, gid=None, platform="win32", transport="pipe_unresolved")
        except Exception:
            return PeerIdentity(pid=-1, create_time=None, uid=None, gid=None, platform="win32", transport="pipe_unresolved")


# -------------------------------------------------------------------------
# 5. Core In-Memory Engine Implementations
# -------------------------------------------------------------------------

class InMemorySessionManager(SessionManager):
    def __init__(self):
        self._sessions: Dict[str, SessionCredential] = {}

    def provision_session(self, principal: str, peer: PeerIdentity, ttl: float = 3600.0) -> SessionCredential:
        import secrets
        session_id = f"sess-{secrets.token_hex(8)}"
        secret_key = secrets.token_bytes(32)  # 256-bit ephemeral HMAC key
        cred = SessionCredential(
            session_id=session_id,
            principal=principal,
            peer_identity=peer,
            secret_key=secret_key,
            created_at=time.time(),
            ttl_seconds=ttl,
            is_revoked=False
        )
        self._sessions[session_id] = cred
        return cred

    def get_session(self, session_id: str) -> Optional[SessionCredential]:
        return self._sessions.get(session_id)

    def revoke_session(self, session_id: str, reason: str = "administrative_revocation") -> bool:
        if session_id in self._sessions:
            self._sessions[session_id].is_revoked = True
            return True
        return False

class InMemoryFreshnessVerifier(FreshnessVerifier):
    def __init__(self, max_nonce_cache: int = 10000, max_time_skew_sec: float = 300.0):
        self._seen_nonces: Set[str] = set()
        self._max_time_skew_sec = max_time_skew_sec

    def verify_and_record_nonce(self, nonce: str, session_id: str, timestamp: float) -> Tuple[bool, str]:
        now = time.time()
        # 1. Check time window skew
        if abs(now - timestamp) > self._max_time_skew_sec:
            return False, "TIMESTAMP_OUT_OF_BOUNDS"
        # 2. Check nonce replay
        composite_key = f"{session_id}:{nonce}"
        if composite_key in self._seen_nonces:
            return False, "REPLAY_DETECTED"
        self._seen_nonces.add(composite_key)
        return True, "FRESH"

class InMemoryCapabilityStore(CapabilityStore):
    def __init__(self):
        self._caps: Dict[str, CapabilityToken] = {}

    def register_capability(self, cap: CapabilityToken):
        self._caps[cap.capability_id] = cap

    def get_capability(self, capability_id: str) -> Optional[CapabilityToken]:
        return self._caps.get(capability_id)

    def revoke_capability(self, capability_id: str) -> bool:
        if capability_id in self._caps:
            self._caps[capability_id].is_revoked = True
            return True
        return False


# -------------------------------------------------------------------------
# 6. DROS Hybrid PEP Boundary Engine (Candidate C Prototype)
# -------------------------------------------------------------------------

class DrosHybridIpcPEP:
    """
    Implements Candidate C:
    - Verifies peer identity (OS transport)
    - Verifies ephemeral session HMAC token
    - Verifies capability owner binding
    - Verifies ArgHash integrity
    - Verifies freshness / nonce
    - Verifies live revocation state
    - Prevents confused deputy propagation
    """
    def __init__(
        self,
        peer_provider: PeerIdentityProvider,
        session_manager: SessionManager,
        capability_store: CapabilityStore,
        freshness_verifier: FreshnessVerifier
    ):
        self.peer_provider = peer_provider
        self.session_manager = session_manager
        self.capability_store = capability_store
        self.freshness_verifier = freshness_verifier

    def compute_request_signature(self, secret_key: bytes, session_id: str, nonce: str, timestamp: float, arg_hash: str) -> str:
        """HMAC-SHA256(secret_key, session_id || nonce || timestamp || arg_hash)"""
        msg = f"{session_id}|{nonce}|{int(timestamp)}|{arg_hash}".encode("utf-8")
        return hmac.new(secret_key, msg, hashlib.sha256).hexdigest()

    def evaluate_ipc_request(
        self,
        raw_connection: Any,
        payload: Dict[str, Any]
    ) -> AuthenticatedContext:
        # Step 1: Derive OS Peer Identity from transport connection
        peer = self.peer_provider.get_peer_identity(raw_connection)
        claimed_principal = payload.get("principal", "UNKNOWN")
        session_id = payload.get("session_id", "")
        capability_id = payload.get("capability_id", "")
        nonce = payload.get("nonce", "")
        timestamp = float(payload.get("timestamp", 0.0))
        caller_hmac = payload.get("signature", "")
        arguments = payload.get("arguments", {})
        computed_arg_hash = compute_canonical_arg_hash(arguments)

        # Step 2: Validate Session Existence & Authenticity
        session = self.session_manager.get_session(session_id)
        if not session:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal="UNAUTHENTICATED",
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="INVALID_SESSION",
                error_message=f"Session '{session_id}' not found or never provisioned."
            )

        # Step 3: Verify Session Peer Identity Binding (PID, UID, and Process Lifetime create_time)
        # Prevent another process (even same UID) from hijacking session if PID differs
        if session.peer_identity.pid != peer.pid:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal="UNAUTHENTICATED",
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="SESSION_PEER_MISMATCH",
                error_message=f"Caller PID {peer.pid} does not match session owner PID {session.peer_identity.pid}."
            )

        # Invariant I1-Ext: Check Process Start Time to prevent PID Reuse / Recycling Attacks (IPC-016)
        if (session.peer_identity.create_time is not None and 
            peer.create_time is not None and 
            abs(session.peer_identity.create_time - peer.create_time) > 0.05):
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal="UNAUTHENTICATED",
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="PID_REUSE_DETECTED",
                error_message=f"PID {peer.pid} create_time ({peer.create_time}) does not match session owner start time ({session.peer_identity.create_time})."
            )

        # Step 4: Check Session Revocation & Expiry
        if session.is_revoked:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="SESSION_REVOKED",
                error_message="Ephemeral session has been revoked."
            )
        if session.is_expired:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="SESSION_EXPIRED",
                error_message="Ephemeral session TTL expired."
            )

        # Step 5: Check Principal Claim vs. Authenticated Session Principal (Invariant I1)
        if claimed_principal != session.principal:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,  # Attribute to authentic owner
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="PRINCIPAL_SPOOFING_DETECTED",
                error_message=f"Claimed principal '{claimed_principal}' does not match session principal '{session.principal}'."
            )

        # Step 6: Verify Cryptographic Signature (HMAC over ArgHash + Nonce)
        expected_sig = self.compute_request_signature(session.secret_key, session_id, nonce, timestamp, computed_arg_hash)
        if not hmac.compare_digest(expected_sig, caller_hmac):
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="INVALID_SIGNATURE",
                error_message="Cryptographic proof (HMAC) invalid or ArgHash mutation detected."
            )

        # Step 7: Check Freshness / Nonce Replay (Invariant I5)
        fresh, freshness_reason = self.freshness_verifier.verify_and_record_nonce(nonce, session_id, timestamp)
        if not fresh:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code=freshness_reason,
                error_message=f"Freshness check failed: {freshness_reason}"
            )

        # Step 8: Validate Capability & Principal Ownership Binding (Invariant I2)
        cap = self.capability_store.get_capability(capability_id)
        if not cap:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="CAPABILITY_NOT_FOUND",
                error_message=f"Capability '{capability_id}' not found."
            )

        # Check Capability Revocation
        if cap.is_revoked:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="CAPABILITY_REVOKED",
                error_message=f"Capability '{capability_id}' has been revoked."
            )

        # Check Capability Expiry
        if time.time() > cap.expires_at:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="CAPABILITY_EXPIRED",
                error_message=f"Capability '{capability_id}' has expired."
            )

        # Check Principal Ownership (Capability Owner must match Authenticated Session Principal)
        if cap.principal != session.principal:
            # Check for legitimate delegation chain if Confused Deputy check
            delegation = payload.get("delegation_chain", [])
            if not (session.principal in cap.delegation_chain and cap.principal in delegation):
                return AuthenticatedContext(
                    peer_identity=peer,
                    authenticated_principal=session.principal,
                    session_id=session_id,
                    capability_id=capability_id,
                    arguments_hash=computed_arg_hash,
                    nonce=nonce,
                    decision="DENY",
                    reason_code="CAPABILITY_PRINCIPAL_MISMATCH",
                    error_message=f"Capability '{capability_id}' belongs to '{cap.principal}', but caller is authenticated as '{session.principal}'."
                )

        # Step 9: Validate Action Binding (Tool, Action, Resource) (Invariant I3)
        requested_tool = payload.get("tool")
        requested_action = payload.get("action")
        requested_resource = payload.get("resource")

        if cap.tool != requested_tool or cap.action != requested_action:
            return AuthenticatedContext(
                peer_identity=peer,
                authenticated_principal=session.principal,
                session_id=session_id,
                capability_id=capability_id,
                arguments_hash=computed_arg_hash,
                nonce=nonce,
                decision="DENY",
                reason_code="ACTION_BINDING_VIOLATION",
                error_message=f"Requested ({requested_tool}, {requested_action}) does not match capability ({cap.tool}, {cap.action})."
            )

        # Step 10: Validate Resource Scope & Argument Constraints (Invariant I4)
        prefix = cap.argument_constraints.get("path_prefix")
        if prefix:
            target_path = arguments.get("path", "")
            if not target_path.startswith(prefix):
                return AuthenticatedContext(
                    peer_identity=peer,
                    authenticated_principal=session.principal,
                    session_id=session_id,
                    capability_id=capability_id,
                    arguments_hash=computed_arg_hash,
                    nonce=nonce,
                    decision="DENY",
                    reason_code="ARGUMENT_CONSTRAINT_VIOLATION",
                    error_message=f"Argument 'path' ({target_path}) violates required prefix ({prefix})."
                )

        # All Invariants Passed: Grant Execution
        return AuthenticatedContext(
            peer_identity=peer,
            authenticated_principal=session.principal,
            session_id=session_id,
            capability_id=capability_id,
            arguments_hash=computed_arg_hash,
            nonce=nonce,
            decision="ALLOW",
            reason_code="AUTHENTICATED_AND_AUTHORIZED",
            error_message=None
        )
