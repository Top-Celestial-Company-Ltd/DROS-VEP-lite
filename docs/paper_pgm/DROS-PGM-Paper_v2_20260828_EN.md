# 🛡️ DROS-PGM: A Deterministic Post-Compromise Execution Containment Substrate for Autonomous AI Workloads (v2.0)

## Counterexample-Driven Validation of Non-Inheritance Between Application Compromise and Execution Authority

**Document Version:** 2.0 Submission Candidate / Peer-Reviewed Academic Manuscript (Target: IEEE TIFS / ACM CCS)  
**Date:** August 28, 2026  
**Author:** Chun-Cheng (Jimmy) Chen (`jimmychen@dr-os.io`)  
**Affiliation:** Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.  
**Patent Notice:** Deterministic runtime governance and physical defense technologies are protected under U.S. Provisional Patent Application (U.S. PPA No. 64/111,973, Patent Pending).  
**Open-Source Testbed & Replication Package:** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**Permanent Academic Citation (DOI):** [Zenodo Record DOI: 10.5281/zenodo.21903687](https://doi.org/10.5281/zenodo.21903687)

---

## Abstract

In modern autonomous AI agent workloads where agents obtain legitimate credentials and invoke consequential tools, traditional application-layer perimeters suffer from fundamental failure modes. Conventional defenses rely on probabilistic semantic guardrails or coarse-grained operating system sandboxes, operating under the foundational assumption of preventing compromise. However, once internal dialogue or interpreter environments succumb to indirect prompt injection or logic hijacking, attackers inevitably inherit valid credentials and execute irreversible physical state changes.

This paper presents **DROS-PGM (Physical Guard Module)**, a post-compromise execution containment substrate operating at the binary execution control plane. Architecturally, **the C-ABI / FFI boundary manages policy evaluation and principal capability attribution, while OS kernel hooks enforce mandatory authorization checks over explicitly instrumented operation classes $X_{\text{covered}}$**. PGM decouples application principal identity from binary execution authority, maintaining the formal containment invariant via sub-microsecond ($P50 = 353\text{ ns}$) lock-free evaluation and atomic RCU state-pointer swaps:
$$\forall x \in X_{\text{covered}}, \quad Auth_E(x) = \text{DENY} \implies Exec_{\text{unauthorized}}(x) = 0 \quad \land \quad \forall s \in \mathcal{S}_{\text{obs}}, \; \Delta s = 0$$

To rigorously evaluate boundary robustness without self-witness circularity, we introduce the **PGM-VEP Five-Tier Progressive Falsification Methodology (V1--V5)**, encompassing attack-equivalent baselines ($A_{B0} = A_{B1}$), adaptive white-box state search, negative control meta-verification (5/5 injected flaw detection and 100/100 instantiated mutant kill score), a four-stage decoupled ground-truth oracle pipeline ($O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$), and cross-environment independent replication across Linux x86_64, ARM64, and Windows environments. Across 68,355 adversarial and validation executions plus 50,000 benign baseline requests (118,355 total executions, benign false-denial rate $\text{BFDR} = 0/50,000$), zero unauthorized executions or state drifts were observed within explicitly instrumented boundaries. We report these guarantees as empirical invariants over the evaluated state space rather than ungrounded global proofs, and establish an open counterexample registry to support ongoing adversarial falsification by the academic community.

**Keywords:** Execution Containment Substrate, Post-Compromise Security, Kernel Enforcement Boundary, Dynamic Capability Revocation (RCU), Progressive Adversarial Falsification, Decoupled Oracles.

---

## 1. Problem Definition: Application Compromise Does Not Entail Execution Authority

Autonomous AI Agent architectures (e.g., LangGraph, CrewAI, AutoGen) routinely operate with elevated privileges, including database read/write access, cloud API keys, inter-process communication (IPC), and system command execution. In these environments, security architectures encounter a fundamental **Semantic-Kernel Paradox**:

1. **Semantic Application Middleware (High Semantics, Zero Determinism):** Prompt firewalls, JSON schema validators, and output filters operate purely at the natural language or declarative data plane. Lacking physical execution containment, they are bypassed by interpreter escapes (`eval`, `bash`), dynamic parameter obfuscation, or multi-step logic evasion.
2. **Operating System Sandboxes (High Determinism, Zero Semantics):** Traditional kernel mechanisms (Seccomp, Linux Namespaces, eBPF filters) enforce binary constraints but lack application semantic awareness. When an agent holding a valid database connection pool executes a malicious write, the kernel cannot distinguish whether the request originated from an authorized finance agent or a prompt-injected support agent.

This disconnect causes **Identity-Authority Confusion**: once the application layer is compromised ($C_A = 1$), the attacker automatically inherits the full ambient authority of the underlying host process. We formalize the core research thesis:
> **Compromise of an application principal does not entail inheritance of unrestricted execution authority ($C_A \centernot\implies C_E$).**

---

## 2. Dual Boundaries & Architectural Placement

To avoid architectural ambiguity, the system establishes a strict separation of concerns between **DROS (Upstream Governance)** and **DROS-PGM (Substrate Execution Guard)** through a Dual-Boundary Model:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Semantic & Application Layer                                                │
│ [Agent Swarm / LangGraph] ──► Compromised Principal: C_A = 1                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (DROS L1-L3: DIT Token & Capability Bitmask)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Boundary 1: C-ABI / FFI Policy Evaluation & Attribution Boundary            │
│ [PGM Policy Gate: O(1) Bitmask Lookup / RCU State Pointer (353 ns)]         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (Pass / Fail-Closed Panic)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Boundary 2: OS Kernel Mandatory Enforcement Boundary over X_covered         │
│ [Linux LSM Hook / Windows Minifilter] ──► Mandatory Interception on X_cov   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (Deny: ΔS = 0; Allow: Benign Only)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Physical State Space: Filesystem, Database WAL, Network, Process Tree       │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **DROS (Upstream Governance)**: Manages cryptographic credentials (PKI), Dynamic Intent Tokens (DIT), and information-flow taint tracking (L1--L3).
* **DROS-PGM (Substrate Execution Guard)**: **Eliminates asymmetric cryptography on the critical path**, focusing strictly on L2-cached $O(1)$ SIMD bitmask evaluation, lock-free RCU state swaps, and binary kernel hook mediation.

### Explicitly Instrumented Operation Classes ($X_{\text{covered}}$) & Non-Claim Clause
Security claims are strictly bounded to the explicitly instrumented operation classes $X_{\text{covered}}$:
1. **Filesystem Modification ($X_{\text{fs}}$)**: `sys_enter_openat` (O_CREAT/O_WRONLY/O_RDWR), `sys_enter_unlinkat`, `sys_enter_renameat2`, `sys_enter_write`.
2. **Process Lifecycle ($X_{\text{proc}}$)**: `sys_enter_execve`, `sys_enter_execveat`, `sys_enter_ptrace`, `sys_enter_kill`.
3. **Network Endpoints ($X_{\text{net}}$)**: `sys_enter_connect` (external IP/port redirection), `sys_enter_bind`, `sys_enter_sendto`.
4. **Memory & IPC Privilege ($X_{\text{ipc}}$)**: `sys_enter_mprotect` (PROT_EXEC), `sys_enter_process_vm_writev`.

$$X_{\text{covered}} = X_{\text{fs}} \cup X_{\text{proc}} \cup X_{\text{net}} \cup X_{\text{ipc}}$$

> **Non-Claim Clause:** *PGM does not claim syscall-complete mediation over uninstrumented kernel paths. Security claims are strictly restricted to the explicitly instrumented operation classes $X_{\text{covered}}$ and their enumerated enforcement hooks.*

---

## 3. Formal Invariants & Security Claim Boundary Matrix

DROS-PGM formally decouples four fundamental operational primitives:
* **Application Principal Identity ($Identity_A$)**: Logical role or session identity managed by the application.
* **Capability Grant ($Auth_C$)**: Permission set expressed via capability bitmasks.
* **Execution Gate Authorization ($Auth_E$)**: Binary determination ($\text{ALLOW} / \text{DENY}$) evaluated at runtime by C-ABI and kernel hooks.
* **Physical Effect ($I_{\text{physical}}$)**: Observable mutations in filesystem, DB WAL, kernel syscalls, or external network sockets.

### Formal Invariants

1. **Non-Inheritance of Authority Axiom:**
   $$C_A \centernot\implies C_E$$
   Compromise of application context or interpreter state does not grant binary execution authority.
2. **Covered Containment Invariant:**
   $$\forall x \in X_{\text{covered}}, \quad Auth_E(x) = \text{DENY} \implies Exec_{\text{unauthorized}}(x) = 0 \quad \land \quad \forall s \in \mathcal{S}_{\text{obs}}, \; \Delta s = 0$$
3. **Ghost Syscall Measurement Oracle:**
   The ghost syscall metric $G$ is formulated as an empirical measurement oracle:
   $$G = \# \{ x \in X_{\text{covered}} \mid Auth_E(x) = \text{DENY} \land \text{SyscallObserved}(x) = 1 \}$$
   The experimental falsification target is observing $G \equiv 0$ across all evaluated corpora.
4. **Linearization Semantics of Dynamic Revocation:**
   Following the atomic pointer swap linearization point ($T_{\text{swap}} = 420\text{ ns}$), all subsequent policy evaluations deterministically observe the revoked state; in-flight operations admitted prior to $T_{\text{swap}}$ are isolated via pre-allocated safe-state execution contexts.

### Table 1: DROS-PGM Security Claim Boundary Matrix

| Claim Category | Statement & Bounded Scope | Epistemic Status |
| :--- | :--- | :--- |
| **Claimed** | In $X_{\text{covered}}$, operations evaluated as `DENY` produce zero unauthorized executions | Architectural Invariant |
| **Claimed** | Dynamic revocation takes effect for subsequent calls immediately at linearization point $T_{\text{swap}}$ | Linearization Semantics |
| **Observed** | Across the instantiated evaluation corpus, observed ghost syscall count $G = 0$ | Empirical Fact within $\mathcal{S}_{\text{obs}}$ |
| **Observed** | Across explicitly instrumented state space $\mathcal{S}_{\text{obs}}$, observed state drift $\Delta S = 0$ | Multi-Oracle Differential Fact |
| **Not Claimed** | Global syscall-complete mediation over uninstrumented OS kernel paths | Explicit Non-Claim (Out of Scope) |
| **Not Claimed** | Defense against kernel-mode rootkits or hardware MMU penetration | Host TCB Trust Assumption |
| **Not Claimed** | Semantic correctness of upstream application capability bitmask mapping | Upstream Responsibility |
| **Not Claimed** | Safety of uninstrumented asynchronous driver IOCTL routines | Explicit Non-Claim ($x \notin X_{\text{covered}}$) |

---

## 4. Threat Model: Post-Compromise Assumption ($C_A = 1$)

### A. In-Scope Attacker Capabilities
1. **Full Application Compromise ($C_A = 1$):** Attacker controls agent cognitive flow via indirect prompt injection or achieves arbitrary code execution within the host application container.
2. **Ambient Credential Possession:** Attacker possesses access to in-memory OAuth tokens, database connection handles, and API keys.
3. **Multi-Agent Collusion & Confused Deputy:** Attacker coordinates multiple agents across complex delegation chains attempting privilege escalation.

### B. Out-of-Scope & TCB Assumptions
* **Excluded Attacker:** Attacker cannot execute kernel-mode rootkits, tamper with PGM binary text segments in protected memory, or corrupt CPU MMU page tables.
* **Trusted Computing Base (TCB):** Strictly limited to the PGM binary gate, CPU instruction set architecture (Ring 0/MMU), OS kernel LSM drivers, and immutable audit buffers.

---

## 5. PGM-VEP Five-Tier Progressive Adversarial Falsification Methodology (V1--V5)

To eliminate tester bias, we enforce the **No-Self-Witness Principle ($O_I \neq O_A \neq O_E \neq O_P$)**:
> *"The authorization decision engine must never serve as the sole source of evidence for successful execution containment."*

```text
  [ V1: Attack the PGM ] ────► Attack-Equivalent Baseline Comparison (B0 vs B1, A_B0 = A_B1)
           │
           ▼
  [ V2: Counterexample Search ] ──► Wide-State White-Box Adaptive Fuzzing & Stress (60,000+ Probes)
           │
           ▼
  [ V3: Attack the Test ] ──► Meta-Verification: Negative Controls & 100 Mutants (100% Kill Rate)
           │
           ▼
  [ V4: Attack the Oracle ] ──► 4-Stage Fact Chain with 9 Oracle Torture Vectors (G = 0 Ghost Syscalls)
           │
           ▼
  [ V5: Cross-Env Reproduction ] ─► Open Replication Package across 3 Heterogeneous Environments
```

### Table 2: PGM-VEP Methodology Tiers to Open-Source Asset Mapping

| Methodology Tier | Objective & Verification Focus | Open-Source Executable Harness | Evidence & Report Asset |
| :--- | :--- | :--- | :--- |
| **V1: Attack the PGM** | Attack-equivalent baseline ($A_{B0}=A_{B1}$) | `benchmark/run_benchmark.py`<br>`scripts/run_cybermes_crucible.py` | `reports/CYBERMES_POST_COMPROMISE_REPORT.md`<br>`reports/evidence/cybermes_crucible_traces.json` |
| **V2: Counterexample Search** | 60,000+ white-box adaptive search | `benchmark/stress_test_accelerated.py`<br>`scripts/run_24h_soak_test.py` | `reports/DROS_24H_Soak_Test_Final_Report.md`<br>`reports/stress_summary.json` |
| **V3: Attack the Test** | 5 sabotaged binaries + 100 mutants | `benchmark/conformance_test.py` (w/ mutant harness) | `reports/conformance_report.json` |
| **V4: Attack the Oracle** | 4-stage fact chain ($O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$) | `benchmark/replay.py`<br>`telemetry/event_logger.py` | `reports/COMPARATIVE_GOVERNANCE_REPORT.md`<br>`reports/evidence/comparative_benchmark/` |
| **V5: Cross-Environment** | Independent replication across 3 OS targets | `docker-compose.yml`<br>`docker-compose-b2b.yml` | `reports/benchmark_summary.json`<br>`docs/TESTBED_SPECIFICATION.md` |

---

## 6. Experimental Results & Metric Analysis

### 6.1 Evaluation Accounting Matrix

Table 3 provides an accounting of all evaluated probes and workloads:

#### Table 3: Evaluation Accounting Matrix

| Validation Tier | Test Configuration & Architecture | Unique Probes | Replay / Concurrent Load | Total Executions | Observed CE | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **V1 (Baseline)** | B0/B1 Equivalence ($A_{B0}=A_{B1}$) | 50 | 250 | 300 | 0 | **PASS** |
| **V2 (Adversarial)** | White-box search + Concurrency crucible | 2,410 | 57,590 (21.4M Tokens) | 60,000 | 0 | **PASS** |
| **V3 (Meta-Verify)** | 5 sabotaged binaries + 100 mutants | 105 | — | 105 | 0 | **PASS** |
| **V4 (Oracle Torture)**| 4-stage fact chain + 9 torture vectors | 450 | — | 450 | 0 | **PASS** |
| **V5 (Cross-Env)** | 3 OS environment profiles | 1,500 | 6,000 | 7,500 | 0 | **PASS** |
| **Adversarial Subtotal**| **V1--V5 Cumulative Adversarial Load** | **4,515** | **63,840** | **68,355** | **0** | **ALL PASS** |
| **Benign Workload** | Selected SPEC CPU2017 + Benign Tools | 50,000 | — | 50,000 | 0 | **BFDR = 0/50,000** |
| **Total Workload** | **Comprehensive Full-Spectrum Load** | **54,515** | **63,840** | **118,355** | **0** | **ALL PASS** |

*Note: Benign False-Denial Rate (BFDR) reflects erroneous rejections of legitimate requests.*

### 6.2 Meta-Verification: Negative Controls & Mutation Testing (V3)
$$\text{Corpus Mutation Score} = \frac{\text{Killed Mutants}}{\text{Total Instantiated Mutants}} = \frac{100}{100} = 1.0$$
The test framework achieved a 100% kill rate (100/100) across 8 flaw classes (bit widening, identity substitution, expiry bypass, unconditional allowance, etc.), confirming high sensitivity to instantiated defects.

### 6.3 Performance Overhead & Selected SPEC CPU2017 Benchmarks

Table 4 breaks down latency overhead on Intel Xeon Gold 6330 @ 2.00GHz (128GB ECC RAM, Ubuntu 22.04 LTS):

#### Table 4: Selected SPEC CPU2017 Benchmark Breakdown

| Benchmark Suite | Workload Characteristics | Native Baseline (sec) | DROS-PGM Enabled (sec) | Relative Overhead (%) |
| :--- | :--- | :---: | :---: | :---: |
| **500.perlbench_r** | C interpreter & high-frequency string ops | 412.3 | 417.6 | +1.28% |
| **502.gcc_r** | C compiler, process creation & memory alloc | 328.7 | 333.1 | +1.34% |
| **505.mcf_r** | Combinatorial optimization (memory intensive) | 289.4 | 291.8 | +0.83% |
| **520.omnetpp_r** | Discrete event network simulation | 356.1 | 360.2 | +1.15% |
| **523.xalancbmk_r** | XML parsing & DOM tree transformations | 298.5 | 302.7 | +1.41% |
| **557.xz_r** | Data compression & intensive I/O streaming | 385.2 | 389.9 | +1.22% |
| **Geometric Mean** | **Overall System & Compute Overhead** | — | — | **+1.20% (±0.12%)** |

During a 72-hour continuous soak test, PGM sustained an **aggregate policy decision throughput of 952,991 QPS across 16 concurrent worker threads** with zero memory leakage.

### 6.4 Microbenchmark Protocol & Full Latency Distribution

Measurements adhere to standard microbenchmarking protocols: single physical core affinity (`taskset -c 2`), Intel Turbo Boost/C-states disabled, CPU invariant TSC (`CPUID` barrier + `RDTSCP`), with $10^6$ warm-up iterations followed by $10^7$ production measurements.

#### Table 5: PGM In-Band Latency Distribution ($10^7$ Samples, Unit: Nanoseconds ns)

| Metric | Min | P50 | P90 | P95 | P99 | P99.9 | Max | StdDev | 95% Confidence Interval |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C-ABI Policy Table Lookup** | 312 ns | **353 ns** | 388 ns | 398 ns | 412 ns | 445 ns | 620 ns | 18.4 ns | [351, 355] ns |
| **RCU Pointer Swap ($T_{\text{swap}}$)** | 390 ns | **420 ns** | 428 ns | 432 ns | 438 ns | 462 ns | 580 ns | 12.1 ns | [416, 424] ns |
| **Fail-Closed Fast Denial Path** | 410 ns | **465 ns** | 480 ns | 484 ns | 488 ns | 512 ns | 640 ns | 15.2 ns | [462, 468] ns |

---

## 7. Limitations & Epistemic Scope

1. **Empirical Invariants vs. A Priori Proofs:** Zero counterexamples across 118,355 executions is bounded by the evaluated corpus and does not constitute a priori proof across infinite attack universes.
2. **Cross-Platform Enforcement Heterogeneity:** V5 evaluates binary policy semantics and integration portability; native kernel enforcement depth depends on host OS primitives (Linux LSM hooks vs. Windows Minifilter/callbacks).
3. **Upstream Semantic Dependency:** PGM precision depends on correct mapping of application operations to capability bitmasks by upstream governance.
4. **Hardware & Kernel TCB Boundary:** Security assumes uncompromised Ring 0 execution and CPU MMU integrity.

---

## 8. Discussion: Post-Compromise Security Paradigm

Traditional security focuses on **pre-compromise defense** (minimizing $\Pr(C_A = 1)$). In autonomous agent workloads where prompt injection and interpreter exploitation are realistic failure modes, PGM shifts the paradigm to **post-compromise containment**: ensuring that even when an agent is fully compromised, binary execution boundaries deterministically intercept unauthorized physical side effects.

---

## 9. Related Work & Systems Taxonomy

#### Table 6: Runtime Security & Agent Governance Taxonomy Matrix

| Architecture Category | Representative Systems | Enforcement Point | Semantic Attribution | Runtime Enforcement | Post-Compromise Security | Kernel Boundary | Dynamic Revocation |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Prompt Guardrails** | NeMo Guardrails [7] | LLM / Text Boundary | Full | Text Filter Only | Weak | None | High Latency |
| **Tool / MCP Gateways** | AgentVisor [16], MCP PEP [17] | Tool Call Interface | Full | Tool Layer Only | Partial | Missing Syscall Gate | Dynamic |
| **Type Systems** | Tracked Capabilities [18] | Language Type System | Full | Compile-Time | Static Assumption | None | Static Only |
| **Capability Kernels / LibOS** | Agent libOS [14], authgate [15] | Runtime Primitive | Full | Runtime Primitive | Architectural | Over Host OS | Supported |
| **Traditional OS Sandboxes** | seccomp-bpf [2], SELinux [1] | OS Syscall / Kernel MAC | None | Kernel Mandatory | Process Level | Full Kernel Hook | Static Config |
| **DROS-PGM (This Work)** | **DROS-PGM (v2.0)** | **C-ABI + Kernel Hook** | **Full (via DIT)** | **Sub-Microsecond** | **$C_A=1$ Enforced** | **Dual Boundary ($X_{\text{cov}}$)** | **RCU Linearized** |

#### Table 7: Methodological Rigor Matrix across Runtime Defense Systems

| Defense Category / System | System Instance | Attack-Equiv Baseline ($A_{B0}=A_{B1}$) | Meta-Verify (Mutant Kill) | Decoupled Multi-Oracle | Non-Inheritance under $C_A=1$ | Cross-Platform Reproduction | Full V1--V5 Standard |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Prompt Guardrails** | NeMo Guardrails et al. | Weak | None | None | No | Rare | No |
| **Tool / MCP Gateways** | AgentVisor, MCP PEP et al. | Partial | None | Weak | Partial | Rare | No |
| **OS Sandboxes / MAC** | seccomp-bpf, SELinux | Feasible | None | Weak | Partial | Common | No |
| **Commercial Endpoint Agent** | CrowdStrike, Palo Alto, Microsoft | Internal | Undisclosed | Undisclosed | Partial | Limited | No |
| **Capability Kernels** | authgate et al. | Yes | Limited | Partial | Conceptual | Limited | No |
| **Container / MicroVM** | gVisor, Firecracker | Feasible | None | Weak | Partial | Common | No |
| **DROS-PGM (This Work)** | **DROS-PGM v2.0** | **Yes** | **Yes (100/100 Killed)** | **Yes** | **Yes** | **Yes** | **Yes** |

*Table 7 Note: To the best of our survey across publicly documented literature and industry whitepapers, we did not identify an existing defense system that simultaneously reports and opens all five validation dimensions under a unified reproducible evaluation package.*

---

## 10. Conclusion & Declarations

This paper presented DROS-PGM, establishing a deterministic binary execution containment boundary for autonomous AI workloads. Evaluated via the five-tier progressive falsification methodology (V1--V5) across 118,355 executions, PGM maintained the core invariant with zero observed counterexamples. The complete testbed and open falsification protocol are released to advance AI runtime security on empirical scientific foundations.

### Acknowledgment & AI Collaboration Disclosure
In accordance with IEEE / ACM 2023+ guidelines on Generative AI and research integrity:
1. **Research Originality & Intellectual Property**: The system architecture, dual-boundary model (C-ABI attribution and kernel enforcement), formal invariants, five-tier progressive falsification methodology (V1--V5), and patent claims (U.S. PPA No. 64/111,973) were independently conceived, designed, formalized, and empirically evaluated by the author Chun-Cheng (Jimmy) Chen.
2. **Role of AI Tools**: Large Language Models (LLM Agents / Gemini) were utilized strictly as assistive productivity tools for grammatical proofreading, English structural refinement, LaTeX syntax troubleshooting, and script formatting. AI tools did not generate any foundational patent concepts, core invariants, or novel theoretical constructs. The author retains full intellectual, empirical, and legal responsibility for the integrity and claims of this work.

---

## References

1. P. Loscocco and S. Smalley, "Meeting critical security objectives with security-enhanced Linux," in *Proc. Ottawa Linux Symposium*, 2001.
2. W. Drewry, "Chrome sandbox: seccomp-bpf," *Google Security Blog*, 2012.
3. J. Edge, "A seccomp overview," *LWN.net*, 2015.
4. B. Gregg, *BPF Performance Tools*. Addison-Wesley, 2019.
5. A. Birgisson, J. Polakis, S. Erlingsson, A. Sommese, and M. Anisetti, "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud," *NDSS*, 2014.
6. R. Sandhu, E. Coyne, H. Feinstein, and C. Youman, "Role-Based Access Control Models," *IEEE Computer*, vol. 29, no. 2, pp. 38-47, 1996.
7. NVIDIA, "NeMo Guardrails: Programmable Guardrails for LLM Applications," *NVIDIA Developer Documentation*, 2024.
8. European Parliament, "Artificial Intelligence Act (Regulation EU 2024/1689), Article 50: Transparency and Traceability of AI Systems," *Official Journal of the European Union*, 2024.
9. MITRE Corporation, "ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems," *MITRE ATLAS Knowledge Base*, 2026.
10. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," *OWASP Standard*, 2025.
11. P. E. McKenney, "Is Parallel Programming Hard, And, If So, What Can You Do About It? (Read-Copy Update Architecture)," *Linux Technology Center, IBM Operating Systems Review*, 2024.
12. W. Enck et al., "TaintDroid: An Information-Flow Tracking System for Real-Time Privacy Monitoring on Smartphones," *ACM Transactions on Computer Systems (TOCS)*, vol. 32, no. 2, pp. 1-32, 2014.
13. METR (Model Evaluation and Threat Research), "Evaluating Autonomous Capabilities in Frontier AI Models," *METR Technical Research Standard*, 2025.
14. Agent libOS Team, "Agent libOS: A Library-OS-Inspired Runtime for Long-Running, Capability-Controlled LLM Agents," *arXiv preprint arXiv:2606.03895*, June 2026.
15. Authgate Team, "A Capability Kernel for Agent Authorization," *SSRN Electronic Journal*, abstract id 6931639, July 2026.
16. AgentVisor Team, "AgentVisor: Defending LLM Agents Against Prompt Injection via Semantic Virtualization," *arXiv preprint arXiv:2604.24118*, April 2026.
17. MCP Security Group, "Runtime Policy Enforcement for MCP-Based LLM Agents," *MDPI Electronics*, vol. 15, no. 13, p. 2829, 2026.
18. Capability Tracking Authors, "Securing Agents With Tracked Capabilities," in *Proc. ACM Conference on AI and Agentic Systems*, DOI: 10.1145/3786335.3813127, 2026.
19. LITMUS Team, "LITMUS: Benchmarking Behavioral Jailbreaks of LLM Agents in Real OS Environments," *arXiv preprint arXiv:2605.10779*, May 2026.
20. J. Chen, "DROS-PGM: Physical Guard Module with Sub-Microsecond C-ABI Binary Execution Boundary," *Zenodo Research Report*, DOI: 10.5281/zenodo.21903687, 2026.
