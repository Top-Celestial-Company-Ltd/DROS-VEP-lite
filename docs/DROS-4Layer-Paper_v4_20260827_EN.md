# 🛡️ DROS: A Four-Layer Runtime Substrate with Deterministic Execution Enforcement for Agent-to-Execution Attribution Governance (v4.0)

## Progressive Adversarial Validation, Meta-Verification, and Open Falsification (Implementation & Empirical Evaluation)

**Document Version:** 4.0 Research Paper / Peer-Reviewed Manuscript  
**Date:** August 27, 2026  
**Author:** Chun-Cheng (Jimmy) Chen (`jimmychen@dr-os.io`)  
**Affiliation:** Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.  
**Patent Notice:** DROS execution governance and security technology is protected under U.S. Provisional Patent Application (U.S. PPA No. 64/111,973, Patent Pending).  
**Open-Source Verification Artifacts & Reproducibility:** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**Permanent Academic Citation (DOI):** [Zenodo Record DOI: 10.5281/zenodo.21755653](https://doi.org/10.5281/zenodo.21755653)

---

## Abstract

Autonomous AI agents increasingly operate with legitimate credentials, delegated capabilities, and access to consequential tools, creating an attribution gap between high-level agent intent and low-level physical execution. We present DROS, a four-layer runtime substrate that separates agent identity from execution authority and enforces capability constraints at a binary C-ABI boundary. Rather than treating security as a priori established, we formulate DROS as an experimentally falsifiable execution-governance boundary and introduce a progressive adversarial validation methodology combining autonomous attack search, negative controls, mutation testing, independent ground-truth oracles, concurrency stress, and open reproducibility. The evaluation decomposes the causal chain into intent, authorization, execution, and physical effect, allowing enforcement decisions to be independently cross-validated against kernel and external state observations. Across the instantiated evaluation corpus, including adaptive attack attempts, multi-agent delegation chains, revocation races, mutation tests, and oracle probes, we observe no unauthorized physical effects within the explicitly instrumented observation boundary. We report the resulting guarantees as empirical invariants over the evaluated state space rather than universal security proofs, and release the evaluation harness and counterexample protocol to enable continued adversarial falsification.

**Keywords:** AI Agent Security, Runtime Execution Substrate, Controlled C-ABI Authorization Boundary, Autonomous Adversarial Evaluation, RCU State Transition, Information Flow Control (IFC), Attribution Governance.

---

## 1. Introduction & The Semantic-Kernel Paradox

Autonomous AI Agents operate with valid credentials, OAuth session tokens, and database connections. In authenticated application-layer abuse scenarios, traditional perimeter controls alone are insufficient because malicious actions originate from authenticated internal principals.

### 1.1 The Semantic-Kernel Paradox
Modern systems literature identifies a fundamental split in AI defense:
1. **Semantic Application Middleware (High Semantics, Zero Determinism):** Prompt firewalls, JSON schema validators, and application middlewares inspect natural language and declared schemas. However, they lack execution-boundary containment; interpreter escapes, undeclared tool invocations, and semantic obfuscation consistently bypass these layers.
2. **Kernel Sandboxes (High Determinism, Zero Semantics):** Low-level primitives (e.g., Seccomp, Linux Namespaces, eBPF) enforce binary syscall filtering but cannot distinguish whether a database write originated from an authorized Finance Agent or a hijacked Support Agent operating in the same worker process.

### 1.2 DROS 4-Layer Substrate Placement & Core Design Thesis
DROS resides between application frameworks and the host operating system, establishing four deep enforcement layers where **L1 may fail, but L2–L4 deterministically enforce**:

```text
Application Frameworks (OpenAI Agents, LangGraph, CrewAI, AutoGen)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ L1: Detective Intelligence (Detect - Semantic Filtering)    │
├─────────────────────────────────────────────────────────────┤
│ L2: Identity & Zero Trust  (Attribute - 3-Tier PKI + DIT)   │
├─────────────────────────────────────────────────────────────┤
│ L3: Dynamic IFC Governance (Constrain Data - Taint/Masking) │
├─────────────────────────────────────────────────────────────┤
│ ★ L4: Execution Enforcement (Enforce - Sub-μs Denial Path)  │
└────────────────────────────┬────────────────────────────────┘
                             │ (Controlled Binary C-ABI / FFI Boundary)
                             ▼
Host Operating System & Physical Endpoints (OS Syscall, DB, File I/O)
```

### 1.3 Core Contribution Thesis & Research Questions
> **DROS does not assert that "absolute security is proven a priori"; rather, it establishes an experimentally falsifiable execution-governance boundary evaluated through progressively adversarial, independently observed, and openly falsifiable experiments.**

To systematically validate this thesis, this paper investigates four primary research questions:
* **RQ1 (Enforcement Effectiveness)**: Under post-compromise application conditions ($C_A = 1$), can the governed execution path deterministically prevent unauthorized operations from causing physical state transitions?
* **RQ2 (Revocation Atomicity)**: Under concurrent execution and policy revocation races, does there exist any stale authorization window allowing replayed executions?
* **RQ3 (Evaluator Sensitivity)**: Can the evaluation framework and test harness effectively detect deliberately injected security flaws and mutation regressions?
* **RQ4 (Oracle Independence)**: Can authorization decisions be objectively and independently verified by decoupled execution-side and physical-side observers?

---

## 2. Threat Model, Evaluation Space, and Epistemic Boundaries

### 2.1 Post-Compromise Threat Model ($C_A = 1$)
Our evaluation establishes a rigorous **Post-Compromise** threat model:
* **Assumption 1 (Full Application/Agent Compromise $C_A = 1$)**: The adversary has achieved prompt injection, extracted system prompts, and holds arbitrary interpreter/code execution capabilities within the application container.
* **Assumption 2 (Valid Credential Possession)**: The adversary possesses legitimate OAuth tokens, internal API keys, and authenticated session identities.
* **Assumption 3 (Multi-Agent Collusion & Delegation)**: The adversary controls multiple heterogeneous agents attempting privilege escalation via delegation chains and confused-deputy patterns.
* **Root of Trust**: The controlled binary C-ABI execution gate and underlying OS memory isolation.

### 2.2 Comparative Baselines & Attack Preservation ($A_{B0} = A_{B1}$)
To eliminate evaluation bias from payload variance, comparative experiments strictly adhere to the **Attack Preservation Principle ($A_{B0} = A_{B1}$ and $\text{Env}_{B0} \approx \text{Env}_{B1}$)**:

| Baseline ID | Topology Structure | Primary Purpose |
| :--- | :--- | :--- |
| **B0 (Bare Application)** | `Attacker -> Application -> OS` | Establishes unmanaged baseline; verifies exploit payloads cause real damage ($\Delta S_{B0} > 0$). |
| **B1 (DROS Enabled)** | `Attacker -> Application -> DROS/PGM -> OS` | Primary subject under test; verifies execution containment ($\Delta S_{B1} \equiv 0$). |
| **B2 (Defense-in-Depth)** | `Attacker -> App -> DROS + Stack -> OS` | Verifies compatibility and coverage with existing EDR/XDR/WAF infrastructure. |
| **B3 (Pure Binary C-ABI)** | `Attacker -> Standalone PGM C-ABI -> OS` | Evaluates C-ABI execution gate in complete isolation without application assistance. |

### 2.3 Formal Physical Effect & Invariants

#### Formal Definition of Physical Effect ($I_{\text{physical}}$)
To eliminate semantic ambiguity, physical effect $I_{\text{physical}}(x)$ is strictly defined over the explicitly instrumented observation set $\mathcal{S}_{\text{obs}}$:

$$I_{\text{physical}}(x) = \begin{cases} 1, & \exists s \in \mathcal{S}_{\text{obs}}: \Delta(s) > 0 \\ 0, & \forall s \in \mathcal{S}_{\text{obs}}: \Delta(s) = 0 \end{cases}$$

$$\mathcal{S}_{\text{obs}} = \{ \text{Kernel Syscall}, \text{Filesystem Diff}, \text{Database WAL}, \text{Process Tree}, \text{Outbound Network}, \text{IPC State} \}$$

#### Terminology Consistency
* **Counterexample Search**: Refers to the proactive adversarial exploration process aimed at discovering any executable violating state ($C_A \land \neg C_E \implies I_{\text{physical}} > 0$) across the instantiated state space.
* **Counterexample Submission**: Refers to the public verification protocol and intake mechanism enabling external researchers to submit reproducible counterexample traces to the community registry.

#### Formal Security Invariants

$$\boxed{C_A \centernot\implies C_E \quad (\text{Non-Inheritance of Authority})}$$
$$\boxed{C_E(t_0) \centernot\implies C_E(t_1) \quad (\forall t_0 \neq t_1, \text{Temporal Isolation})}$$
$$\boxed{\bigcup_{i=1}^n C_{A_i} \centernot\implies C_E^{\text{unauth}} \quad (\text{Capability Composition Safety})}$$
$$\boxed{\forall x \in X_{\text{evaluated}}, \quad C_A(x) \land \neg C_E(x) \implies \neg \text{Exec}_{\text{unauthorized}}(x) \implies I_{\text{physical}}(x) = 0}$$
$$\boxed{S_{\text{after}} \equiv S_{\text{before}} \quad (\text{Zero State Drift within } \mathcal{S}_{\text{obs}})}$$

---

## 3. DROS 4-Layer Substrate Implementation

### 3.1 L1: Detective Intelligence (Detect)
L1 applies heuristic pattern matching and lightweight semantic filters. In DROS, **L1 is explicitly treated as probabilistic**. When L1 fails due to novel jailbreaks or encoding bypasses, threat containment falls deterministically onto L2–L4.

### 3.2 L2: Identity & Dynamic Intent Tokens (Attribute)
L2 establishes a cryptographic 3-Tier PKI attribution model (Enterprise CA $\rightarrow$ Task Issuer $\rightarrow$ Ephemeral Worker Agent) and issues Dynamic Intent Tokens (DIT). The DIT cryptographically binds the designated tool name, argument hash, timestamp, and capability bitmask using Ed25519 signatures.

### 3.3 L3: Dynamic IFC & In-Band Redaction (Constrain Data)
L3 implements in-memory taint tracking and in-band secret masking. When confidential assets (e.g., proprietary formulas, API keys, private keys) pass through the agent context, L3 redacts them in-band (substituting `[REDACTED_BY_DROS_POLICY_GATE]`), mitigating prompt side-channel exfiltration.

### 3.4 L4: Binary C-ABI Authorization Execution Gate (Enforce Execution)
L4 serves as the controlled binary authorization boundary, implemented in memory-safe Rust and exposed via a pure C-ABI dynamic library.
1. **$O(1)$ Constant-Time Policy Lookup**: Bitmask evaluation executes in sub-microsecond bounds.
2. **Atomic Policy-State Transition ($T_{\text{swap}} = 420\text{ ns}$)**: Capability pointers are swapped atomically via `AtomicPtr`. The measured $T_{\text{swap}} = 420\text{ ns}$ defines the state-pointer swap mechanism latency, ensuring subsequent governed calls cannot access stale authorization entries.
3. **Sub-Microsecond Fail-Closed Denial Path (<500 ns)**: Any bitmask mismatch or unauthorized capability triggers an immediate fail-closed denial branch, preventing execution from reaching the governed operating system path.

---

## 4. Progressive Adversarial Validation Framework

Rather than presenting static checklists, we construct a 7-tier progressive falsification hierarchy:

```text
Level 1: Baseline Calibration ── Establish functional correctness & B0 breach (ΔS_B0 > 0)
   ↓
Level 2: Autonomous Adversarial Search ── Strix white-box adaptive search (max I_physical)
   ↓
Level 3: Dynamic Stress & Chaos ── 100-agent emulated mesh, RCU race conditions, fault injection
   ↓
Level 4: Meta-Verification ── Negative controls (sabotaged binaries) & 100 mutants
   ↓
Level 5: Oracle Independence ── 4-Stage ground-truth pipeline (Intent → Auth → Exec → Effect)
   ↓
Level 6: Configuration Validation ── Policy portability across x86_64, aarch64, glibc, musl, MSVC
   ↓
Level 7: Open Falsification ── Public reproducibility kit & immutable counterexample registry
```

### 4.1 Adversarial Coverage vs. Results Matrix

| Attack Dimension | Evaluated Variants & Scenarios | Observed Defense / Mechanism | Counterexamples |
| :--- | :--- | :--- | :--- |
| **Identity** | Valid credentials / Forged identity / Role substitution | Ed25519 signature verification fails; L2 rejects token | **0** |
| **Capability** | Missing permissions / Excessive privilege / Combined | L4 bitmask mismatch immediately triggers fail-closed | **0** |
| **Parameter** | Valid payload / Parameter mutation / Replay injection | SHA-256 parameter hash mismatch; execution denied | **0** |
| **Temporal** | Active window / Expired token / RCU instant revocation | Atomic pointer swap renders expired tokens instantly invalid | **0** |
| **Delegation** | Direct invocation / Multi-hop chains / Confused deputy | DIT strictly bound to Task Issuer; cross-role elevation blocked | **0** |
| **Interpreter** | Shell injection (`bash`) / Dynamic evaluation (`eval`) | Escaped calls lack valid DIT; intercepted at C-ABI gate | **0** |
| **Concurrency** | Serial execution / High surges / Sub-microsecond races | Lock-free RCU provides concurrency isolation; 0 race window | **0** |
| **Encoding** | Canonical JSON / Obfuscated payload / Metamorphic | Canonical bitmask matching immune to semantic obfuscation | **0** |
| **Topology** | 1-Agent standalone / 100-Agent emulated mesh / Chained | Multi-agent delegations verified independently; 0 inheritance | **0** |
| **Failure & Fault** | Connection timeout / Process crash / Stale state read | Two-phase atomic commit ensures 0 lingering side-effects | **0** |

### 4.2 Multi-Layer Adversarial Evaluation Results

| Validation Tier | Methodology & Configuration | Adversarial Workload | Observed Defense / Evidence | Counterexamples | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1 Baseline** | B0/B1 A/B removal comparison | 50 unmanaged exploits | B0 breached ($\Delta S_{B0} > 0$); B1 contained ($\Delta S_{B1} \equiv 0$) | **0** | **PASS (RQ1)** |
| **L2 Autonomous** | Strix white-box adaptive search | 2,410 attempts (21.4M Tokens) | 100% of probes reaching gateway rejected under evaluated corpus | **0** | **PASS (RQ1)** |
| **L3 Dynamic Stress** | 100-agent emulated mesh + RCU race | 400 delegation chains + 250 bursts | RCU 420 ns pointer transition; 0 replayed executions | **0** | **PASS (RQ2)** |
| **L4 Meta-Verification** | Negative controls + 100 mutants | 5 injected flaws + 100 mutants | 5/5 flaws caught; 100% mutation score over the 100 instantiated mutants | **0** | **PASS (RQ3)** |
| **L5 Oracle Falsification**| 9 Oracle torture vectors | 450 mutation probes | $G = 0$ ghost syscalls within $\mathcal{S}_{\text{obs}}$; 0 audit-state drift | **0** | **PASS (RQ4)** |
| **L6 Config Validation** | Cross-OS/arch configuration check | 7,500 automated probes | Validated policy semantics portability across x86_64, ARM64, and Windows | **0** | **PASS** |

### 4.3 Meta-Verification: Negative Controls and Mutation Score (RQ3)
To address the research question (**RQ3: Can the evaluation framework detect known security regressions?**), we constructed 5 sabotaged binaries with deliberately injected flaws and evaluated 100 instantiated mutants across 8 mutation classes (M1: bit widening, M2: identity substitution, M3: expiry bypass, M4: hash omission, M5: stale reads, M6: check removal, M7: fail-open branch, M8: audit suppression):

$$\text{Mutation Score} = \frac{\text{Killed Mutants}}{\text{Total Instantiated Mutants}} = \frac{100}{100} = \mathbf{1.0\ (100\%\ \text{mutation-killing rate over the instantiated mutation corpus})}$$

The test harness successfully detected 5/5 sabotaged flaws and killed 100/100 mutants, confirming that the harness is not a permissive rubber stamp.

---

## 5. Decoupled Multi-Observer Oracle & Empirical Results

### 5.1 The Four-Stage Independent Ground-Truth Pipeline (RQ4)
To enforce the principle that **"No Single Component May Act As Its Own Sole Witness,"** DROS-VEP establishes a 4-stage decoupled pipeline ($O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$):

$$\boxed{\text{Intent } (O_I) \longrightarrow \text{Authorization } (O_A) \longrightarrow \text{Execution } (O_E) \longrightarrow \text{Physical Effect } (O_P)}$$

1. **Intent Oracle ($O_I$)**: Records raw tool invocation payloads directly from the caller.
2. **Authorization Oracle ($O_A$)**: PGM C-ABI gate evaluates bitmasks and logs enforcement decisions (DENY).
3. **Execution Oracle ($O_E$)**: Decoupled kernel monitor confirms **$G = 0$ ghost syscalls** escape within instrumented scope.
4. **Physical Effect Oracle ($O_P$)**: Out-of-band DB WAL, filesystem, and process-tree hash diffs verify $\boxed{S_{\text{after}} \equiv S_{\text{before}}}$ over $\mathcal{S}_{\text{obs}}$.

### 5.2 Physical Side-Effect Containment Analysis ($\Delta I_{\text{physical}}$ - RQ1)

$$\Delta I_{\text{physical}} = I_{\text{physical}}(B0) - I_{\text{physical}}(B1) = 1.0 - 0.0 = \mathbf{100\%\ \text{observed physical-effect suppression over the evaluated attack corpus}}$$

### 5.3 Performance & Latency Overhead
Evaluated on bare-metal AMD Ryzen 9 7950X / Ubuntu 24.04:
* **End-to-End Decision Latency (P50)**: $26.1\ \mu\text{s}$ (HTTP parse, DIT Ed25519 verify, bitmask check).
* **End-to-End Decision Latency (P99)**: $31.4\ \mu\text{s}$.
* **RCU State-Pointer Swap Latency ($T_{\text{swap}})**: $420\text{ ns}$ (memory barrier & atomic swap, isolated from network I/O).
* **L4 Fail-Closed Denial Path Latency**: $<500\text{ ns}$.

---

## 6. Open Falsification Protocol & Limitations

### 6.1 Limitations & Epistemic Scope (Gap in Scope)
1. **Ontological Dependency**: DROS enforcement relies on accurate capability bitmask mapping in L2 DITs. Granting administrative bits to untrusted roles constitutes policy misconfiguration rather than substrate escape.
2. **Observation Boundary**: The zero-counterexample finding is strictly bounded to the experimentally instantiated space of 60,000+ probes, 100-agent emulated meshes, and chaos mutations, and does not constitute a priori proof across infinite attack universes.
3. **Configuration Portability vs. Native Kernel Boundary (Gap in Scope)**: L6 evaluates policy configuration portability across platforms; native kernel-level enforcement remains subject to host OS MMU and kernel driver guarantees.

### 6.2 Public Counterexample Registry
We publish the complete replication package on GitHub and establish an immutable counterexample registry (`reproducibility/counterexamples/`). External researchers observing an unauthorized state transition ($I_{\text{physical}} > 0$) are invited to submit reproducible artifacts:

```text
Public Counterexample Submission Schema:
├── CE-ID (e.g., CE-001)
├── Target Environment & Compiler Flags
├── Seed / Reproduction Script
├── Observed State Diff (ΔS > 0)
└── Physical Effect Artifact
```

---

## 7. Conclusion & Declarations

This paper presented and experimentally evaluated the **DROS 4-Layer Runtime Substrate with Deterministic Execution Enforcement**. By sinking execution boundaries to a controlled binary C-ABI / FFI authorization layer, DROS bridges the semantic-kernel paradox in agentic workflows.

Through progressive adversarial validation incorporating autonomous red teaming, negative controls, mutation testing, and decoupled oracles, DROS demonstrated zero observable counterexamples across the instantiated evaluation space:

$$\boxed{\text{Final Epistemic Verdict: } \forall x \in X_{\text{evaluated}}, \quad C_A(x) \land \neg C_E(x) \implies I_{\text{physical}}(x) = 0 \quad (\text{PASS})}$$

---

## References

1. **J. Chen**, *"DROS: A Four-Layer Deterministic Runtime Operation System Bridging the Agent-to-Execution Attribution Gap in Autonomous AI Workloads,"* Zenodo Technical Report, DOI: `10.5281/zenodo.22092008`, 2026.
2. **J. Chen**, *"DROS Trilogy Reading Guide: An Agent Runtime Operation Substrate (Academic Version 3.0),"* Zenodo Technical Guide, DOI: `10.5281/zenodo.22114036`, 2026.
3. **J. Chen**, *"DROS-PGM: Physical Guard Module with Sub-Microsecond C-ABI Binary Execution Boundary,"* Zenodo Research Report, DOI: `10.5281/zenodo.21903687`, 2026.
4. **J. Chen**, *"DROS 6P Architectural Specification: Unified Trust, PKI, and Execution Governance,"* Zenodo Specification, DOI: `10.5281/zenodo.21833970`, 2026.
5. **Strix Security Team**, *"Strix: Autonomous Multi-Agent AI Penetration Testing Framework (v1.5.3),"* 2026. [Online]. Available: `https://strix.ai`
6. **Microsoft**, *"Microsoft Agent Framework Documentation: Tool Calling and Execution Governance,"* Microsoft Learn, 2025.
7. **NVIDIA**, *"NeMo Guardrails: Programmable Guardrails for LLM Applications,"* NVIDIA Developer Documentation, 2024.
8. **European Parliament**, *"Artificial Intelligence Act (Regulation EU 2024/1689), Article 50: Transparency and Traceability of AI Systems,"* Official Journal of the European Union, 2024.
9. **MITRE Corporation**, *"ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems,"* MITRE ATLAS Knowledge Base, 2026.
10. **OWASP Foundation**, *"OWASP Top 10 for Large Language Model Applications,"* OWASP Standard, 2025.
11. **P. E. McKenney**, *"Is Parallel Programming Hard, And, If So, What Can You Do About It? (Read-Copy Update Architecture),"* Linux Technology Center, IBM Operating Systems Review, 2024.
12. **W. Enck et al.**, *"TaintDroid: An Information-Flow Tracking System for Real-Time Privacy Monitoring on Smartphones,"* ACM Transactions on Computer Systems (TOCS), vol. 32, no. 2, pp. 1–32, 2014.
13. **METR (Model Evaluation and Threat Research)**, *"Evaluating Autonomous Capabilities in Frontier AI Models,"* METR Technical Research Standard, 2025.
14. **USENIX Security Symposium**, *"Artifact Evaluation Guidelines and Criteria,"* USENIX Association, 2024.
15. **IEEE S&P Editorial Board**, *"IEEE Symposium on Security and Privacy: Call for Papers and Submission Guidelines,"* IEEE Computer Society, 2026.
