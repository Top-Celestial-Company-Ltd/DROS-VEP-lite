# DROS Loopback IPC Authentication Normative Requirements (IPC_AUTHENTICATION_REQUIREMENTS.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE SPECIFICATION FOR P2 PROTOTYPE
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1`, `IPC_CURRENT_ARCHITECTURE.md`, and `LOOPBACK_IPC_THREAT_MODEL.md`

---

## 1. Normative Requirement Table

The following testable requirements constitute the definitive acceptance gate for the Phase P2 IPC Authentication Prototype and the Phase P3 Attack Corpus:

| Requirement ID | Requirement Description | Testable? | Target Threat Level | Bound Invariant | Expected Outcome | Verification Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **IPC-AUTH-001** | **Caller Identity Cannot Be Caller-Supplied**<br>The PEP must derive caller identity from kernel peer credentials or active session binding; any payload-asserted `principal` that disagrees with the transport-authenticated identity must be rejected. | **YES** | A0 / A1 | I1 | **DENY** | Transmit payload asserting `principal="admin"` from unauthenticated client process; assert rejection. |
| **IPC-AUTH-002** | **Principal / Capability Mismatch Rejection**<br>A capability token issued to Principal $P_A$ presented by caller Principal $P_B$ must be unconditionally rejected. | **YES** | A0 / A2 | I2 | **DENY** | Steal valid token for Agent-B and submit from Agent-A socket connection; assert rejection. |
| **IPC-AUTH-003** | **Replay Protection via Freshness Nonce**<br>Any request presenting a previously executed nonce or sequence ID must be detected and rejected. | **YES** | A0 / A2 | I5 | **DENY** | Capture and immediately replay an identical valid execution payload over IPC; assert second execution rejected. |
| **IPC-AUTH-004** | **ArgHash Mutation Rejection**<br>Any alteration of request arguments that produces an `arguments_hash` differing from the authorized token must cause execution failure. | **YES** | A0 | I4 | **DENY** | Alter `path` or parameters while keeping the capability token intact; assert hash check fails. |
| **IPC-AUTH-005** | **Immediate Hot Revocation Enforcement**<br>A revoked capability or session must be rejected immediately, even if the loopback connection/socket remains established. | **YES** | A0 | I6 | **DENY** | Issue revocation signal to PDP while socket is open, then attempt tool execution; assert immediate DENY. |
| **IPC-AUTH-006** | **Expired Capability / TTL Rejection**<br>A capability whose wall-clock TTL has elapsed or whose monotonic counter has expired must be rejected at the PEP gate. | **YES** | A0 | I5 | **DENY** | Fast-forward clock or submit token after expiry timestamp; assert expiry DENY. |
| **IPC-AUTH-007** | **Endpoint Substitution Rejection**<br>Clients must reject rogue sockets (e.g. symlink hijack, rogue server); PEP must verify socket filesystem permissions (e.g. `0600`). | **YES** | A1 | I7 | **DENY** | Point client to unauthorized mock socket or simulate hijacked socket permissions; assert handshake fails. |
| **IPC-AUTH-008** | **Confused Deputy Delegation Prevention**<br>Intermediary deputy services must pass a verifiable delegation chain; ambient deputy authority cannot be substituted for client capability. | **YES** | A0 | I2 / I3 | **DENY** | Submit request via local proxy without signed delegation chain; assert ambient escalation fails. |
| **IPC-AUTH-009** | **Attribution Integrity in Audit Log**<br>The generated audit record must record the *authenticated* transport principal, not the caller's asserted self-claim. | **YES** | A0 / A1 | I8 | **PASS** | Submit request with mismatched claim; verify audit log writes verified kernel/session identity. |
| **IPC-AUTH-010** | **Same-UID Session Isolation**<br>A separate process running under the same UID cannot invoke another process's session without possession of the ephemeral session secret. | **YES** | A2 | I1 / I2 | **DENY** | Spawn second process under same UID; attempt IPC request using victim's session ID without HMAC key. |

---

## 2. Test Verification Matrix for P2 / P3

| Requirement ID | Unit / Integration Test Case Name | Target Harness |
| :--- | :--- | :--- |
| `IPC-AUTH-001` | `test_ipc_rejects_forged_principal_payload` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-002` | `test_ipc_rejects_stolen_cross_principal_token` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-003` | `test_ipc_rejects_duplicate_nonce_replay` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-004` | `test_ipc_rejects_mutated_arghash` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-005` | `test_ipc_enforces_immediate_hot_revocation` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-006` | `test_ipc_rejects_expired_ttl_capability` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-007` | `test_ipc_rejects_insecure_endpoint_permissions` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-008` | `test_ipc_rejects_confused_deputy_ambient_call` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-009` | `test_ipc_audit_records_authenticated_principal` | `tests/security/test_ipc_auth.py` |
| `IPC-AUTH-010` | `test_ipc_rejects_same_uid_unauthenticated_process`| `tests/security/test_ipc_auth.py` |

---

## 3. Exit Criteria for P2 Implementation

The Phase P2 implementation must implement:
1. An IPC server/client transport demonstrating Candidate C (OS Peer verification where available + per-process ephemeral session token/HMAC).
2. A deterministic mock harness allowing automated test execution across Windows/Linux without requiring root privileges.
3. 100% green test execution for all 10 requirements in the table above.
