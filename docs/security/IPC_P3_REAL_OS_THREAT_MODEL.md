# DROS Loopback IPC Phase P3 Threat Model & Real OS Boundary Specification (IPC_P3_REAL_OS_THREAT_MODEL.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE RESEARCH SPECIFICATION (PHASE P3)
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1`, `REPORT_P2_CONSOLIDATED_AUDIT.md`
* **Core Scientific Hypothesis**:
  $$\mathbf{\text{Execution Authority} = \text{Secret Possession} \land \text{OS-Attested Process Identity}}$$

---

## 1. Research Motivation & The PID Identity Problem

In Phase P2, Candidate C demonstrated that combining secret possession with OS peer attribution blocks stolen-key attacks. However, Phase P2 evaluated this under a simulated peer provider.

In Phase P3, we investigate the fundamental systems question:
> **"Is OS Process ID (PID) an authentic process identity, or merely a transient identifier? What OS-attested process identity binding is necessary and sufficient to prevent an attacker from porting execution authority across process boundaries?"**

---

## 2. Real OS Process Threat Scenarios (P3 Extensions)

We formalize four critical failure modes inherent to real operating system execution boundaries:

### Scenario 1: Real Same-UID Attacker with Stolen Credentials (IPC-013-R)
* **Precondition**: Two distinct OS processes execute under the identical UID (`uid=1000` on Linux, same user SID on Windows).
* **Adversary Action**: Process B ($PID_B$) steals the valid 256-bit session secret, capability token, and nonce of Process A ($PID_A$). Process B connects directly to the real DROS IPC endpoint.
* **Security Invariant**: The real OS transport kernel must deliver the authentic caller PID. The PEP must evaluate $PID_B \neq PID_A$ and reject execution with `SESSION_PEER_MISMATCH`.

### Scenario 2: PID Recycling & Reuse Vulnerability (IPC-016)
* **The Vulnerability Vector**:
  $$\text{Agent A } (PID_1) \longrightarrow \text{Session Issued} \longrightarrow \text{Agent A Exits} \longrightarrow \text{OS Reuses } PID_1 \longrightarrow \text{Attacker B } (PID_1)$$
  If authentication binds solely to the numerical integer `pid`, an attacker who inherits or forces the recycling of $PID_1$ can inherit Agent A's unexpired session authority.
* **The Countermeasure Hypothesis**:
  $$\text{Process Identity} = \langle \text{PID},\ \text{Process Start Time (create\_time)} \rangle$$
  Because a newly spawned process recycling $PID_1$ possesses a strictly greater `create_time` than the defunct Agent A, checking $\Delta t_{\text{start}} == 0$ detects and eliminates PID reuse attacks.

### Scenario 3: Real Fork & Child Process Credential Inheritance (IPC-018-R)
* **The Vulnerability Vector**:
  On Unix systems, `os.fork()` creates an exact clone of the address space. Child process $PID_{\text{child}}$ inherits the session secret in heap memory.
* **The Countermeasure Hypothesis**:
  Upon connection, the kernel reports $PID_{\text{child}} \neq PID_{\text{parent}}$. The child cannot execute using the parent's session unless a new session is formally negotiated.

### Scenario 4: Real Socket Persistent Connection Revocation (IPC-010-R)
* **The Vulnerability Vector**:
  A client maintains an active, open TCP/UDS/Named-Pipe connection. An administrative revocation signal is dispatched to the PDP.
* **Security Invariant**:
  The PEP must evaluate revocation state on *every incoming request frame*, not merely during the initial socket connection handshake.

---

## 3. Normative Acceptance Criteria for Phase P3

| Evaluation Item | Real Linux Environment | Real Windows Environment |
| :--- | :--- | :--- |
| **Transport Boundary** | Real Unix Domain Socket (`AF_UNIX`) | Real Named Pipe (`\\.\pipe\...`) |
| **Kernel Identity Extraction** | `SO_PEERCRED` / `SCM_CREDENTIALS` | `GetNamedPipeClientProcessId` + Token SID |
| **Attribution Tuple** | $\langle \text{pid},\ \text{create\_time},\ \text{uid} \rangle$ | $\langle \text{pid},\ \text{create\_time},\ \text{user\_sid} \rangle$ |
| **Adversarial Execution** | Separate OS subprocesses via `subprocess.Popen` | Separate OS subprocesses via `subprocess.Popen` |
| **Report Status Rule** | If executed $\to$ `PASS` / `FAIL`<br>If unexecuted $\to$ `NOT EXECUTED` | If executed $\to$ `PASS` / `FAIL`<br>If unexecuted $\to$ `NOT EXECUTED` |
