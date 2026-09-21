# DROS Loopback IPC Authentication Architecture & Implementation (IPC_AUTHENTICATION_IMPLEMENTATION.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE IMPLEMENTATION SPECIFICATION
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1`, `LOOPBACK_IPC_THREAT_MODEL.md`

---

## 1. Candidate C Reference Implementation Summary

The prototype implementation is housed at `src/vep/security/ipc_auth.py` and provides the execution governance boundary across four modular layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: OS Peer Provider                │
│  - Linux: LinuxPeerIdentityProvider (SO_PEERCRED)           │
│  - Windows: WindowsPeerIdentityProvider (Named Pipe PID)    │
│  - Test Harness: MockPeerIdentityProvider                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Layer 2: Ephemeral Session Mgr              │
│  - Generates 256-bit CSPRNG session secrets                 │
│  - Strictly binds session_id to caller PID and Principal    │
│  - Manages session TTL and immediate revocation state       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Layer 3: Freshness & ArgHash Engine           │
│  - Canonicalize JSON recursively (NFC, float normalization) │
│  - Nonce replay cache with time-skew window validation      │
│  - HMAC-SHA256 signature verification over (Nonce||ArgHash) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Layer 4: Policy & Capability Store            │
│  - Validates capability ownership vs authenticated Principal│
│  - Validates action tuple (Tool, Action, Resource)          │
│  - Validates argument constraints (Path prefix)             │
│  - Prevents Confused Deputy delegation escalation           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Invariant Enforcement Mapping

| Security Invariant | Implementing Method / Check | Tested Attack ID |
| :--- | :--- | :---: |
| **I1 Principal Authenticity** | `session.principal != claimed_principal` check | IPC-001 |
| **I2 Capability Binding** | `cap.principal != session.principal` check | IPC-003 |
| **I3 Action Binding** | `cap.tool != tool or cap.action != action` check | IPC-002 |
| **I4 Argument Integrity** | `compute_canonical_arg_hash` & prefix constraint check | IPC-007, IPC-008 |
| **I5 Freshness & Replay** | `freshness_verifier.verify_and_record_nonce` | IPC-005, IPC-006 |
| **I6 Hot Revocation** | `cap.is_revoked` & `session.is_revoked` real-time gate | IPC-010 |
| **I7 Endpoint Authenticity** | `peer.transport == "unresolved_rogue"` peer check | IPC-011 |
| **I8 Audit Attribution** | `ctx.authenticated_principal` populated from session | IPC-001, IPC-009 |
