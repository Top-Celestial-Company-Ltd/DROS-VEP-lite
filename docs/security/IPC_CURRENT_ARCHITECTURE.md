# DROS Current Loopback IPC Architecture & Data-Flow Analysis (IPC_CURRENT_ARCHITECTURE.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE AUDIT BASELINE
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1` (`EXP-1789532251-38a4fd`)
* **Evaluation Target**: `dros-vep-lite` Reference Substrate & DROS Runtime PEP

---

## 1. System Context & Component Boundaries

In the current reference benchmark substrate (`substrates/dros/adapter.py`) and standard DROS deployment profiles, execution governance is evaluated across five primary logical components:

1. **Agent Process (Caller)**:
   The execution client generating action intents. In threat modeling, this process is modeled as post-compromise (under adversarial cognitive or execution control).
2. **Loopback Transport Layer**:
   The communication channel connecting the Agent process to the DROS Policy Enforcement Point (PEP). Deployed as in-band Python call boundary (in VEP benchmarks), Unix Domain Sockets (UDS), or local loopback TCP (in microkernel and enterprise sidecar profiles).
3. **Policy Enforcement Point (PEP)**:
   The interception gate that intercepts execution requests before they reach the OS or target tool runtime.
4. **Policy Decision Point (PDP / GuardVM)**:
   The evaluation engine that computes deterministic access decisions (`ALLOW` / `DENY`) against active security policies, scope constraints, and capability tokens.
5. **Target Execution Boundary**:
   The physical OS syscall boundary, external API client, or microkernel C-ABI that performs the underlying action.

---

## 2. End-to-End Data Flow

The flow of an execution request from a compromised Agent process to the execution boundary proceeds as follows:

```
┌─────────────────────────────────────────────────────────────┐
│                       Agent Process                         │
│             (Compromised Context: Adversary A0)              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ 1. CanonicalExecutionRequest
                               │    (JSON Payload / FFI Struct)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Loopback Transport (UDS / Memory)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Policy Enforcement Point (DROS PEP)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 2. Request Parsing & Deserialization                  │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 3. Principal Attribution Check                        │  │
│  │    Compare request.principal vs. authorized_principal │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 4. Temporal & Revocation Check                        │  │
│  │    Check TTL expiry & hot revocation flag             │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 5. Freshness & Replay Verification                    │  │
│  │    Check nonce against seen_nonces cache              │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 6. Tool, Scope & Argument Integrity (ArgHash)        │  │
│  │    Verify tool whitelist, scope bounds & prefix      │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
                        [ Decision Gate ]
                         /            \
                   ALLOW /              \ DENY
                        /                \
                       ▼                  ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  Target Execution Boundary   │  │    Rejection / Audit Log     │
│  (Subprocess / API / Syscall)│  │ (Structured Evidence Record) │
└──────────────────────────────┘  └──────────────────────────────┘
```

---

## 3. Detailed Request Field Trust & Provenance Classification

The table below audits every field in `CanonicalExecutionRequest` under the current architecture, classifying its provenance, authentication status, and trustworthiness:

| Field Name | Transport Representation | Field Provenance | Authentication Status | Trust Classification | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `request_id` | String (UUID / custom) | Caller-supplied | Unauthenticated | **UNTRUSTED** | Can be forged or randomized by caller. |
| `principal` | String (e.g. `agent-support`) | Caller-supplied | Unauthenticated | **UNTRUSTED** | **VULNERABILITY GAP**: A compromised Agent can self-declare any principal identity unless verified via OS peer credentials or cryptographic signature. |
| `task` | String (e.g. `task-ticket-482`) | Caller-supplied | Unauthenticated | **UNTRUSTED** | Used for tracing, not authenticated. |
| `tool` | String (e.g. `filesystem.write`) | Caller-supplied | Authenticated against Capability Whitelist | **DERIVED / CONDITIONAL** | Must match `authorized_tools` in capability token. |
| `action` | String (e.g. `write`) | Caller-supplied | Authenticated against Capability Whitelist | **DERIVED / CONDITIONAL** | Verified against capability scope. |
| `resource` | String (URI / path) | Caller-supplied | Authenticated against Scope & Prefix | **DERIVED / CONDITIONAL** | Verified against prefix constraints. |
| `arguments` | Dict / JSON object | Caller-supplied | Subject to canonical hashing | **UNTRUSTED (Raw) / DERIVED (Hash)** | Mutated arguments must invalidate authorization if bound to hash. |
| `arguments_hash` | String (`sha256:...`) | Derived (Engine post-init) | Computed by PEP / Ingestion | **TRUSTED (within PEP boundary)** | Automatically computed from `arguments` upon ingestion. |
| `requested_capability` | String (e.g. `fs.write`) | Caller-supplied | Matched against token | **UNTRUSTED** | Target capability identifier. |
| `authorization_context.authorized_principal` | String (e.g. `billing-service`) | Capability Token payload | Unsigned in reference model | **UNTRUSTED (unless Cryptographically Bound)** | In reference benchmark, token is passed by caller as structured JSON. If unsigned, attacker can forge both `principal` and `authorized_principal`. |
| `authorization_context.scope` | List[String] | Capability Token payload | Unsigned in reference model | **UNTRUSTED (unless Signed)** | Determines resource sandbox boundaries. |
| `authorization_context.ttl` / `is_expired` | Integer / Boolean | Capability Token payload | Wall-clock / PEP verified | **DERIVED** | Checked by PEP against clock/flag. |
| `authorization_context.is_revoked` | Boolean | Capability Token / PDP state | PDP/PEP state | **TRUSTED (when held by PDP)** | Hot revocation list maintained by PDP. |
| `authorization_context.nonce` | String | Caller-supplied / Token | Cached in PEP `seen_nonces` | **AUTHENTICATED (Freshness)** | Prevents duplicate replay if nonces are unforgeable and tracked. |

---

## 4. Current Architectural Gaps Identified

1. **In-Band Caller Self-Declaration**:
   In the reference Python adapter (`DrosAdapter`), the request payload contains both `request.principal` and `auth["authorized_principal"]`. While the check `auth_principal != request.principal` succeeds in catching mismatched declarations, an attacker in control of the caller process who constructs the payload can supply matching forged strings (`principal: "admin"`, `authorized_principal: "admin"`) unless the capability token is signed by an external authority or the caller identity is verified via OS-level socket credentials (`SO_PEERCRED`).
2. **Transport Channel Agnosticism**:
   The current reference PEP does not bind the incoming connection to the caller's physical OS PID/UID. Any process that can write to the loopback transport is evaluated solely on the contents of its payload.
3. **Session State vs. Stateless Invocation**:
   Replay protection relies on an in-memory `seen_nonces` set. If the PEP process restarts or multiple PEP instances run without a shared replay ledger, replay attacks become feasible across process restarts.

---

## 5. Architectural Verdict
The current DROS logic implements rigorous **policy decision rules** (attributions, boundaries, argument prefix checking, hot revocation, nonce checking). However, the **attribution boundary** at the physical loopback transport level requires hardening: caller identity must not be caller-supplied, but must be anchored to OS peer credentials, kernel cgroups, or cryptographic signatures.
