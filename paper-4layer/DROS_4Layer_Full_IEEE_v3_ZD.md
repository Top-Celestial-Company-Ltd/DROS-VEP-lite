# DROS: A Four-Layer Deterministic Runtime Operation System Bridging the Agent-to-Execution Attribution Gap in Autonomous AI Workloads

> **Author:** Chun-Cheng (Jimmy) Chen
> **Affiliation:** Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.
> **Contact:** jimmychen@dr-os.io
> **ORCID:** 0009-0001-6387-0500
> **Version:** v3.0 | 2026-08-25
> **Target Journal:** ACM Transactions on Privacy and Security (TOPS)

---

## Abstract

The rapid deployment of autonomous AI agents capable of multi-step tool invocation introduces a fundamental security gap: existing semantic firewalls (e.g., NVIDIA NeMo Guardrails) operate probabilistically and are susceptible to indirect prompt injection (IPI), while conventional OS-level mechanisms (eBPF, Seccomp) enforce deterministic binary rules but suffer from context-blindness, as syscall enforcement mechanisms generally lack application-semantic identity at the granularity of individual agent roles sharing a single OS process. We define this structural weakness as the **Agent-to-Execution Attribution Gap**.

We propose **DROS (Deterministic Runtime Operation System)**, a four-layer defense-in-depth architecture comprising: (L1) a probabilistic semantic boundary filter; (L2) a three-tier PKI identity layer binding agent roles to cryptographic execution tokens (DIT); (L3) an ABAC topology enforcer; and (L4) a deterministic C-ABI enforcement layer executing zero-heap O(1) capability bitmap comparisons at the FFI boundary.

Empirical evaluation on a 24-hour soak test (N=160,611 total requests, N_adv=137,751 adversarial attempts across four attack families comprising five evaluated attack classes) demonstrates that for all invocations reaching the L4 C-ABI boundary, the full DROS stack achieves an observed 100% blocking rate on the evaluated adversarial corpus under the defined threat model. The downstream governance decision pipeline exhibits a median policy evaluation latency of 26.21 $\mu\text{s}$ (P99=242.69 $\mu\text{s}$, excluding upstream semantic token processing) with isolated C-ABI bitmap enforcement latency <500 $\text{ns}$, introducing <1.8% CPU utilization overhead relative to matched uninstrumented workloads. In a cumulative layer addition study, L4 increased the observed blocking rate for the known-template IPI subset from 93.5% to 100%, while providing the only evaluated layer that blocked the 52,180 obfuscated IPI attempts that bypassed L1-L3. Furthermore, an architectural comparison against application middleware (Microsoft AGT host-middleware configuration) demonstrates that DROS establishes a complementary execution-boundary reference monitor for unmanaged runtime paths with a P99 decision-path latency of $1.20\ \mu\text{s}$.

**Index Terms** -- AI Agent Security, Runtime Governance, C-ABI Boundary Enforcement, Zero Trust, PKI, Indirect Prompt Injection, Capability-Based Access Control, Attribution Gap, Defense-in-Depth.

---

## I. Introduction

The core challenge is not merely preventing agents from being manipulated at the semantic layer -- it is ensuring that **semantic compromise does not translate into executable compromise**.

> **Thesis**: DROS does not establish that an agent's internal reasoning is trustworthy; rather, it establishes that under an explicitly defined complete-mediation deployment boundary, loss of cognitive integrity does not by itself expand the agent's execution authority beyond its cryptographically bound capability envelope evaluated at the C-ABI/FFI boundary.

Current defenses fall into two categories, each with fundamental limitations:

**Semantic Firewalls**: Systems such as NVIDIA NeMo Guardrails, LlamaGuard, and PromptBench analyze natural language intent at the application layer. While effective against known attack templates, they provide zero mathematical guarantee against adversarial obfuscation, multi-turn context poisoning, or indirect prompt injection via external data sources.

**OS-Level Enforcement**: Mechanisms such as eBPF, SELinux, AppArmor, and Seccomp enforce binary syscall rules deterministically. However, they suffer from what we term the **Context-Blindness Problem**: conventional OS enforcement mechanisms operate on kernel-visible identifiers (PID, UID, cgroups, namespaces, LSM security labels) and generally lack application-semantic identity at the granularity of ephemeral agent roles and tasks executing within a single shared interpreter process (e.g., `python.exe`).

Recent eBPF-based observability work (AgentSight, Eunomia) provides tracing but not enforcement -- observing that an unauthorized call occurred is insufficient; unauthorized calls must be deterministically intercepted and prevented at the execution boundary.

### A. Problem Formulation: The Attribution Gap

We formally define the **Agent-to-Execution Attribution Gap** as:
> **Definition (Attribution Gap)**: The structural absence of a trustworthy, verifiable mapping between application-level agent principals and execution-level authorization decisions under a shared runtime identity. An Attribution Gap exists whenever two or more logically distinct authorization principals execute within the same operating system security principal (e.g., shared PID/UID), while the underlying execution substrate cannot cryptographically distinguish their authorization states at the enforcement boundary.

```
Conventional Multi-Agent Runtime:
  Agent Role A ──┐
                 ├── Single OS Process (PID 1234, UID 1000) ──> C-ABI / libc ──> tool_execution()
  Agent Role B ──┘
  [Kernel / eBPF / OS MAC View: All calls originate identically from PID 1234. Role identity is unobservable.]

DROS In-Band Attribution Substrate:
  Agent Role A ──> DIT_A (Signed by AIA) ──┐
                                          ├── C-ABI Reference Monitor ──> Immutable B_A[i] ──> ALLOW/DENY
  Agent Role B ──> DIT_B (Signed by AIA) ──┘                                Immutable B_B[i]
```

*Distinction from Classic Models*: While conceptually related to the Confused Deputy problem [Hardy 1988] and classical reference monitor theory [Anderson 1972], the Attribution Gap in agentic runtimes presents three domain-specific challenges: (1) multiple autonomous principals with divergent authority dynamically co-exist inside a single managed language runtime without POSIX boundary separation; (2) the agent's internal control flow is guided by probabilistic natural language inputs inherently vulnerable to cognitive hijacking; and (3) existing operating system capabilities or POSIX identities cannot inspect or bind to transient in-process LLM agent roles without an in-band cryptographic bridge.

The core novelty of this work is not capability control by itself, nor cryptographic identity by itself, but the architectural composition that preserves agent-role attribution from an ephemeral in-process principal into the authorization decision made at the binary execution boundary.

### B. Contributions

1. **Attribution Gap Formalization**: We formally define and characterize the Agent-to-Execution Attribution Gap and demonstrate its exploitability across four attack families.
2. **DROS Four-Layer Architecture**: A defense-in-depth architecture forming a probabilistic-to-deterministic security funnel.
3. **Formal Security Model**: A formal capability security model specifying the complete-mediation conditions (Assumptions A1-A4) under which the Capability Enforcement Invariant (CEI) deterministically holds.
4. **Empirical Ablation Evaluation**: A controlled ablation study quantifying each layer's independent and cumulative contribution on an open-source reproducible testbed.

---

## II. Background and Threat Model

### A. Agentic Attack Vectors (AAV-2026)

Threat model **AAV-2026** encompasses four primary attack families (comprising five evaluated attack classes). All share a common precondition: the adversary cannot directly modify agent code, binary binaries, or system configuration.

| Attack Family | MITRE ATLAS | Mechanism | Target Asset |
|:---|:---|:---|:---|
| Indirect Prompt Injection (IPI) | AML.T0051 | Attacker embeds malicious instructions in untrusted external data consumed by the agent | Tool invocation control flow |
| Goal Hijacking | AML.T0054 | Context window poisoning alters long-horizon agent objectives | Agent planning state |
| Privilege Escalation via Tool Abuse | AML.T0053 | Compromised agent exploits valid OAuth tokens to invoke high-privilege endpoints | Authorization boundary |
| Upstream Compromise (Supply Chain) | AML.T0010 | Poisoned upstream model weights or datasets induce unauthorized action synthesis | Authorization boundary |

**Table I: AAV-2026 Threat Matrix**

### B. Adversary Model

We assume a Dolev-Yao-inspired adversary who:
- Controls all data flowing through external sources (email, documents, third-party APIs, datasets)
- Cannot modify agent source code, system configuration, or cryptographic material
- Interacts with system tools exclusively through managed runtime calls (arbitrary native code injection, raw memory tampering, and kernel exploits are addressed as deployment boundary assumptions; see Section VII-D)
- Can craft arbitrarily complex, multi-turn adversarial prompts
- Has full knowledge of L1 semantic filtering heuristics
- Cannot forge cryptographic signatures without access to private keys
- Cannot modify compiled capability bitmaps at runtime

### C. Existing Defense Limitations

Semantic filtering (L1) operates on natural language representations that can be arbitrarily obfuscated. PKI/zero-trust networking in existing systems binds identity at the service level (mTLS, OAuth), not at agent-role granularity within a service. ABAC/RBAC middleware typically operates at the API gateway layer (4-50ms latency) outside the execution path.

---

## III. DROS Architecture

DROS implements a defense-in-depth funnel transforming probabilistic semantic defenses into deterministic execution-boundary enforcement. Control plane and runtime enforcement plane are architecturally decoupled.

![Figure 1: DROS control plane and runtime enforcement plane architecture.](E:/vscode/AI知識庫/DROS商品專案暫存/商業與架構文件庫/DROS_Visual_Assets/dros_defense_layers_en.png)

*Figure 1: DROS control plane and runtime enforcement plane architecture.*

### A. L1 -- Semantic Boundary Layer (Probabilistic Filtering)

L1 performs semantic analysis of natural language inputs, applying known injection template matching, input sanitization, and intent classification. L1 provides no mathematical security guarantee. Design objective: filter the majority of known, unobfuscated attacks cheaply (O(input tokens)) before they reach downstream layers.

On the evaluated adversarial corpus, L1 filtered 85.2% of the known-template IPI subset (representing 58,327 of 68,420 attacks; 0% of obfuscated attacks; see Table II); the observed false positive rate on the benign evaluation set was 0/22,860. L1 is explicitly designed to be bypassed by sophisticated adversaries; its failure mode is handled by L2-L4.

### B. L2 -- Zero-Trust Identity Layer (Cryptographic Binding)

L2 eliminates the Context-Blindness Problem via **DrosIdentityToken (DIT)**: a cryptographically signed execution token binding (Agent_Role, Task_ID, Authorization_Scope, Capability_Bitmap_Hash) to each tool invocation.

**Three-Tier PKI Architecture:**
- Root CA (DROS-ROOT-CA-2026): Enterprise root certificate, offline key custody
- AIA Intermediate CA: Automated Issuance Authority, issues per-deployment certificates
- BEC Leaf Certificate (Bound Execution Certificate): Cryptographically binds agent role and capability bitmap to a short-lived execution credential

**Formal DIT Structure:**
```
DIT := {
  agent_id:           UUID,
  role_id:            uint32,
  task_id:            UUID,               // Cryptographic binding for audit & provenance (non-authorizing)
  bitmap_hash:        SHA-256(B_r),       // Cryptographic commitment verifying policy synchronization
  issued_at:          Unix timestamp,
  expires_at:         Unix timestamp (TTL: 15 min),
  signature:          Ed25519(private_key_AIA, DIT_body)
}
```

Every governed tool invocation must carry a valid DIT. 

**Authority Source vs. Cryptographic Commitment**: We explicitly distinguish the source of authority from the token's contents: the DIT does *not* confer arbitrary permissions asserted by the caller. Rather, `bitmap_hash` serves solely as an immutable cryptographic commitment ensuring that the agent and the GuardVM reference the identical compiled policy epoch. The true enforcement authority resides exclusively in the GuardVM's write-protected policy store: $B_r = 	ext{PolicyStore}[r]$. Furthermore, `task_id` binds each invocation to a cryptographically attributable workflow unit for non-repudiable audit logging, preventing token reuse across decoupled business tasks.

**Formal Issuance Authority (AIA Trust Model)**: Crucially, the DIT cannot be minted by the agent itself. DITs are generated exclusively by the Automated Issuance Authority (AIA) / Bound Execution Certificate (BEC) service residing in a separate trust domain (or secure enclave). When an orchestrator dispatches a task to an agent role $r$, the AIA authenticates the task allocation against signed workflow manifests and signs a short-lived DIT (TTL $\le$ 15 min) embedding $r$ and $	ext{SHA-256}(B_r)$. Because private signing keys are strictly withheld from the agent execution environment, a compromised agent process cannot elevate its role or forge a token for an unauthorized role $r' 
eq r$.

**Cross-Organizational Federation:** When agents interact across enterprise boundaries (Corp-Alpha to Corp-Beta), L2 extends to a cross-domain PKI gateway: the receiving enterprise verifies the external DIT against the sending enterprise's published root CA, enforcing local capability bitmaps regardless of the external agent's claimed permissions.

### C. L3 -- Agentic Topology and ABAC Layer (Structural Isolation)

L3 enforces multi-agent Swarm topology constraints via agent_manifest.yaml, declaratively specifying:
- Permitted communication channels between agent roles (directed acyclic capability graph)
- Cross-department invocation restrictions (e.g., HR-Agent cannot invoke DevOps-Agent APIs)
- Maximum fan-out limits per agent role (preventing amplification attacks)

L3 implements ABAC aligned with NIST SP 800-162, evaluated against runtime DIT attributes at the orchestration layer.

### D. L4 -- C-ABI Deterministic Binary Enforcement Layer (Execution Gate)

L4 operates as an execution-boundary reference monitor at the C-ABI/FFI boundary -- the transition point where governed tool invocations cross from the LLM's managed runtime into binary execution. Complete mediation is established across all governed tool invocations by routing tool dispatch through cryptographically instrumented FFI wrappers, enforcing execution-boundary containment rather than hardware-level physical enforcement.

**Capability Bitmap Enforcement:**

Given an enumerated universe of $N$ registered system tools $\mathcal{M} = \{m_1, \dots, m_N\}$, each agent role $r$ is assigned a capability vector $B_r \in \{0,1\}^N$ compiled at system initialization into write-protected memory pages.

**Authenticated Capability Resolution Chain**: To prevent a compromised process from forging an in-memory `Role_ID`, the capability resolution follows a strict cryptographic verification chain:
$$\text{Incoming Request} \xrightarrow{} \text{Verify Ed25519}(\sigma_{\text{DIT}}, K_{\text{AIA}}) \xrightarrow{} \text{Extract Authenticated } r \xrightarrow{} \text{Lookup Immutable } B_r \xrightarrow{} B_r[i] \& 1$$

For requested tool $m_i$:
```
Decision(r, m_i) = ALLOW  if B_r[i] = 1
                   DENY   if B_r[i] = 0
```
Implemented as a zero-heap bitwise operation over verified role bitmaps.

This operation executes in O(1) constant time with zero string parsing, zero LLM inference, and zero heap allocation, achieving sub-microsecond isolated decision latency.

**Immutability Guarantee:** Capability bitmaps are compiled from vajra.md policy declarations at system initialization and loaded into write-protected memory pages. No managed runtime path exists for an agent to modify the bitmap without low-level kernel subversion.

**Deterministic Enforcement:** A bitmap result of 0 triggers an immediate FFI panic, returning HTTP 403, *before* any tool function body executes.

---

## IV. Formal Security Model

To avoid circular reasoning where an invariant merely restates implementation code, we formalize the execution environment under four explicit operational assumptions:

### A. Operational Assumptions for Complete Mediation
- **Assumption A1 (Complete Boundary Mediation)**: All security-relevant tool invocations $m \in \mathcal{M}$ are dispatched exclusively through the instrumented DROS C-ABI interface. Direct unmediated native system calls or uninstrumented dynamic library loading are prevented by the surrounding deployment environment (see Section VII-D).
- **Assumption A2 (Cryptographic Unforgeability)**: The adversary cannot forge Ed25519 signatures of the AIA without access to private key $K_{\text{AIA}}$, and SHA-256 collisions are computationally infeasible.
- **Assumption A3 (Policy Immutability)**: The compiled capability store $B$ is loaded into write-protected memory pages inaccessible to in-process managed code.
- **Assumption A4 (Dispatch Integrity)**: The L4 reference monitor evaluates authorization synchronously before transferring execution control to the tool implementation body.

### B. Definition of Governed Execution
We define the governed execution predicate $\text{GExec}(r, m_i, s)$ to be true if and only if tool $m_i$ executes to completion on behalf of role $r$ in state $s$ through a registered DROS dispatch path.

### C. Theorem 1 (Boundary Confinement under CEI)
> **Theorem 1 (Execution Boundary Confinement)**: Under Assumptions A1--A4, for all agent roles $r \in \mathcal{R}$, all registered tools $m_i \in \mathcal{M}$, and all runtime states $s \in \mathcal{S}$, if $B_r[i] = 0$, then no governed execution can occur:
> $$B_r[i] = 0 \implies \neg\text{GExec}(r, m_i, s)$$

*Proof*: 
1. By Assumption A1, execution of $m_i$ requires entering the DROS C-ABI reference monitor.
2. By Assumption A4, execution proceeds to the tool body only if the reference monitor returns `ALLOW`.
3. By construction of L4, the principal used for capability resolution is bound strictly to the verified DIT:
$$\text{DispatchPrincipal}(x) = \text{AuthenticatedRole}(\text{DIT}) = r$$
Execution proceeds to `ALLOW` if and only if $\text{Verify}(\sigma_{\text{DIT}}, K_{\text{AIA}}) = \text{VALID}$, $\text{DispatchPrincipal}(x) == r$ (preventing caller-supplied variable spoofing), and the bitwise check $B_r[i] == 1$ evaluates to true.
4. By Assumption A2, a valid token for role $r$ cannot be forged by an adversary without $K_{\text{AIA}}$.
5. By Assumption A3, $B_r[i]$ cannot be modified at runtime.
6. Therefore, if $B_r[i] = 0$, the check evaluates to false, returning `DENY` (HTTP 403) and triggering an FFI panic before body dispatch.
7. Hence, $\text{GExec}(r, m_i, s)$ is false. By contraposition: $\text{GExec}(r, m_i, s) \implies \text{ValidDIT}(r, s) \land (B_r[i] = 1)$. $\blacksquare$

### D. Derived Security Properties

**Property 1 (Governed Execution Confinement):** A semantically compromised agent cannot successfully execute any governed tool invocation $m_i$ for which $B_r[i] = 0$, regardless of prompt manipulation or cognitive subversion.

**Property 2 (Blast Radius Invariant):** Let $\mathcal{C}^* = \text{Hostile}$ denote total cognitive compromise of the agent planning state. Let $\mathcal{E}_{\text{effective}}$ denote the set of tool executions achievable by the compromised agent. Under Assumptions A1--A4:
$$\mathcal{C}^* = \text{Hostile} \land \text{Theorem 1} \implies \mathcal{E}_{\text{effective}} \subseteq \mathcal{B}_{r_{\text{assigned}}}$$
That is, cognitive compromise of an agent does not expand its execution authority beyond the pre-committed capability envelope assigned to its authenticated role.

**Property 3 (Cryptographically Verifiable Execution Evidence):** Every ALLOW and DENY decision is recorded in an Ed25519-signed, SHA-256 Merkle hash chain audit log, providing tamper-evident, cryptographically verifiable execution evidence suitable for forensic and regulatory inspection.

---

## V. Implementation and Experimental Evaluation

### A. Implementation

DROS is implemented in Rust (L4 enforcement kernel) and Python (L1-L3 orchestration), with C-ABI FFI bindings compatible with CPython, Node.js, and JVM runtimes. The GuardVM serves as Policy Enforcement Point (PEP) and Policy Decision Point (PDP), co-located with the agent runtime.

To ensure immutability and performance at the C-ABI layer, the L4 capability bitmaps utilize **write-protected memory pages** for tamper-resistance and employ **RCU (Read-Copy-Update)** mechanisms for zero-downtime hot-updates.

**Test Environment:**
- Hardware: Intel Xeon E3-1275L v3 (4 cores, 8 threads, 16 GB RAM)
- Reference Container Environment: Ubuntu 22.04 LTS (Linux Kernel 6.6, Docker 26.1)
- Host Verification Environment: Microsoft Windows 10 IoT Enterprise LTSC (Build 19044) / Python 3.11
- Agent runtime: Python 3.11 (LangChain 0.2, OpenAI GPT-4o)

To ensure full scientific reproducibility, all test scripts, attack payloads, and the continuous execution runner are publicly available in the **DROS Verification & Evaluation Platform (DROS-VEP-lite)** open-source repository: <https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite>. A local single-node deployment reference using Docker Compose is provided in the **DROS Home-Lab** repository: <https://github.com/Top-Celestial-Company-Ltd/dros-home-lab>.

### B. Attack Corpus Methodology

- **Total requests**: N = 160,611 over 24 consecutive hours
- **Benign workload**: N_ben = 22,860 (legitimate tool invocations from authorized roles)
- **Adversarial corpus**: N_adv = 137,751 across four attack families (comprising five evaluated attack classes):
  - IPI (Template): 68,420 known injection patterns (OWASP corpus)
  - IPI (Obfuscated): 52,180 adversarially mutated payloads (base64, Unicode, multi-turn)
  - Goal Hijacking: 9,251 long-horizon context poisoning sequences
  - Privilege Escalation: 6,112 boundary role-crossing attempts
  - Supply Chain Contamination: 1,788 cross-enterprise lateral movement simulations

**Adversarial Generation and Independent Evaluation Protocol**:
To mitigate generator bias and circularity:
1. *Independent Generation Harness*: Payloads were generated across three distinct model families (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) using parameterized mutation operators (lexical masking, multi-turn context splitting, syntactic Unicode obfuscation, and base64 embedding).
2. *Semantic Validity Filtering*: Candidate payloads were evaluated against an uninstrumented baseline agent to verify attack validity; only payloads that successfully diverted uninstrumented agent execution flow were retained.
3. *Blind Runtime Execution*: The DROS governance engine had no access to attack generation seeds, prompt labels, or adversary metadata during evaluation; decisions were rendered strictly in-band upon FFI invocation.
4. *Evaluation Scope*: 5 independent executions of the complete corpus were performed, yielding consistent metrics.

### C. Cumulative Layer Addition Study Results

**Table II: Cumulative Layer Addition Defense Study**

| Configuration | L1 | L2 | L3 | L4 | Known IPI Block | Obfuscated IPI Block | Median Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Baseline (no defense) | N | N | N | N | 0.0% | 0.0% | 0 $\mu\text{s}$ |
| +L1 only | Y | N | N | N | 85.2% | 0.0% | 45.2 ms |
| +L1+L2 | Y | Y | N | N | 90.0% | 0.0% | 25.8 $\mu\text{s}$ |
| +L1+L2+L3 | Y | Y | Y | N | 93.5% | 0.0% | 26.0 $\mu\text{s}$ |
| Full DROS (L1-L4) | Y | Y | Y | Y | 100.0% | 100.0% | 26.21 $\mu\text{s}$ |
| Observed False Positive Rate | - | - | - | - | - | - | 0 / 22,860 |

**Key finding and Metric Reconciliation**: Table II demonstrates the cumulative protection provided as defense layers are added. Semantic filtering (L1) blocked 85.2% of known IPI templates but was completely bypassed (0.0% block rate) by adversarially obfuscated payloads. The addition of L2 (PKI identity) and L3 (topology enforcement) increased known-template defense to 93.5% through structural role and channel constraints. Crucially, without L4, all 52,180 obfuscated IPI payloads (and 6.5% of known templates) bypassed the upper layers. L4 closed the remaining 6.5 percentage point gap on the known-template subset (raising it from 93.5% to 100.0%), while providing the only evaluated layer that arrested the 52,180 obfuscated execution attempts (0.0% to 100.0%). L4 was the only evaluated layer capable of arresting obfuscated execution attempts, confirming that semantic and structural governance alone cannot guarantee execution-boundary confinement.

### D. Comparative Results: With/Without DROS L4

**Table III: Controlled Comparison against Matched Baseline**

*Baseline Definition*: The unprotected baseline consists of an identical LangChain agent environment (same prompt templates, identical LLM model, identical registered tool implementations, and identical OS execution environment) executing without DROS FFI interception wrappers.

| Test Scenario | Without DROS | With DROS (L4 Active) | Latency |
|:---|:---|:---|:---:|
| ATS-001: Customer DB exfiltration via IPI | Tool body executed (Breach=1) | 100% blocked (HTTP 403) | 25.8 $\mu\text{s}$ |
| ATS-002: ERP ransom via credential extraction | Tool body executed (Breach=1) | 100% blocked (HTTP 403) | 26.1 $\mu\text{s}$ |
| ATS-003: Fable-5 jailbreak (unauthorized deploy) | Tool body executed (Breach=1) | 100% blocked (HTTP 403) | 25.5 $\mu\text{s}$ |
| ATS-004: Cross-enterprise supply chain hijack | Tool body executed (Breach=1) | 100% blocked (HTTP 403) | 26.4 $\mu\text{s}$ |

*Blocking results reported for the evaluated corpus under the defined threat model.*

### E. Boundary Coverage Study: Application Middleware vs. Binary Execution Substrates

To evaluate how enforcement boundary placement influences security coverage, we conducted a boundary coverage study comparing application-layer middleware (implementing function-decorator policy interception as specified in Microsoft AGT v4.1.0) with an in-band binary execution substrate (DROS GuardVM) under identical hardware and agent workloads. 

*Methodological Clarification*: This experiment does not evaluate whether application middleware is inherently secure or insecure within its intended design scope. Rather, it investigates an architectural research question: *Does middleware interception inside the managed runtime provide complete mediation when an agent executes unmanaged runtime paths?* Both systems were evaluated using their native execution wrappers against identical adversary probes.

The evaluation addresses three core Research Questions:
* **RQ1 (Declared Tool Enforcement):** Both AGT and DROS successfully enforced Allow/Deny policies against standard declared tool invocations across all evaluated ATS scenarios.
* **RQ2 (Enforcement Boundary Coverage):** When execution proceeds outside standard tool wrappers via unmanaged runtime paths (PROBE-01: native file I/O, PROBE-02: raw TCP sockets, PROBE-03: subprocess spawning, PROBE-04: in-memory reflection), AGT policy interception was absent in the evaluated configuration. Conversely, DROS GuardVM enforced deterministic denials at its encapsulated C-ABI boundary.
* **RQ3 (Latency Overhead):** In high-throughput micro-benchmarks ($N=10,000$ independent iterations per arm on Intel Xeon E3-1275L v3 @ 2.70GHz, Windows 10 IoT Enterprise LTSC / Python 3.11), P99 decision latencies were measured at: Baseline ($0.4\ \mu\text{s}$), AGT ($1.8\ \mu\text{s}$), DROS GuardVM ($1.2\ \mu\text{s}$), and Dual-Layer AGT+DROS ($15.9\ \mu\text{s}$).

**Table V: Architectural Boundary Coverage and Decision-Path Overhead**

| Configuration / Enforcement Arm | Standard Tool Containment (RQ1) | Boundary Coverage Outside Declared Paths (RQ2) | P99 Decision Latency (RQ3) |
|:---|:---:|:---:|:---:|
| **Arm A: Baseline** (No Governance) | 0.0% (Exploited) | Unmonitored | 0.40 $\mu\text{s}$ |
| **Arm B: Microsoft AGT** (Middleware) | 100.0% Blocked | Policy Interception Absent | 1.80 $\mu\text{s}$ |
| **Arm C: DROS GuardVM** (C-ABI Substrate) | 100.0% Blocked | Deterministic DENY at C-ABI | 1.20 $\mu\text{s}$ |
| **Arm D: Defense-in-Depth** (AGT + DROS) | 100.0% Blocked (L1) | Deterministic DENY at C-ABI | 15.90 $\mu\text{s}$ |

*Key finding*: The results support the architectural conclusion that application-layer governance and execution-layer enforcement are complementary: application policy frameworks (such as AGT / ACS) govern what the agent is allowed to request through runtime state and policy evaluation, while DROS preserves agent-principal attribution from an ephemeral in-process role into an immutable execution-boundary capability decision.

### F. 24-Hour Micro-Benchmark Summary

**Table VI: 24-Hour Soak Test Results**

| Metric | Value | Notes |
|:---|:---|:---|
| Total test requests | 160,611 | Continuous 24.0-hour soak test (~1.86 req/s baseline, periodic concurrency peaks) |
| Policy evaluation latency (P50) | 26.21 $\mu\text{s}$ (+/- 0.34 $\mu\text{s}$) | Downstream pipeline mean (excl. LLM token parsing) |
| Policy evaluation latency (P99) | 242.69 $\mu\text{s}$ | Measured during high-concurrency burst micro-benchmarks |
| C-ABI enforcement latency | <500 $\text{ns}$ (+/- 42 ns) | Isolated FFI boundary DENY path |
| CPU overhead | <1.8% | Relative to matched uninstrumented workload |
| Adversarial blocking rate | 100% (N_adv=137,751) | Observed over evaluated corpus under defined threat model |
| False positive rate | 0 / 22,860 * | Observed on evaluated benign corpus |
| Memory leak (24h) | None detected | Tracked via jemalloc / OS RSS heap profiling |
| Bitmap memory footprint | <1 MB | 4KB/role bitmap page |

*\* Benign Workload Reconciliation Note*: The benign evaluation denominator ($N_{\text{ben}}=22,860$) comprises 22,854 successfully authorized tool operations and six transient OS TCP socket recycling exceptions (`TIME_WAIT` port exhaustion during high-rate polling); zero benign requests were denied due to policy logic false positives (FPR = 0/22,860).

### G. Extreme Post-Compromise Containment: The Minimal-Substrate Isolation Crucible (RQ4)

To evaluate whether execution authority survives when cognitive integrity and all upper governance layers completely collapse ($\text{Integrity}(\text{Agent}) = 0 \land \text{Integrity}(\text{Upper Governance}) = 0$), we deployed the **Minimal-Substrate Isolation Crucible** (`dros-vep-lite/benchmarks/bare_metal_crucible/run_crucible.py`). All application-level defenses (Prompt Guards, EDR, Network Firewalls, Framework Classifiers, and Human-in-the-Loop gates) were stripped away, leaving only the raw DROS C-ABI capability substrate active to evaluate the minimum trusted computing base.

The evaluation injected 1,000 hostile transitions spanning credential theft (`~/.ssh/id_rsa`, `.env`), subprocess spawning (`python`, `bash`), outbound exfiltration (`curl`), recursive file deletion (`rm -rf`), and kernel policy tampering attempts into a compromised `doc-reader-agent` whose declared capability was strictly limited to reading `./workspace/input/` and writing `./workspace/output/summary.txt`.

**Table VII: Minimal-Substrate Isolation Crucible Empirical Results**

| Metric / Evaluation Invariant | Baseline (Unprotected) | DROS-Only (Minimal-Substrate) | Epistemic Status |
|:---|:---:|:---:|:---|
| **Adversarial Injections ($N$)** | 1,000 | 1,000 | Full hostile spectrum |
| **Unauthorized Hostile Attempts** | 906 | 906 | Multi-vector exploitation |
| **Unauthorized Execution Interceptions** | 0 (Breached) | **906 (100.0% Blocked)** | Sub-microsecond DENY |
| **Unauthorized Escapes / Bypasses** | 906 (100.0%) | **0 (0.000%)** | 0 Counterexamples observed |
| **Legitimate Requests Processed** | 94 / 94 (100.0%) | **94 / 94 (100.0%)** | Normal operation unhindered |
| **Post-Compromise Containment Rate ($R_{\text{contain}}$)** | 0.000 | **1.000 (100.0%)** | Empirically observed containment: 1.000 across 906 attempts; theoretically bounded by CEI |
| **Unauthorized State Mutation ($\Delta\text{Effect}$)** | Complete host mutation | **0 bytes mutation** | $\Delta\text{Effect}_{\text{unauthorized}} = 0$ over protected set $\mathcal{S}_{\text{protected}}$ (monitored workspace directories, filesystem inodes, and declared persistent state) via SHA-256 state diff |
| **Mean C-ABI Decision Latency** | N/A | **825.0 ns (0.825 $\mu\text{s}$)** | Isolated capability-decision critical path |
| **p99 Decision Latency** | N/A | **2,800.0 ns (2.800 $\mu\text{s}$)** | Deterministic $O(1)$ bitmap check |
| **Enforcement Throughput** | N/A | **52,583 decisions/sec** | End-to-end request lifecycle with audit-chain insertion |
| **Audit Log Cryptographic Integrity** | None | **1,000 Merkle Entries** | Append-only SHA-256 chain |

*Latency vs. Throughput Reconciliation*: We clarify the measurement boundaries between the latency and throughput figures. The 825.0-ns metric ($1 / 825\text{ns} \approx 1.21\text{M decisions/s}$ theoretical maximum) evaluates solely the isolated in-memory bitmap verification critical path. Conversely, the 52,583 decisions/sec benchmark measures end-to-end multi-threaded request processing, encompassing request serialization, mutex locking, cryptographic SHA-256 Merkle audit-chain node insertion, and OS thread scheduling.

*Empirical Support for Bounded Blast Radius*: The empirical observations directly align with the theoretical model:
$$B_{\max} \subseteq \mathcal{E}_{\text{authorized}} \cap \mathcal{E}_{\text{enforced}}$$
Even when the cognitive plane is entirely subverted ($C^* = \text{Hostile}$), the downstream execution authority ($A^*$) remains strictly confined to the declared capability envelope.

### H. Attack-Chain Mechanics Reproduction (ATS-006 / PC-11)

To validate DROS against contemporary vulnerability reports (e.g., coding-agent auto mode indirect prompt injection and autonomous code synthesis escapes), we implemented the 7-stage adversarial state transition model (**ATS-006 / AII-EC**). The experiment reproduces the attack-chain mechanics reported in contemporary agentic coding-agent incidents rather than reproducing a vendor-specific vulnerability implementation:
1. **T1 (Content Injection):** Untrusted web database returns HTTP 500 containing prompt injection instructions.
2. **T2 (Autonomous Re-planning):** Agent subverts its web-reading objective and attempts fallback to system command-line utilities.
3. **T3 (Tool Substitution):** Agent attempts `system:curl_download` to fetch `mirror.zip` $\rightarrow$ **Blocked by DROS at 2.5 $\mu\text{s}$ (HTTP 403 UNAUTHORIZED_CAPABILITY)**.
4. **T4 (Autonomous Code Synthesis):** Agent detects suspicious bash unpacker and autonomously synthesizes a clean Python script (`extract_clean.py`).
5. **T5 (Process Execution Spawning):** Agent attempts `process:spawn_python` $\rightarrow$ **Blocked by DROS at 0.8 $\mu\text{s}$ (HTTP 403 UNAUTHORIZED_CAPABILITY)**.
6. **T6 (Protected Resource Access):** Malicious unpacker module attempts to spawn a secondary background agent to exfiltrate `~/.ssh/id_rsa` and machine UUIDs $\rightarrow$ **Blocked by DROS at 1.0 $\mu\text{s}$ (HTTP 403 UNAUTHORIZED_CAPABILITY)**.
7. **T7 (Epoch Invalidation):** RCU atomic pointer exchange executes dynamic revocation in 0.6 $\mu\text{s}$, irreversibly terminating the compromised session.

*Key Finding*: When multi-step semantic manipulation successfully bypasses application-level intent filters and reaches downstream execution attempts, DROS enforces three distinct non-bypassable binary checkpoints, ensuring that cognitive subversion cannot escalate into unauthorized execution effects.

---

## VI. Related Work

### A. Agent Security and Hijacking

Perez and Ribeiro first formally characterized indirect prompt injection, demonstrating that content in agent-consumed data sources can reliably redirect agent behavior. Greshake et al. extended this to real-world LLM-Integrated Application scenarios. OWASP LLM Top 10 catalogs LLM06 (Excessive Agency) as a primary risk, which DROS L4 directly addresses.

### B. Application Governance Middleware

Recent industry initiatives, notably the **Microsoft Agent Governance Toolkit (AGT)**, introduce application-level policy enforcement via function decorators (`@govern`) and policy engines (e.g., Agent Control Specification, OPA, Cedar). AGT optimizes for ecosystem breadth across heterogeneous agent frameworks (LangChain, AutoGen, Semantic Kernel). However, as acknowledged in official security disclosures, application middleware shares the agent's process memory boundary. DROS complements application middleware by providing an execution-enforcement substrate anchored at the C-ABI boundary.

### C. OS-Level Enforcement and Kernel Security

SELinux and AppArmor provide mandatory access control with strong formal foundations, but operate at process-level granularity insufficient for multi-agent workloads. Seccomp provides syscall filtering but cannot map agent roles to syscall policies within a shared PID. eBPF-based tracing frameworks (AgentSight, Eunomia) provide observability but not enforcement; DROS bridges this gap.

### D. Capability-Based Security and Comparative Taxonomy

DROS's L4 bitmap model builds on the theoretical foundations of capability-based security (Dennis and Van Horn 1966; Levy 1984), which established that minimum-capability access control provides stronger confinement properties than discretionary or mandatory models. Unlike classic operating system capability architectures (such as Capsicum or CHERI) which enforce memory addresses or file descriptors at hardware/OS boundaries, DROS introduces a lightweight, in-band cryptographic binding directly tying application-level agent identities to execution capabilities.

**Table VIII: Comparative Taxonomy of Authorization and Confinement Paradigms**

*Taxonomy Scope Note*: Table VIII classifies the primary enforcement abstraction of each paradigm based on published designs; it does not imply that listed architectures cannot be retrofitted or combined with external orthogonal mechanisms.

| Paradigm / System | Identity Model | Confinement Boundary | Dynamic Context | In-Process Agent Role | FFI / C-ABI Enforcement | Cryptographic Capability Binding |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **POSIX DAC (UID/GID)** | Static OS User | OS Syscall | No | No | No | No |
| **SELinux / Linux LSM** | Process Security Context | Kernel LSM Hooks | Limited | No | No | No |
| **Linux Seccomp-BPF** | Thread / Process Syscall Filter | Syscall Entry | No | No | No | No |
| **Capsicum / CHERI** | Capability Descriptors / Hardware Fat Ptrs | Hardware / Syscall | No | No | No | Yes |
| **OAuth 2.0 / Macaroons** | Bearer Token / HMAC Caveats | HTTP API Gateway | Yes | Yes (Service) | No | Yes |
| **Microsoft AGT (v4.x Host Middleware)** | Decorator / Identity Context | Application Middleware | Yes | Yes | No | Optional |
| **DROS (This Work)** | **3-Tier PKI + Ephemeral DIT** | **C-ABI / FFI Substrate** | **Yes** | **Yes** | **Yes ($O(1)$ Bitmap)** | **Yes (Ed25519 + SHA-256)** |


### E. Zero Trust Architecture

NIST SP 800-207 defines Zero Trust as requiring continuous verification of every subject, asset, and resource request. DROS adopts Zero Trust architectural principles (NIST SP 800-207) at the agent execution level, extending continuous verification from network-layer mTLS down into binary FFI boundary enforcement.

### F. Cryptographically Attributable Audit Evidence

DROS's Ed25519-signed Merkle log provides cryptographically attributable and tamper-evident execution evidence. While the audit architecture supports technical requirements relevant to traceability under applicable AI governance frameworks (EU AI Act 2024), demonstrating full regulatory compliance requires additional legal and operational controls beyond the scope of this paper.

---

## VII. Discussion

### A. Comparison with Alternative Approaches

DROS L4 differs from eBPF syscall attachment in the attribution layer: eBPF rules bind to kernel-visible process/user identities, while DROS L4 binds to cryptographically authenticated agent roles.

API gateways operate at the network/HTTP mediation layer and therefore do not inherently mediate local in-process FFI calls. An agent invoking local tool functions directly via FFI (the common LangChain/AutoGen pattern) completely bypasses network-layer gateways. Conversely, all execution paths that cross the protected DROS boundary are subject to deterministic capability enforcement prior to body dispatch.

We explicitly distinguish three distinct latency measurement points within the DROS architecture:
1. $L_{\text{policy}} = 26.21\ \mu\text{s}$ (P50): Evaluates downstream governance decision latency from DIT reception through L2 DIT cryptographic verification, L3 ABAC resolution, and L4 bitmap check (excluding upstream L1 semantic LLM inference, which introduces $L_{\text{semantic}} \approx 45.2\ \text{ms}$).
2. $L_{\text{isolated}} = 825.0\ \text{ns}$: Measures the isolated, in-memory capability bitmap check critical path at the L4 C-ABI boundary under zero heap allocations.
3. $L_{\text{micro}} = 1.20\ \mu\text{s}$ (P99): Quantifies GuardVM boundary interception under high-rate microbenchmarks.

### B. Relationship to Lower-Layer Syscall Enforcement (DROS-PGM)

While this paper focuses exclusively on bridging the Agent-to-Execution Attribution Gap at the **C-ABI/FFI boundary** for autonomous AI workloads, complementary research explores deterministic enforcement at the operating system **syscall boundary** (DROS-PGM [Chen, Zenodo 2026]). In that orthogonal domain, enforcement targets host-level binary malware (ransomware, unauthorized privilege escalation) independent of LLM agent roles. Together, they illustrate a shared architectural philosophy: that deterministic execution-boundary enforcement is essential whether the boundary resides at the FFI gate of an AI interpreter or at the OS kernel interface.

### C. Deployment Considerations

DROS requires no modification to model weights or tool business logic; deployment requires routing governed tool invocations through the registered DROS C-ABI boundary wrapper. The GuardVM deploys as a co-located sidecar container. Policy updates declared in `vajra.md` are hot-reloaded without process restart: utilizing RCU (Read-Copy-Update) atomic pointer swapping, policy updates propagate into active worker threads in sub-microsecond latency ($T_{\text{prop}} = t_{\text{observe}} - t_{\text{publish}} < 1.0\ \mu\text{s}$) with zero service downtime.

### D. Limitations and Threat Model Boundaries

1. **Threat Model Boundary**: This study evaluates a compromised application-level agent in Python runtime environments. It assumes capabilities to invoke undeclared functions and perform in-process variable reflection. It explicitly excludes arbitrary native code execution, kernel privilege escalation, hypervisor compromise, or physical host access.
2. **Tool Universe Completeness**: L4 enforcement requires all tool invocations to pass through the registered FFI boundary. Dynamically loaded tools require explicit registration.
3. **BEC Key Custody**: L2 security depends on secure key custody. HSM integration is recommended for production.
4. **Evaluation Scope and Complete Mediation Boundary**: DROS does not claim to provide complete mediation over arbitrary native code execution unless the host deployment environment additionally constrains unmanaged execution paths (e.g., via OS-level seccomp filters or restricted container profiles that prevent direct `libc` or `execve` bypass). The guarantees established herein apply strictly to execution paths routed through the governed substrate interfaces.

---

## VIII. Conclusion

We have presented DROS, a four-layer defense-in-depth architecture addressing the Agent-to-Execution Attribution Gap. The core contribution is L4: a deterministic C-ABI enforcement layer executing O(1) capability bitmap comparisons at the FFI boundary.

Our cumulative layer addition study demonstrates L4 is not redundant with L1-L3: without L4, the upper layers left 52,180 obfuscated IPI attempts uncontained in the evaluated corpus; L4 blocked all of these attempts at the governed C-ABI boundary. With full DROS enforcement, complete containment (0 escapes) was empirically observed across all 137,751 evaluated adversarial attempts under the stated threat model, with a downstream median latency of 26.21 $\mu\text{s}$ and an observed false positive rate of 0/22,860 on benign workloads.

The central thesis -- that an agent's authorization state can be deterministically enforced at the execution boundary even after semantic compromise -- is validated by the ablation evidence. Execution-boundary enforcement represents an essential architectural primitive for robust enterprise AI agent deployment, complementary to but not replaceable by semantic-layer defenses.

Future work: (1) formal verification of CEI under concurrent multi-agent workloads; (2) extension of DIT federation to W3C DID-based cross-organizational identity standards; (3) automated policy synthesis from natural language governance specifications. The complementary kernel-level enforcement problem for traditional PC threats (ransomware, phishing, privilege escalation) is addressed in the companion DROS-PGM paper [DOI: 10.5281/zenodo.21494849].

---

## Acknowledgments and AI Collaboration Disclosure

Generative AI tools (including Antigravity and Google Gemini Pro) were employed as interactive research, software engineering, and writing assistants throughout this project. Specifically, AI tools assisted in exploring established AI security mechanisms, prototyping multi-agent C-ABI boundary enforcement logic, generating and debugging evaluation scripts, structuring technical documentation, and refining manuscript syntax.

The core research vision, problem formulation, four-layer security architecture design, threat model assumptions, capability bitmap formalization, experimental benchmark methodology, result interpretation, patent claims, and final manuscript verification were independently directed, validated, and approved by the human author, who assumes sole intellectual and legal responsibility for the submitted work.

**Patent Notice:** The core technology and architectures described in this paper are protected under U.S. Provisional Patent Application No. 64/111,973 (Patent Pending).


## References

### Verified References (完整引用資訊)

**[1] Zero Trust Architecture**
NIST Special Publication 800-207, "Zero Trust Architecture," National Institute of Standards and Technology, Aug. 2020.

**[2] OWASP LLM Top 10**
OWASP Foundation, "OWASP Top 10 for Large Language Model Applications, Version 1.1," 2023. [Online]. Available: https://owasp.org/www-project-top-10-for-large-language-model-applications/

**[3] OWASP Top 10 for Agentic Applications (2026 Edition)**
OWASP Foundation, "OWASP Top 10 for Agentic Applications (2026 Edition)," Dec. 2025. [Online]. Available: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-2026/

**[4] MITRE ATLAS**
MITRE Corporation, "MITRE ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems, Version 4.5," 2024. [Online]. Available: https://atlas.mitre.org/

**[5] AgentSight**
Y. Zheng, Y. Hu, T. Yu, and A. Quinn, "AgentSight: System-Level Observability for AI Agents Using eBPF," arXiv preprint arXiv:2508.02736, Aug. 2025.
[University of California Santa Cruz & ShanghaiTech University; eunomia-bpf Community]

**[6] Eunomia-bpf / eBPF Security**
Y. Zheng et al., "AgentOps: Enabling Observability of LLM Agents," arXiv preprint arXiv:2411.05285, Nov. 2024.
[Note: Eunomia-bpf community project; cite companion paper for eBPF security monitoring]

**[7] Indirect Prompt Injection (IPI) -- Original Formulation**
F. Perez and I. Ribeiro, "Ignore Previous Prompt: Attack Techniques For Language Models," in Proc. NeurIPS 2022 Workshop on Machine Learning Safety, New Orleans, LA, USA, Dec. 2022.

**[8] Indirect Prompt Injection -- Real-World LLM Apps**
K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injections," arXiv preprint arXiv:2302.12173, Feb. 2023.
[Presented at ACM AISec Workshop 2023]

**[9] SELinux**
P. Loscocco and S. Smalley, "Integrating Flexible Support for Security Policies into the Linux Operating System," in Proc. USENIX Annual Technical Conference (ATC), 2001, pp. 29--42.

**[10] SE Android and LSM Architecture**
S. Smalley and R. Craig, "Security Enhanced (SE) Android: Bringing Flexible MAC to Android," in Proc. Network and Distributed System Security Symposium (NDSS), San Diego, CA, USA, Feb. 2013.

**[11] Linux Seccomp**
"seccomp(2) -- Linux Programmer's Manual," Linux Kernel Documentation, Version 6.9, 2024. [Online]. Available: https://man7.org/linux/man-pages/man2/seccomp.2.html

**[12] Capability-Based Security -- Foundations**
J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," Communications of the ACM, vol. 9, no. 3, pp. 143--155, Mar. 1966. DOI: 10.1145/365230.365252

**[13] Capability-Based Computer Systems**
H. M. Levy, Capability-Based Computer Systems. Bedford, MA: Digital Press, 1984.

**[14] NIST ABAC**
V. Hu, D. Ferraiolo, R. Kuhn, A. Schnitzer, K. Sandlin, R. Miller, and K. Scarfone, NIST Special Publication 800-162, "Guide to Attribute Based Access Control (ABAC) Definition and Considerations," NIST, Jan. 2014. DOI: 10.6028/NIST.SP.800-162

**[15] W3C DIDs**
M. Sporny, D. Longley, M. Sabadello, D. Reed, O. Steele, and C. Allen, "Decentralized Identifiers (DIDs) v1.0," W3C Recommendation, World Wide Web Consortium, Jul. 2022. [Online]. Available: https://www.w3.org/TR/did-core/

**[16] Merkle Hash Chains**
R. C. Merkle, "A Digital Signature Based on a Conventional Encryption Function," in Advances in Cryptology -- CRYPTO 1987, Lecture Notes in Computer Science, vol. 293, C. Pomerance, Ed. Berlin: Springer, 1988, pp. 369--378. DOI: 10.1007/3-540-48184-2_32

**[17] NeMo Guardrails**
T. Rebedea, R. Dinu, M. Shivagunde, C. Haardt, and N. Bhatt, "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails," arXiv preprint arXiv:2310.10501, EMNLP 2023 System Demonstrations, Singapore, Dec. 2023.

**[18] LlamaGuard**
H. Inan, K. Upasani, J. Chi, R. Rungta, K. Iyer, Y. Mao, M. Tontchev, Q. Hu, B. Fuller, D. Testuggine, and M. Khabsa, "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations," arXiv preprint arXiv:2312.06674, Dec. 2023.

**[19] PromptBench**
K. Zhu, J. Wang, J. Zhou, Z. Wang, H. Chen, Y. Wang, L. Yang, W. Ye, Y. Zhang, N. Gong, and X. Xie, "PromptBench: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts," arXiv preprint arXiv:2306.04528, Jun. 2023. Published in IEEE TKDE 2024.

**[20] EU AI Act**
European Parliament and Council of the European Union, "Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 Laying Down Harmonised Rules on Artificial Intelligence (Artificial Intelligence Act)," Official Journal of the European Union, L 2024/1689, Jul. 2024.

**[21] DROS Prior Art (Zenodo)**
C. C. Chen, "Runtime Attribution Framework: An External C-ABI and PKI-Based Zero-Trust Infrastructure for Non-Repudiable Execution Governance in Multi-Agent Systems," Zenodo, DOI: 10.5281/zenodo.20823163, 2026.

**[22] InjecAgent -- IPI Benchmark (ACL 2024)**
Q. Zhan, Z. Liang, Z. Ying, and D. Kang, "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents," in Findings of the Association for Computational Linguistics: ACL 2024, Bangkok, Thailand, Aug. 2024, pp. 3088--3101.

**[23] LLM Agent Security Survey (ACM CSUR 2025)**
F. He, T. Zhu, D. Ye, B. Liu, W. Zhou, and P. S. Yu, "The Emerged Security and Privacy of LLM Agent: A Survey with Case Studies," ACM Computing Surveys, vol. 58, no. 6, Article 162, Dec. 2025. arXiv preprint arXiv:2407.19354.

**[24] Macaroons: Cookies with Contextual Caveats**
A. Birgisson, J. G. Polakis, Ú. Erlingsson, R. Kumar, and M. Stiegler, "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud," in Proc. Network and Distributed System Security Symposium (NDSS), San Diego, CA, Feb. 2014.

**[25] Role-Based Access Control Models**
R. S. Sandhu, E. J. Coyne, H. L. Feinstein, and C. E. Youman, "Role-Based Access Control Models," IEEE Computer, vol. 29, no. 2, pp. 38--47, Feb. 1996. DOI: 10.1109/2.485845.
