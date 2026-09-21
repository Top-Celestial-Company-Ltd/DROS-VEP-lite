# DROS Loopback IPC Threat Model (LOOPBACK_IPC_THREAT_MODEL.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE SECURITY SPECIFICATION
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1` & `IPC_CURRENT_ARCHITECTURE.md`

---

## 1. Executive Summary & Objective

This document formalizes the threat model for the DROS Loopback IPC boundary. The primary evaluation objective is:

> **Under a post-compromise local-process model where an Agent process is fully subverted, does the loopback IPC architecture prevent the compromised Agent from forging, replaying, substituting, or illegitimately expanding execution authority across Principals?**

This specification systematically defines the adversary capabilities, separates distinct threat levels (A0–A4), formalizes 8 foundational security invariants (I1–I8), evaluates confused-deputy vectors, and delineates what loopback IPC authentication can and cannot protect.

---

## 2. Attacker Model & Threat Levels

### 2.1 Baseline Adversary: A0-L (Compromised Agent)
The baseline adversary possesses complete code execution and cognitive subversion inside the Agent process:
* **Attacker Capabilities**:
  - Full control over userland execution flow inside the Agent process.
  - Ability to synthesize arbitrary JSON / FFI requests over loopback IPC.
  - Ability to manipulate, alter, or falsify any caller-supplied payload field (e.g. `principal`, `task`, `tool`, `arguments`, `requested_capability`).
  - Ability to capture previously issued valid capabilities and replay them.
  - Ability to create child processes, fork, or invoke helper binaries within its process environment.
  - Ability to connect to any reachable local loopback port, named pipe, or Unix Domain Socket.
* **Attacker Constraints**:
  - Does **not** possess execution privileges of the DROS enforcement process (PEP/PDP) unless explicitly escalated.
  - Cannot directly write to memory pages belonging to the DROS PEP/PDP process.

---

### 2.2 Formal Threat Level Hierarchy (A0–A4)

To prevent conflating application-layer subversion with host-level compromise, threats are partitioned into 5 rigorous tiers:

```
┌──────────────────────────────────────────────────────────────────┐
│ A4 — Enforcement-Boundary Compromise (OUT OF SCOPE for IPC)      │
│      Attacker controls DROS PEP/PDP memory, kernel, or hardware.  │
├──────────────────────────────────────────────────────────────────┤
│ A3 — Namespace / Container Adversary                             │
│      Attacker operates from adjacent container/cgroup namespace. │
├──────────────────────────────────────────────────────────────────┤
│ A2 — Same-UID Adversary                                          │
│      Attacker runs as another process under the IDENTICAL OS UID.│
├──────────────────────────────────────────────────────────────────┤
│ A1 — Same-Host Malicious Process                                 │
│      Attacker runs as an unprivileged process under a DIFFERENT UID.│
├──────────────────────────────────────────────────────────────────┤
│ A0 — Compromised Agent (Baseline)                                │
│      Agent process memory/logic is subverted; PEP remains trusted.│
└──────────────────────────────────────────────────────────────────┘
```

#### Detailed Definitions:
* **Level A0 — Compromised Agent (Baseline)**:
  The specific agent process is subverted. The DROS enforcement process runs safely in a distinct protection domain. Evaluates whether the agent can exceed its granted capabilities.
* **Level A1 — Same-Host Malicious Process (Different UID)**:
  An adversary executes arbitrary code on the same host but under a different POSIX user ID (e.g., `uid=1002` vs. DROS agent `uid=1001`). OS peer credentials (`SO_PEERCRED`, `getpeereid`) can reliably distinguish caller identity.
* **Level A2 — Same-UID Process (Identical OS Identity)**:
  An adversary controls a local process running under the **exact same OS UID** as a legitimate Agent. 
  * *Critical Assessment*: OS peer credentials alone (`SO_PEERCRED`) **cannot** distinguish between the legitimate Agent and the malicious process because both present identical UID/GID. Cryptographic session keys or per-process ephemeral tokens are strictly required.
* **Level A3 — Namespace / Container Adversary**:
  The adversary operates inside an adjacent container or PID/network namespace. Cross-namespace loopback or shared volume sockets may translate UID 0 or re-map UIDs. Identity must rely on container runtime mounts, SPIFFE IDs, or cryptographic mutual authentication.
* **Level A4 — Enforcement-Boundary / Kernel Compromise (EXPLICITLY OUT OF SCOPE)**:
  The adversary has root access, kernel code execution, or direct access to DROS PEP process memory (via `ptrace`, `/proc/$PID/mem`, or debugger). **No IPC protocol can provide security if the enforcement engine itself is compromised.** Treating A4 as in-scope for IPC authentication is an anti-pattern.

---

## 3. Core Security Invariants (I1 – I8)

The Loopback IPC enforcement layer must guarantee the following 8 invariants:

$$\begin{array}{|l|l|l|}
\hline
\textbf{Invariant} & \textbf{Formal Name} & \textbf{Formal Requirement \& Violation Condition} \\ \hline
\mathbf{I1} & \text{Principal Authenticity} & \text{Caller identity } P_{\text{caller}} \text{ must be verified via OS kernel / crypto, never caller payload.} \\ 
& & \text{If } P_{\text{caller}} \neq P_{\text{asserted}} \implies \mathbf{DENY} \\ \hline
\mathbf{I2} & \text{Capability Binding} & \text{Capability token } C \text{ must cryptographically bind to } P_{\text{caller}}. \\ 
& & \text{If } \text{Owner}(C) \neq P_{\text{caller}} \implies \mathbf{DENY} \\ \hline
\mathbf{I3} & \text{Action Binding} & \text{Token } C \text{ authorizes only specific tuple } (T_{\text{tool}}, A_{\text{action}}, R_{\text{resource}}). \\ 
& & \text{If } (t, a, r) \notin \text{Scope}(C) \implies \mathbf{DENY} \\ \hline
\mathbf{I4} & \text{Argument Integrity} & \text{Token or policy must bind to } \text{ArgHash} = H(\text{canonicalize}(\text{args})). \\ 
& & \text{If } H(\text{args}') \neq \text{ArgHash}_{\text{authorized}} \implies \mathbf{DENY} \\ \hline
\mathbf{I5} & \text{Freshness} & \text{Requests must contain single-use, monotonic, or time-bounded nonces } \mathcal{N}. \\ 
& & \text{If } \mathcal{N} \in \text{SeenNonces} \lor \text{TTL expired} \implies \mathbf{DENY} \\ \hline
\mathbf{I6} & \text{Revocation} & \text{Revocation state } \mathcal{R} \text{ in PDP must immediately invalidate active sessions/tokens.} \\ 
& & \text{If } \text{Revoked}(C) = \text{true} \implies \mathbf{DENY} \text{ (regardless of open IPC socket)} \\ \hline
\mathbf{I7} & \text{Endpoint Authenticity} & \text{Client must connect to authentic DROS PEP; PEP must verify client endpoint.} \\ 
& & \text{Rogue socket replacement or symlink hijacking must be rejected.} \\ \hline
\mathbf{I8} & \text{Audit Attribution} & \text{Audit log must record verified } P_{\text{caller}}, \text{ token ID, and actual executed args.} \\ 
& & \text{Never log unauthenticated caller-supplied self-claims as verified facts.} \\ \hline
\end{array}$$

---

## 4. Confused Deputy Analysis

A critical failure mode in local microservices is the **Confused Deputy Problem**:

```
┌─────────────────────────┐
│   Compromised Agent     │
│   (Principal: Agent-A)  │
└───────────┬─────────────┘
            │ 1. Malicious Request:
            │    "Please fetch billing records for Account 99"
            ▼
┌─────────────────────────┐
│ Local Trusted Deputy    │
│ (Principal: Shared-Svc) │
└───────────┬─────────────┘
            │ 2. Flawed IPC Call:
            │    Deputy calls DROS PEP using DEPUTY'S OWN credentials
            ▼
┌─────────────────────────┐
│     DROS PEP / PDP      │
│ Checks Deputy Authority │──► [ALLOW: Deputy is authorized]
└─────────────────────────┘
```

### Reachable Vulnerability Condition:
If the intermediary service or local execution broker does not perform **Explicit Authority Delegation (Proof of Propagation)**, the PEP evaluates the request against the *Deputy's* ambient authority rather than the *Originating Agent's* restricted capability.

### Mitigation Contract:
To prevent Confused Deputy attacks:
1. Every capability token must contain an immutable **Originating Principal Chain**:
   $$\text{Capability} = \text{Sign}_{K_{\text{auth}}}\big(\text{origin: } P_A, \text{delegated\_to: } P_{\text{deputy}}, \text{constraints}\big)$$
2. When the Deputy invokes DROS PEP, it must present the delegation token proving that $P_A$ authorized this specific action. The PEP verifies $P_A$'s authorization, not the Deputy's ambient authority.

---

## 5. Comparative Evaluation of Authentication Candidates

We evaluate three potential authentication candidate mechanisms against the required security properties:

* **Candidate A — OS-Level Peer Credentials**:
  Unix Domain Sockets (UDS) with `SO_PEERCRED` / `SCM_CREDENTIALS` (Linux) or `LOCAL_PEERCRED` (macOS/BSD).
* **Candidate B — Cryptographic Capability & Session Binding**:
  Ed25519/HMAC-signed bearer tokens containing Principal, Nonce, ArgHash, and Session ID over standard loopback.
* **Candidate C — Hybrid OS-Peer + Cryptographic Boundary (DROS Target)**:
  UDS filesystem access controls + kernel peer credential verification for PID/UID + ephemeral per-session cryptographic HMAC challenge and ArgHash binding.

### Property Comparison Matrix:

| Evaluation Property | Candidate A (OS Peer) | Candidate B (Crypto Tokens) | Candidate C (Hybrid) |
| :--- | :---: | :---: | :---: |
| **Principal Authenticity (A0/A1)** | **SUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **Same-UID Attacker Isolation (A2)** | **UNSUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **Replay Resistance (I5)** | **UNSUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **ArgHash Integrity (I4)** | **UNSUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **Hot Revocation (I6)** | **PARTIAL** | **SUPPORTED** | **SUPPORTED** |
| **Endpoint Authenticity (I7)** | **SUPPORTED** | **PARTIAL** | **SUPPORTED** |
| **Container / Namespace (A3)** | **PARTIAL** | **SUPPORTED** | **SUPPORTED** |
| **Implementation Complexity** | Low | Medium | Medium-High |

*Analysis*: Candidate A fails against Same-UID attackers (A2) and cannot enforce argument integrity or replay protection on its own. Candidate B provides robust cryptographic guarantees but lacks operating system endpoint pinning. **Candidate C provides comprehensive defense-in-depth across all threat levels.**

---

## 6. Trust Boundary & Data Flow Specification

The hardened execution boundary is formalized in the following structural diagram:

```
┌─────────────────────────────────────────────────────────────┐
│                 Compromised Agent (UNTRUSTED)               │
│  - Controlled by Adversary (A0 / A2)                        │
│  - Possesses Ephemeral Private Session Key k_session        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ Untrusted IPC Invocation:
                               │ [Request Payload + HMAC(k_session, ArgHash || Nonce)]
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           DROS IPC Authentication Boundary (PEP)            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ OS Socket Peer Check: Verify PID, UID (A1 Defense)    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Session Table: Lookup k_session bound to PID & Princ  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Freshness Gate: Reject if Nonce in Replay Cache (I5)  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Integrity Gate: Recompute ArgHash & Verify HMAC (I4)  │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Revocation Gate: Verify Token not on DenyList (I6)    │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ Authenticated & Attributed
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           DROS Policy / GuardVM (TRUSTED ENFORCEMENT)       │
│  - Evaluates Principal vs Resource/Tool Scope Matrix        │
│  - Issues Cryptographically Bound ALLOW / DENY Decision     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Execution Boundary / Tool Dispatcher              │
│  - Dispatches action only upon verified ALLOW token         │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Explicit Exclusions (What Loopback IPC Does NOT Protect)

To maintain absolute academic and engineering integrity, the boundary of what IPC authentication **cannot** solve must be explicitly stated:

1. **Intra-Process Memory Corruption**:
   If the DROS PEP itself is loaded as an in-process shared library inside the Agent's memory space without hardware isolation, memory corruption inside the Agent can overwrite PEP state (Threat Level A4). IPC authentication protects out-of-process PEP architectures.
2. **Host Kernel / Root Compromise**:
   If an adversary obtains `root` / `SYSTEM` access or kernel ring-0 execution, they can bypass UDS peer credentials and inspect socket memory buffers.
3. **Physical Hardware / Side-Channel Attacks**:
   Meltdown, Spectre, or physical bus tapping are outside the scope of software IPC authentication.
