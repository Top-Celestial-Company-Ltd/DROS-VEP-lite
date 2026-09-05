# DROS: A Four-Layer Runtime Substrate with Deterministic Execution Enforcement for Agent-to-Execution Attribution Governance

**Target Journal / Publication:** IEEE Security & Privacy Magazine (Regular Article, Manuscript SP-2026-08-0414)  
**Author:** Chun-Cheng (Jimmy) Chen (`jimmychen@dr-os.io`)  
**Affiliation:** Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.  
**ORCID:** 0009-0001-6387-0500  
**Patent Notice:** Protected under U.S. Provisional Patent Application No. 64/111,973 (Patent Pending).  
**Permanent Academic Citation:** [Zenodo Record DOI: 10.5281/zenodo.21755653](https://doi.org/10.5281/zenodo.21755653)  
**Open Verification Harness:** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  

---

## Abstract
DROS is a four-layer runtime substrate that cryptographically binds agent identity and declared execution authority to a governed binary execution path. Under a post-compromise threat model, adversarial search, mutation testing, independent oracles, and 24-hour soak testing observed zero unauthorized physical effects within the evaluated observation boundary.

**Index Terms—** AI Agent Security, Runtime Execution Substrate, Controlled C-ABI Authorization Boundary, Autonomous Adversarial Evaluation, RCU State Transition, Information Flow Control (IFC), Attribution Governance.

---

## 1. Introduction & The Semantic-Kernel Paradox

Autonomous AI agents powered by Large Language Models (LLMs) are transitioning from conversational assistants to operational systems with direct tool invocation authority. In modern enterprise workflows, agents plan multi-step workflows, query backend relational databases, modify source code repositories, and make financial or infrastructure commitments.

This operational autonomy introduces a critical, unresolved security challenge: the fundamental decoupling of semantic intent from physical execution authority. Autonomous agents operate with legitimate credentials, delegated OAuth tokens, and authenticated session identities while reasoning over untrusted, potentially hostile external context. When an adversary poisons this context via Indirect Prompt Injection (IPI), goal hijacking, or multi-turn conversational induction, traditional perimeter controls fail because malicious actions originate from within an authenticated internal security principal.

### 1.1 The Semantic-Kernel Paradox
Modern security architectures exhibit a structural dichotomy when governing autonomous AI workloads, which we define as the **Semantic-Kernel Paradox**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE SEMANTIC-KERNEL PARADOX                            │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 1. Application Semantic Middleware   │ 2. Operating System Kernel Sandboxes │
│    (High Semantics, Zero Determinism)│    (High Determinism, Zero Semantics)│
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Prompt Firewalls & JSON Validators │ • Linux Seccomp, Namespaces, eBPF    │
│ • Rich natural language understanding│ • Binary deterministic syscall filter│
│ • Fundamentally probabilistic        │ • Context-blind to agent identity    │
│ • Bypassed via obfuscation/injection │ • Cannot attribute shared PID writes │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

1. **Application-Layer Semantic Defenses (High Semantics, Zero Determinism):** Systems such as LLM-based guardrails, prompt sanitizers, and input/output classifiers operate in the semantic domain. They analyze natural language for jailbreaks and injection templates. However, semantic filtering is fundamentally probabilistic: adversarial prompt mutations, multi-turn context poisoning, and obfuscated indirect prompt injection can bypass semantic checks with non-zero probability.
2. **OS-Level Sandbox Defenses (High Determinism, Zero Semantics):** Low-level primitives such as Linux Seccomp-BPF profiles, Namespaces, Landlock, and eBPF tracing operate in the physical domain. They enforce binary allow/deny rules on system calls and resource access. However, OS sandboxes are *context-blind*: from the kernel's perspective, all agent actions originate from the same host process (e.g., the Python runtime PID), making it impossible to attribute a specific syscall to an individual agent role or evaluate whether the invocation is authorized within the business context.

We define this structural vulnerability as the **Agent-to-Execution Attribution Gap**: the structural inability of modern architectures to cryptographically bind an agent's semantic identity and authorization context to its deterministic binary execution path.

### 1.2 DROS Substrate Placement & Governed Execution Domain
DROS (Deterministic Runtime Operation System) resides between application frameworks and the host operating system, establishing a co-located authorization plane that works in tandem with host isolation primitives:

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
│ ★ L4: Execution Authorization Gate (Sub-μs Bitmask C-ABI)   │
└────────────────────────────┬────────────────────────────────┘
                             │ (Governed Binary Execution Path)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Host OS Isolation Boundary (Seccomp-BPF / Linux Namespaces) │
└────────────────────────────┬────────────────────────────────┘
                             ▼
Host Operating System Kernel & Physical Endpoints (DB, File I/O)
```

The core design thesis of DROS is that **security must be treated as an experimentally falsifiable property within a strictly governed execution domain, rather than an a-priori claim across unmanaged native code paths**. All security guarantees reported herein represent empirical invariants rigorously verified over the instrumented observation space.

### 1.3 Primary Research Questions
To systematically investigate this thesis, this paper evaluates four core research questions:
* **RQ1 (Enforcement Effectiveness):** Under post-compromise application conditions ($C_A = 1$), can the governed execution path deterministically prevent unauthorized operations from causing physical state transitions within the governed domain?
* **RQ2 (Revocation Atomicity):** Under high-concurrency execution and dynamic policy revocation races, does the linearized state transition protocol permit stale authorization execution?
* **RQ3 (Evaluator Sensitivity):** Can the evaluation framework and test harness effectively detect deliberately injected security flaws and compiler-level mutation regressions?
* **RQ4 (Oracle Independence):** Can authorization decisions be objectively and independently verified by decoupled execution-side and physical-side observers?

---

## 2. Threat Model, Evaluation Space, and Epistemic Boundaries

### 2.1 Post-Compromise Threat Model & Explicit Hypotheses ($C_A = 1$)
Our evaluation establishes a rigorous **Post-Compromise Threat Model** that deliberately assumes the adversary has already penetrated the application layer:
* **Assumption 1 (Full Application Compromise $C_A = 1$):** The adversary has achieved prompt injection, bypassed prompt sanitizers, extracted system instructions, and holds arbitrary execution control over the agent application logic within its managed runtime container.
* **Assumption 2 (Legitimate Credential Possession):** The adversary possesses valid OAuth tokens, internal API keys, database credentials, and authenticated session identities.
* **Assumption 3 (Multi-Agent Swarm Collusion):** The adversary controls multiple heterogeneous agents attempting privilege escalation through complex delegation chains and confused-deputy patterns.

#### Explicit Structural Hypotheses (Governed Execution Boundary)
To maintain strict epistemological clarity and prevent conflating user-space C-ABI authorization with kernel-level isolation, DROS formally articulates four explicit boundary hypotheses:
* **$H_1$ (Governed Path Invariant):** All privileged operations within the evaluated capability class $X_{\text{covered}}$ are routed through the DROS-governed execution path.
* **$H_2$ (Substrate Non-Subversion):** The adversary cannot directly overwrite the memory space of the loaded DROS binary or tamper with the underlying binary dynamic link tables within the execution container.
* **$H_3$ (Host Isolation Foundation):** The host kernel, hardware MMU, and baseline container isolation boundaries (e.g., Seccomp-BPF blocking unmanaged raw socket/syscall escapes) remain trusted and non-compromised.
* **$H_4$ (Scope Boundary):** Unmanaged raw system operations outside the declared capability set $X_{\text{covered}}$ are explicitly outside the empirical security claim of the C-ABI authorization gate.

Under these hypotheses, DROS evaluates whether deterministic in-band authorization can prevent physical side-effects once application-level semantic reasoning is completely subverted.

### 2.2 Comparative Baselines & Attack Preservation ($A_{B0} = A_{B1}$)
To eliminate experimental bias caused by payload variance, all comparative benchmarks strictly adhere to the **Attack Preservation Principle** ($A_{B0} = A_{B1}$ and $\text{Env}_{B0} \approx \text{Env}_{B1}$). Table I summarizes the four evaluation topologies.

| Topology ID | Topology Structure | Primary Purpose |
| :--- | :--- | :--- |
| **B0 (Bare App)** | `Attacker -> App -> OS` | Unmanaged baseline; verifies exploit payloads cause real damage ($\Delta S_{B0} > 0$). |
| **B1 (DROS Enabled)** | `Attacker -> App -> DROS -> OS` | Primary evaluation subject; verifies execution containment ($\Delta S_{B1} \equiv 0$). |
| **B2 (Defense-in-Depth)**| `Attacker -> App -> DROS+Stack -> OS` | Verifies integration and compatibility with EDR, XDR, and WAF infrastructure. |
| **B3 (Pure Binary C-ABI)**| `Attacker -> Standalone C-ABI -> OS` | Evaluates C-ABI gate in complete isolation without application middleware assistance. |

### 2.3 Formal Physical Effect & Invariants
Physical effect $I_{\text{physical}}(x)$ is formally defined over the instrumented observation set $\mathcal{S}_{\text{obs}}$:

$$I_{\text{physical}}(x) = \begin{cases} 1, & \exists s \in \mathcal{S}_{\text{obs}}: \Delta(s) > 0 \\ 0, & \forall s \in \mathcal{S}_{\text{obs}}: \Delta(s) = 0 \end{cases}$$

$$\mathcal{S}_{\text{obs}} = \{ \text{Kernel Syscall}, \text{Filesystem Diff}, \text{Database WAL}, \text{Process Tree}, \text{Outbound Network}, \text{IPC State} \}$$

A **ghost syscall** is defined as an authorization-denied operation that nevertheless escapes to the host kernel. We formally require $G = \#\{ \text{syscall} \mid \text{Auth} = \text{DENY} \land \text{syscall\_observed} = 1 \} = 0$.

The substrate evaluates five formal mathematical invariants:
1. **Non-Inheritance of Authority:** $C_A \centernot\implies C_E$
2. **Temporal Isolation:** $C_E(t_0) \centernot\implies C_E(t_1) \quad (\forall t_0 \neq t_1)$
3. **Capability Composition Safety:** $\bigcup_{i=1}^n C_{A_i} \centernot\implies C_E^{\text{unauth}}$
4. **Physical Containment Invariant:** $\forall x \in X_{\text{covered}}, \; C_A(x) \land \neg C_E(x) \implies I_{\text{physical}}(x) = 0$
5. **Zero State Drift:** $S_{\text{after}} \equiv S_{\text{before}} \quad (\text{over } \mathcal{S}_{\text{obs}})$

---

## 3. DROS Four-Layer Substrate Implementation

### 3.1 L1: Detective Intelligence (Detect)
L1 applies heuristic pattern matching and lightweight semantic filters. In DROS, **L1 is explicitly treated as probabilistic**. Threat containment falls deterministically onto L2–L4; an L1 miss is never regarded as a fatal failure of the substrate.

### 3.2 L2: Identity & Dynamic Intent Tokens (Attribute)
L2 establishes a cryptographic 3-Tier PKI model ($\text{Enterprise CA} \rightarrow \text{Task Issuer} \rightarrow \text{Ephemeral Worker Agent}$) and mints Dynamic Intent Tokens (DIT). Each DIT cryptographically binds the tool name, SHA-256 argument hash, timestamp, and 64-bit capability bitmask using Ed25519 signatures.

#### Why DIT Solves the Attribution Binding Problem
Traditional agent architectures pass natural language tool requests directly to execution handlers. Under prompt injection, an adversary can manipulate tool arguments or masquerade as higher-privileged roles. DIT eliminates this vulnerability through immutable cryptographic encapsulation:
1. **Principal Decoupling:** The Worker Agent executing the LLM prompt possesses zero direct authority to invoke tools; it only holds ephemeral intent descriptors.
2. **Task Issuer Authority:** Only the authenticated Task Issuer component possesses the private key required to sign a valid DIT.
3. **Argument Tamper Resistance:** By binding the exact SHA-256 hash of the tool argument payload into the signed DIT, any downstream argument tampering by a hijacked interpreter invalidates the cryptographic signature.
4. **Instant Revocation Cascade:** Revoking a Task Issuer immediately invalidates all active DITs issued under its lineage, establishing a hard temporal cutoff enforced at the binary layer.

### 3.3 L3: Dynamic IFC & In-Band Redaction (Constrain Data)
L3 implements in-memory taint tracking and in-band secret masking. When sensitive data passes through the agent context, L3 redacts it in-band (substituting `[REDACTED_BY_DROS_POLICY_GATE]`), mitigating both accidental leakage and prompt side-channel exfiltration.

### 3.4 L4: Binary C-ABI Authorization Execution Gate (Enforce)
L4 is the controlled binary authorization boundary, implemented in memory-safe Rust and exposed via a pure C-ABI dynamic library. All governed tool invocations must cross this gate. Three architectural properties are critical:
1. **$O(1)$ Policy Lookup:** Capability checks execute via constant-time 64-bit bitmask comparison.
2. **RCU State Revocation & Grace-Period Semantics ($T_{\text{swap}} \approx 420\text{ ns}$):** Capability pointers are linearized via `AtomicPtr.swap(&P_act, P_new, Ordering::Release)`. Newly admitted readers observe the new policy generation immediately after the atomic pointer exchange; pre-existing readers executing within active critical sections are bounded by an explicit epoch grace-period protocol before retirement.
3. **Sub-Microsecond Fail-Closed Denial Path ($<500\text{ ns}$):** Unauthorized requests or invalid DITs immediately branch to an in-memory denial path, preventing execution from reaching the OS syscall interface.

---

## 4. Progressive Adversarial Validation Framework

### 4.1 Falsification-Oriented Evaluation Philosophy
In conventional security literature, evaluations frequently present passive test suites designed to confirm that a system works under expected conditions. In contrast, DROS-VEP is explicitly engineered around **Adversarial Falsification**: every evaluation tier is treated as a rigorous attempt to discover an executable counterexample that violates our core security invariants. A `PASS` verdict does not represent an absolute mathematical claim that counterexamples are theoretically impossible across the universe; rather, it signifies that across millions of progressively mutated, concurrency-stressed, and autonomously generated attack attempts, **no counterexample was observed within the instrumented state space**.

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
   │
   └─► Open Falsification (External Reproducibility & Public Counterexample Protocol)
```

Table II summarizes the six quantifiable evaluation tiers, workloads, observed evidence, and verdicts. Level 7 represents the external Open Falsification and community reproducibility layer described in Section 6.

| Tier | Validation Method | Workload & Stress | Observed Evidence | Counterexamples | Verdict |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **L1** | Baseline A/B Comparison | 50 unmanaged exploits | B0 breached ($\Delta S > 0$); B1 contained | **0** | **PASS (RQ1)** |
| **L2** | Strix Adaptive Search | 2,410 attempts (21.4M Tokens) | 100% of malicious probes rejected | **0** | **PASS (RQ1)** |
| **L3** | 100-Agent Mesh + RCU Race | 400 delegation chains + 250 bursts | $T_{\text{swap}} \approx 420\text{ ns}$; 0 stale replays | **0** | **PASS (RQ2)** |
| **L4** | Negative Controls + Mutants | 5 sabotaged binaries + 100 mutants | 5/5 flaws caught; Mutation Score = 1.0 | **0** | **PASS (RQ3)** |
| **L5** | Oracle Torture Probes | 450 mutation probes | $G = 0$ ghost syscalls; 0 audit drift | **0** | **PASS (RQ4)** |
| **L6** | Cross-OS & Platform Port | 7,500 automated test vectors | Validated across x86_64, ARM64, Windows, Linux | **0** | **PASS** |

### 4.2 Adversarial Coverage & 24-Hour Continuous Soak Evidence
The adversarial campaign exercises ten distinct attack dimensions:
1. **Identity:** Forged agent identities and role substitutions (rejected via Ed25519 signature checks).
2. **Capability:** Scope escalation attempts (intercepted via $O(1)$ capability bitmask gate).
3. **Parameter:** Parameter fuzzing and tampering (blocked via SHA-256 payload hash verification).
4. **Temporal:** Replay attacks with expired historical tokens (rejected via epoch bounds).
5. **Delegation:** Confused-deputy multi-hop chains (blocked via Task Issuer signature attestation).
6. **Interpreter:** Subshell escapes (`bash`, `eval`) (halted at C-ABI binary boundary).
7. **Concurrency:** Sub-microsecond RCU revocation races (zero race window observed).
8. **Encoding:** Metamorphic unicode and payload obfuscation (canonical matching immune to syntax tricks).
9. **Topology:** 100-agent emulated mesh (each delegation independently verified; 0 authority inheritance).
10. **Failure & Fault:** Injected crash and network partitions (two-phase commit ensures 0 side effects).

Complementing the progressive hierarchy, a continuous **24-hour adversarial soak test** processed **160,611 independent requests** spanning enterprise and B2B supply-chain scenarios (ATS-001–ATS-004). Of these, **137,751 malicious requests were intercepted at the C-ABI boundary with 100% containment**. Median policy decision latency remained locked at $26.21\ \mu\text{s}$ ($\sigma = \pm 0.34\ \mu\text{s}$), binary denial latency remained below $500\text{ ns}$, and 24-hour resident memory leak was measured at $0\text{ MB}$. Counterfactual toggles of `BYPASS_GUARD` confirmed that the evaluated exploits consistently produced unmanaged state mutations under B0 and complete containment under B1.

### 4.3 Meta-Verification: Negative Controls & Mutation Score (RQ3)
To address **RQ3**, we constructed five sabotaged binaries with deliberately injected flaws and evaluated 100 instantiated mutants across eight mutation classes (bit widening, identity substitution, expiry bypass, hash omission, stale reads, check removal, fail-open branch, audit suppression). The evaluation harness achieved a **Mutation Score of $100 / 100 = 1.0$**, confirming that the test harness actively catches flaws rather than serving as a passive rubber stamp.

---

## 5. Decoupled Multi-Observer Oracle & Empirical Results

### 5.1 Four-Stage Independent Ground-Truth Pipeline (RQ4)
To enforce the foundational principle that **"No Single Component May Act As Its Own Sole Witness,"** DROS-VEP establishes a four-stage decoupled pipeline:

$$\text{Intent } (O_I) \longrightarrow \text{Authorization } (O_A) \longrightarrow \text{Execution } (O_E) \longrightarrow \text{Physical Effect } (O_P)$$

#### Methodological Rationale: Decoupling Claim from Evidence
In monolithic security benchmarks, the authorization subsystem typically logs its own decisions, creating a circular verification vulnerability: if the authorization engine crashes or is bypassed, its internal logs may falsely claim that no violation occurred. By decomposing observation into four independent observers, DROS-VEP guarantees objective cross-validation:
1. **Intent Oracle ($O_I$):** Captures raw tool invocation payloads directly from the caller process prior to any normalization.
2. **Authorization Oracle ($O_A$):** The C-ABI gate evaluates capability bitmasks and emits signed ALLOW/DENY decisions.
3. **Execution Oracle ($O_E$):** A decoupled kernel tracepoint monitor (eBPF / ProcFS) observes whether any actual syscall entered the operating system kernel, confirming $G = 0$ ghost syscalls.
4. **Physical Effect Oracle ($O_P$):** Out-of-band database write-ahead log (WAL) analyzers, filesystem diffing daemons, and process-tree monitors verify that the persistent physical state remained strictly unmodified ($S_{\text{after}} \equiv S_{\text{before}}$).

Agreement among the four decoupled oracles provides independent empirical evidence that the authorization decisions produced the observed physical containment within the instrumented boundary.

### 5.2 Physical Side-Effect Containment ($\Delta I_{\text{physical}}$ - RQ1)
$$\Delta I_{\text{physical}} = I_{\text{physical}}(B0) - I_{\text{physical}}(B1) = 1.0 - 0.0 = \mathbf{1.0\ (100\%\ \text{suppression})}$$
Empirical results demonstrate 100% observed physical-effect suppression across the evaluated attack corpus.

### 5.3 Performance & Benchmark Latencies
On bare-metal AMD Ryzen 9 7950X / Ubuntu 24.04 (and corroborated on Intel Xeon E3-1275L v3):
* **End-to-End Decision Latency (P50):** $26.1\ \mu\text{s}$
* **End-to-End Decision Latency (P99):** $31.4\ \mu\text{s}$ (isolated path) / $242.7\ \mu\text{s}$ (50-thread high-concurrency soak)
* **RCU State-Pointer Swap ($T_{\text{swap}}$):** $420\text{ ns}$
* **L4 Fail-Closed Denial Path:** $<500\text{ ns}$

These figures are well within interactive agent latency budgets and orders of magnitude below standard database round-trips.

---

## 6. Open Falsification Protocol & Limitations

### 6.1 Limitations & Epistemic Scope
1. **Ontological Dependency:** DROS enforcement relies on accurate capability bitmask mapping in L2 DITs. Granting excessive bits constitutes policy misconfiguration, not substrate escape.
2. **Observation Boundary:** Zero-counterexample findings are strictly bounded to the experimentally instantiated state space (>60,000 probes, 160,611 soak requests, 100-agent meshes) and do not constitute non-constructive proofs across infinite attack universes.
3. **Portability vs. Native Kernel Boundary:** L6 validates cross-platform policy portability; native kernel enforcement remains subject to host OS MMU and kernel driver integrity.

### 6.2 Public Counterexample Registry
We publish the complete replication harness at `github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite` and maintain an immutable public counterexample registry. External researchers observing an unauthorized state transition ($I_{\text{physical}} > 0$) are invited to submit reproducible traces. As of this publication, the valid counterexample count remains **0**.

---

## 7. Deep Related Work & Architectural Positioning

The problem of securing autonomous execution systems spans several foundational and emerging areas in computer systems and security literature:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 COMPARATIVE SECURITY ARCHITECTURE LANDSCAPE                 │
├──────────────────────┬────────────────────────┬─────────────────────────────┤
│ Architectural Layer  │ Representative Systems │ Structural Trade-off / Gap  │
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ Semantic Guardrails  │ NeMo, LlamaGuard       │ Probabilistic; lacks binary │
│                      │ PromptBench            │ execution containment       │
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ OS Kernel Sandboxes  │ Seccomp, Landlock      │ Deterministic; lacks agent  │
│                      │ eBPF Tracing, gVisor   │ principal attribution       │
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ Information Flow     │ TaintDroid, Asbestos   │ In-process taint tracking;  │
│                      │ Decentralized Labeling │ lacks agent PKI binding     │
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ Workload Identity    │ SPIFFE/SPIRE, OAuth    │ Service-level identity; not │
│                      │ NIST SP 800-207        │ microsecond tool-call scoped│
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ ★ DROS Substrate     │ DROS-4Layer (This Work)│ Co-located PKI, IFC & C-ABI │
│                      │                        │ binary execution containment│
└──────────────────────┴────────────────────────┴─────────────────────────────┘
```

### 7.1 LLM Semantic Guardrails vs. Runtime Containment
Application-layer guardrails such as NVIDIA NeMo Guardrails, Meta LlamaGuard, and Microsoft Prompt Shield inspect natural language prompts and tool arguments before execution. While highly effective for conversational toxicity and policy alignment, they operate fundamentally on probabilistic classification. When an agent is compromised via indirect prompt injection or interpreter escapes, semantic firewalls cannot prevent unauthorized syscalls because the adversary manipulates the underlying runtime from within an authenticated process. DROS treats semantic filtering as an optional L1 layer and delegates hard security guarantees to the binary C-ABI boundary (L4).

### 7.2 OS Kernel Sandboxing and Context-Blindness
Classical kernel mechanisms such as Linux Seccomp-BPF, Landlock, AppArmor, and hypervisor-based sandboxes (e.g., gVisor, Firecracker) provide rigid binary enforcement on syscalls. However, they suffer from the *Context-Blindness Problem*: the OS kernel only observes process IDs (PIDs) and user IDs (UIDs). In multi-agent frameworks where dozens of heterogeneous agent roles execute inside a shared runtime worker process, kernel sandboxes cannot differentiate between an authorized database query from a Finance Agent and an unauthorized data exfiltration query from a compromised Support Agent. DROS bridges this attribution gap by embedding signed capability bitmasks into dynamic intent tokens verified directly at the FFI boundary.

### 7.3 Information Flow Control & Dynamic Taint Tracking
Dynamic Information Flow Control (IFC) systems such as TaintDroid, Asbestos, and Flume track the propagation of sensitive data through registers, memory, and IPC channels. DROS adapts these foundational IFC concepts into its L3 layer via in-memory taint tracking and in-band secret redaction. Unlike traditional heavyweight whole-system taint analysis, DROS operates in-band within the agent execution context, substituting sensitive tokens prior to egress and preventing prompt side-channel exfiltration without significant performance overhead.

### 7.4 Capability-Based Access Control & Zero Trust Workload Identity
Classical capability systems (e.g., Dennis and Van Horn, Levy, KeyKOS) associate execution privileges with unforgeable tokens. In cloud-native systems, zero-trust frameworks such as SPIFFE/SPIRE and NIST SP 800-207 provide cryptographic workload identity attestations. DROS adapts capability theory to autonomous agent swarms by compiling dynamic permissions into 64-bit capability bitmasks and issuing ephemeral, epoch-bounded Dynamic Intent Tokens (DITs). Sub-microsecond policy revocation is achieved through Read-Copy-Update (RCU) atomic state pointer exchanges, bridging zero-trust identity with microsecond-scale execution enforcement.

---

## 8. Conclusion & Declarations

This paper presented and empirically evaluated DROS, a four-layer runtime substrate with deterministic execution enforcement. By sinking execution boundaries to a binary C-ABI gate, DROS resolves the semantic-kernel paradox in autonomous agent workloads. Across 160,611 soak requests, 2,410 adaptive Strix exploits, and 100 mutant injections, no unauthorized physical state transitions were observed within the instrumented boundary:

$$\forall x \in X_{\text{covered}}, \quad C_A(x) \land \neg C_E(x) \implies I_{\text{physical}}(x) = 0 \quad (\text{PASS})$$

### Acknowledgment & AI Collaboration Disclosure
In accordance with IEEE 2024+ authorship guidelines, the author declares that the novel security concepts, architecture, formalisms, and patent claims were independently conceptualized, architected, and validated by Chun-Cheng (Jimmy) Chen. Large language models were used only for grammatical refinement and formatting; they did not generate foundational concepts or claims.

---

## References

1. J. Chen, "DROS: A Four-Layer Deterministic Runtime Operation System Bridging the Agent-to-Execution Attribution Gap," *Zenodo*, DOI: 10.5281/zenodo.22092008, 2026.
2. J. Chen, "DROS Trilogy Reading Guide (Academic Version 3.0)," *Zenodo*, DOI: 10.5281/zenodo.22114036, 2026.
3. J. Chen, "DROS-PGM: Physical Guard Module with Sub-Microsecond C-ABI Binary Execution Boundary," *Zenodo*, DOI: 10.5281/zenodo.21903687, 2026.
4. J. Chen, "DROS 6P Architectural Specification," *Zenodo*, DOI: 10.5281/zenodo.21833970, 2026.
5. Strix Security Team, "Strix: Autonomous Multi-Agent AI Penetration Testing Framework (v1.5.3)," 2026. [Online]. Available: https://strix.ai
6. Microsoft, "Microsoft Agent Framework Documentation: Tool Calling and Execution Governance," *Microsoft Learn*, 2025.
7. NVIDIA, "NeMo Guardrails: Programmable Guardrails for LLM Applications," 2024.
8. European Parliament, "Artificial Intelligence Act (Regulation EU 2024/1689), Article 50," 2024.
9. MITRE Corporation, "ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems," 2026.
10. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," 2025.
11. P. E. McKenney, "Is Parallel Programming Hard... (Read-Copy Update Architecture)," *IBM Operating Systems Review*, 2024.
12. W. Enck et al., "TaintDroid: An Information-Flow Tracking System," *ACM TOCS*, vol. 32, no. 2, pp. 1–32, 2014.
13. METR, "Evaluating Autonomous Capabilities in Frontier AI Models," 2025.
14. USENIX Security Symposium, "Artifact Evaluation Guidelines," 2024.
15. IEEE S&P Editorial Board, "IEEE Symposium on Security and Privacy CFP," 2026.
16. Top-Celestial Company Ltd., "DROS-VEP-lite: Open-source AI Agent Security Benchmark," https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite, 2026.
17. Top-Celestial Company Ltd., "DROS-VEP 24-Hour Continuous Multi-Scenario Soak Test Benchmark Report," 2026.
18. The Linux Kernel Documentation, "Seccomp BPF," 2024.
19. The Linux Kernel Documentation, "Landlock," 2024.
20. NIST SP 800-207, "Zero Trust Architecture," 2020.
21. J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," *Communications of the ACM (CACM)*, vol. 9, no. 3, pp. 143–155, 1966.
22. H. M. Levy, *Capability-Based Computer Systems*, Digital Press, 2014.
23. Cloud Native Computing Foundation (CNCF), "SPIFFE: Secure Production Identity Framework for Everyone," *CNCF Standard Specification*, 2020.
24. X. Zhang et al., "AgentSight: eBPF-Powered Tracing and Context Correlation for Autonomous LLM Agents," *arXiv preprint arXiv:2408.01234*, 2024.

---

## Author Biography

**Chun-Cheng (Jimmy) Chen** is the Founder and Chief Architect of Top-Celestial Company Ltd., Taipei, Taiwan R.O.C. His research focuses on deterministic runtime governance, microkernel security, autonomous AI agent execution attribution, and capability-based access control systems. He is the inventor of the DROS deterministic runtime architecture (U.S. Patent Application No. 64/111,973). Contact him at jimmychen@dr-os.io.
