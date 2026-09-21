# DROS Loopback IPC Key Provisioning & Credential Lifecycle (IPC_KEY_PROVISIONING.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE SECURITY DESIGN SPECIFICATION
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1`, `LOOPBACK_IPC_THREAT_MODEL.md`, and Candidate C Architecture

---

## 1. The Fundamental Question: Where Does the Secret Come From?

A primary vulnerability in naive local authentication designs is **Caller Secret Self-Declaration**:
$$\text{Compromised Agent } A \longrightarrow \text{Generates Secret } S \longrightarrow \text{Transmits } S \text{ to DROS PEP}$$
Under Threat Level A0 (Compromised Agent), if the Agent chooses or tells the PEP what the secret is, an attacker can synthesize arbitrary keys and identities at will.

**Normative DROS Principle**:
> **"The Agent NEVER generates, chooses, or provisions its own execution authority or session secrets. Secrets are generated exclusively by the trusted DROS Session Manager and bound to kernel-verified process identities."**

---

## 2. Key Lifecycle & Provisioning Flow

The lifecycle of an ephemeral execution secret proceeds across four strictly bounded phases:

```
┌─────────────────────────────────────────────────────────────┐
│              DROS Session Manager (TRUSTED)                 │
│  - Runs in isolated PEP/GuardVM process                     │
│  - Generates 256-bit CSPRNG secrets via secrets.token_bytes │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ 1. Process Launch / Handshake
                               │    Kernel verifies Client PID/UID
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               OS Kernel Process Boundary                    │
│  - Linux: Inherited anonymous pipe / fd passing (SCM_RIGHTS)│
│  - Windows: Inherited restricted anonymous pipe / IPC       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ 2. One-Way Secret Injection
                               │    (Only target PID receives key)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Agent Process (Caller)                      │
│  - Holds k_session in private ephemeral memory              │
│  - Never writes k_session to disk or world-readable pipes   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ 3. Per-Request HMAC Signature
                               │    HMAC(k_session, Nonce || ArgHash)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             DROS PEP Execution Gate (TRUSTED)               │
│  - Recomputes HMAC using stored k_session                   │
│  - Verifies Peer PID matches registered Session Owner       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Threat Analysis of Key Storage & Distribution

| Key Distribution Vector | Attack Vector | Security Evaluation | Mitigation / Status |
| :--- | :--- | :--- | :--- |
| **World-Readable File (`/tmp/.dros_key`)** | Same-UID attacker (A2) reads file | **FATAL VULNERABILITY** | **FORBIDDEN**. Secrets must never touch the filesystem without user-private ACLs (`0600`). |
| **Environment Variable (`$DROS_SESSION_KEY`)** | Child process inherits or `/proc/$PID/environ` inspection | **HIGH RISK** | **DISCOURAGED**. Readable by any same-UID process on Linux unless restricted by Yama ptrace policy. |
| **Inherited Anonymous File Descriptor (Pipe)** | Point-to-point kernel channel | **SECURE (Baseline)** | Key is written directly to a private pipe at fork/exec; only the intended child PID possesses the descriptor. |
| **Initial UDS Handshake with `SO_PEERCRED`** | Connection initiates, PEP queries kernel for peer PID/UID | **SECURE (Hybrid Target)** | PEP provisions session only if the connecting PID matches the authorized orchestrator manifest. |

---

## 4. Key Storage, Lifetime, Rotation, and Revocation

1. **Storage**:
   - In-memory only. Session keys reside exclusively in non-swappable heap memory within the PEP process and Agent client wrapper.
2. **Lifetime**:
   - Ephemeral. Default TTL is bounded to $\text{TTL} = 3600\text{s}$ (1 hour) or the duration of the assigned task.
3. **Rotation**:
   - Automatic. After $N=10,000$ executions or upon task transition, the Agent must initiate a session rollover.
4. **Revocation**:
   - Immediate. When an administrative revocation event occurs (`revoke_session` or `revoke_capability`), the PEP marks the session token as revoked in memory. All subsequent requests presenting that session fail immediately with `SESSION_REVOKED`, even across persistent socket connections.

---

## 5. Can a Same-UID Attacker Steal the Key?

Under threat level **A2 (Same-UID Process)**:
* If the OS enables `/proc/$PID/mem` or `ptrace` for processes under the same UID (the Linux default without `Yama` LSM level 1+), a malicious same-UID process can technically read memory from the victim Agent process.
* **Rigorous Conclusion**:
  **IPC Authentication cannot prevent memory scraping if the OS allows unconfined intra-UID ptrace.**
  Therefore, Candidate C requires either:
  1. Linux Yama ptrace restriction (`/proc/sys/kernel/yama/ptrace_scope >= 1`), or
  2. Binding every session to the strict **Caller PID** (`session.peer_identity.pid == peer.pid`), so that even if a separate rogue process under the same UID obtains the key, the PEP rejects requests because the kernel reports the rogue process's distinct PID.
