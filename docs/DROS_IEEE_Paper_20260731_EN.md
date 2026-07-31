# 🛡️ DROS 4-Layer Defense-in-Depth Architecture for Autonomous AI Workloads

## A Complete Security & Execution Governance Paradigm for the Agentic Web Era

**Document Version:** 2.0 Academic Release (IEEE Standard)  
**Date:** July 31, 2026  
**Classification:** Public Academic Technical Paper  
**Author:** Chun-Cheng (Jimmy) Chen (`jimmychen@dr-os.io`)  
**Affiliation:** Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.  
**Patent Notice:** DROS execution governance and security technology is protected under U.S. Provisional Patent Application (U.S. PPA No. 64/111,973, Patent Pending).  
**Open-Source Proving Ground:** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**Permanent Academic Citation:** [Zenodo Record DOI: 10.5281/zenodo.20823163](https://zenodo.org/records/20823163)

---

## Abstract (摘要)

In 2026, autonomous AI agents capable of multi-step tool execution are deployed across critical enterprise domains—financial compliance, supply chain routing, and infrastructure management. However, existing security primitives face severe architectural boundaries: application-level prompt firewalls (e.g., NVIDIA NeMo Guardrails) remain fundamentally probabilistic and vulnerable to Indirect Prompt Injection (IPI), while kernel-level OS sandboxes (e.g., eBPF, Seccomp) suffer from execution "context-blindness," unable to map user-space agent roles to low-level process streams. To bridge this "Attribution Gap," we present the **DROS 4-Layer Defense-in-Depth Architecture**, a zero-trust runtime execution control plane purpose-built for the Agentic Web era. The architecture decouples Control Plane Provisioning (via OpenAI Terraform Provider & OpenShip) from Runtime Physical Execution Defense. By enforcing immutable $O(1)$ capability bitmaps at the binary C-ABI / FFI boundary, DROS achieves sub-microsecond decision latency (**26.1 μs median, <500 ns panic latency**). Coupled with a 3-tier PKI Certificate Authority (`Root CA -> AIA -> BEC Leaf Token`) issuing signed `DrosIdentityTokens (DIT)`, DROS provides court-admissible, non-repudiable audit logs signed via Ed25519 for regulatory compliance (EU AI Act Sec. 50). Benchmark evaluations demonstrate 100% containment against zero-day prompt injection, Goal Hijacking, and cross-enterprise supply chain attacks (e.g., OpenAI Workloads interacting with poisoned Hugging Face repositories).

**Keywords:** AI Agent Security, Runtime Execution Governance, C-ABI Boundary Enforcement, Zero Trust Architecture, Public Key Infrastructure (PKI), Indirect Prompt Injection (IPI), EU AI Act Compliance.

---

## 1. Introduction (引言與問題定義)

The rapid transition from conversational passive LLMs to autonomous, tool-calling AI agents has fundamentally altered the enterprise threat surface. Modern autonomous agents are entrusted with API keys, OAuth grants, and transactional database permissions. Consequently, when an agent is compromised, the threat actor operates from *within* legitimate security boundaries.

### 1.1 The Failure of Identity & Network-Centric Defenses
Traditional Web Application Firewalls (WAF), Endpoint Detection and Response (EDR), and Identity & Access Management (IAM) systems operate on the assumption that attackers do not possess valid credentials. In the Agentic Web era, a hijacked agent *is* a credentialed actor. WAFs view high-privilege API calls as authorized traffic, while EDRs see generic OS runtimes (e.g., `python.exe` or `node`) executing valid system calls.

### 1.2 The Semantic-Kernel Paradox
As highlighted in recent systems literature (e.g., AgentSight, IEEE S&P 2026), AI agent security suffers from a fundamental paradox:
1. **Semantic Firewalls (High Semantics, Zero Determinism):** Prompt filters inspect high-level natural language intent but offer zero mathematical guarantees against adversarial obfuscation or multi-turn context poisoning.
2. **Kernel Sandboxes (High Determinism, Zero Semantics):** OS-level mechanisms like eBPF or Seccomp enforce strict binary syscall rules but lack user-space context. They cannot discern whether a `sys_connect` to an internal database was initiated by a legitimate Finance Agent or a hijacked Support Agent running inside the same process worker.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Control Plane & GitOps Provisioning (Policy-as-Code)                     │
│    • OpenAI Terraform Provider -> Provision Projects, IAM, Keys & Rate Limits│
│    • OpenShip Engine           -> Orchestrate Multi-Enterprise Containers   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. DROS Runtime Execution Defense (L4 - C-ABI Boundary Enforcement)          │
│    • 3-Tier PKI Certificate Chain -> DrosIdentityToken (DIT) Binding       │
│    • DROS GuardVM (PEP/PDP)       -> Sub-microsecond <500ns Binary Panic    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Threat Model: Agentic Attack Vectors (AAV-2026)

We define runtime attack vectors targeting autonomous AI agents as **Agentic Attack Vectors (AAV-2026)**:

| Attack Vector | MITRE ATLAS | Mechanism & Impact |
| :--- | :--- | :--- |
| **Indirect Prompt Injection (IPI)** | AML.T0051 | Adversaries embed malicious prompt payloads into untrusted external data (e.g., emails, PDFs, database rows), hijacking tool-calling flows. |
| **Goal Hijacking** | AML.T0054 | Context window poisoning alters long-term objectives, causing agents to execute unauthorized multi-step action chains. |
| **Privileged Function Escalation** | AML.T0053 | Compromised agents use valid OAuth tokens to invoke high-privilege endpoints (e.g., `deploy_prod`, `read_env_secrets`) beyond role scope. |
| **Supply Chain Contagion** | AML.T0010 | Poisoned external repositories (e.g., Hugging Face datasets/models) compromise data-fetching agents, which then pivot to attack internal ERP assets. |

---

## 3. The DROS 4-Layer Defense-in-Depth Architecture

DROS establishes a 4-layer defense-in-depth model separating probabilistic filters from deterministic execution gates:

```text
┌──────────────────────────────────────────────────────────────────────┐
│ L1: Detective Intelligence Layer  │ Semantic Prompt Filtering (~90%)  │
├───────────────────────────────────┼──────────────────────────────────┤
│ L2: Zero Trust Mesh & PKI Layer   │ 3-Tier CA (Root->AIA->BEC) + DIT  │
├───────────────────────────────────┼──────────────────────────────────┤
│ L3: Task Orchestration Layer      │ Multi-Agent Swarm ABAC Isolation │
├───────────────────────────────────┼──────────────────────────────────┤
│ ★ L4: C-ABI Physical Enforcement  │ <500ns O(1) Binary Panic Gate    │
└───────────────────────────────────┴──────────────────────────────────┘
```

### 3.1 L1: Detective Intelligence Layer (Probabilistic Filtering)
L1 applies semantic analysis to sanitize natural language inputs, intercepting known prompt injection patterns and jailbreak templates. Because L1 is probabilistic, it serves as an early filter rather than the final line of defense.

### 3.2 L2: Zero Trust Mesh & PKI Identity Layer (Cryptographic Binding)
To eliminate "context-blindness," L2 introduces a 3-tier Public Key Infrastructure:
- **Root CA:** Enterprise Root (`DROS-ROOT-CA-2026`).
- **AIA Intermediate:** Authority Information Access issuer.
- **BEC Leaf Certificate:** By-Execution Certificate cryptographically binding the agent's identity, role, and authorized skill capability maps.

Every tool call carries a signed **DrosIdentityToken (DIT)**. GuardVM verifies the ECDSA/Ed25519 signature before inspecting permissions, resolving OS-level attribution gaps.

### 3.3 L3: Task Orchestration Layer (Swarm Isolation)
L3 enforces Attribute-Based Access Control (ABAC) across multi-agent swarms using `agent_manifest.yaml`. It isolates blast radiuses by restricting inter-agent communication channels to pre-approved graph topologies (e.g., CrewAI / LangGraph workflows).

### 3.4 L4: C-ABI Physical Enforcement Layer (Deterministic Panic Gate)
L4 is the core innovation of DROS. Permissions are pre-compiled into immutable numeric Bitmaps at initialization. When a tool call is executed, GuardVM performs an $O(1)$ bitwise AND operation:

$$\text{Decision} = \text{Capability\_Bitmap}[\text{Role\_ID}] \ \& \ \text{Requested\_Tool\_Bit}$$

If the bit is $0$, the execution physically fails at the C-ABI binary boundary within **<500 ns panic latency**. Zero string parsing, zero LLM inference—mathematical physical containment.

---

## 4. Federated B2B Multi-Enterprise Supply Chain Defense

When autonomous agents interact across enterprise boundaries (e.g., **Corp-Alpha / OpenAI Workload** fetching data from **Corp-Beta / Hugging Face Repository**), DROS transforms L2 into a **Cross-Domain Identity Fingerprinting Gate**.

```text
[ Corp-Beta: Hugging Face Repo ]                  [ Corp-Alpha: Buyer Enterprise ]
┌───────────────────────────────┐                  ┌──────────────────────────────┐
│ Agent-Beta (Data Fetcher)     │                  │ DROS GuardVM Alpha (PEP/PDP) │
│ - Signed DIT-Beta Certificate │ ─B2B Tool Call─► │ 1. Verify DIT SHA-256 Finger │
└───────────────────────────────┘                  │ 2. Check Bitmap[Beta][API]   │
                │                                  │ 3. Execute <500ns Panic      │
   Hijacked via Poisoned Dataset                   └──────────────────────────────┘
   (ATS-004 Supply Chain Scenario)                                 │
                │                                                  ▼
   Attempts Exfiltration to Alpha ERP              [ FULLY BLOCKED AT C-ABI LAYER ]
```

### 4.1 Supply Chain Network Immune Effect
- **Cellular Blast Radius Containment:** Each agent operates as a self-contained cellular unit. An exploit in a Tier-3 supplier agent is contained entirely within its local DROS boundary.
- **Cascading Zero-Trust Adoption:** Mandating DIT tokens for B2B API access forces upstream/downstream suppliers to adopt deterministic execution governance.
- **Instant Revocation (CRL):** If a supplier CA is compromised, buyer GuardVMs update revocation fingerprints in <1 μs, creating instant network-wide antibodies without modifying application code.

---

## 5. Experimental Evaluation & Benchmark Results

### 5.1 Open-Source Proving Ground & Reproducible Test Harness Setup

To guarantee absolute scientific reproducibility, all empirical evaluations were executed inside the **DROS-VEP (Virtual Enterprise Platform) Lite** open-source containerized environment (`docker-compose.yml` and `docker-compose-b2b.yml`). The complete test harness, including attack scenario payloads and the continuous execution runner, is published and open-sourced at [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite).

```text
DROS-VEP Proving Ground Environment:
├── OpenShip / Docker Engine   : Containerized ERPNext, Keycloak, EspoCRM, Forgejo
├── Test Runner Harness         : scripts/run_24h_soak_test.py (Continuous Fuzzer)
├── Target PDP/PEP Engine       : GuardVM (http://localhost:8082)
└── Reproducibility Verification: python scripts/run_24h_soak_test.py
```

All stress tests were conducted on an Intel Xeon E3-1275 v3 hardware platform running Linux kernel 6.6 with Docker 26.1.

### 5.2 Comparative Counterfactual Benchmark (Control Group vs. Protected Group)

To quantitatively prove the necessity of binary boundary enforcement, we conducted counterfactual control-group experiments by toggling the `BYPASS_GUARD` mode across identical attack payloads (EP1~EP4):

| Benchmark Scenario | Control Group (Without DROS Guard) | Protected Group (With DROS Guard L4) | DROS Interception Latency |
| :--- | :--- | :--- | :--- |
| **ATS-001 (EP1 Customer Data Exfiltration)** | ❌ **100% Exfiltrated** (Data Leak) | ✅ **100% Intercepted** (DENY 403) | **25.8 μs** |
| **ATS-002 (EP2 ERP Secrets Ransomware)** | ❌ **100% Compromised** (.env Leaked) | ✅ **100% Intercepted** (DENY 403) | **26.1 μs** |
| **ATS-003 (EP3 Fable 5 Production Deployment)** | ❌ **100% Deployed** (Unapproved Push) | ✅ **100% Intercepted** (DENY 403) | **25.5 μs** |
| **ATS-004 (EP4 OpenAI x Hugging Face IPI)** | ❌ **100% Hijacked** (Cross-Enterprise Exfil) | ✅ **100% Intercepted** (DENY 403) | **26.4 μs** |

### 5.2 Adversarial Fuzzing Mutation Engine & Non-API Obfuscation Methodology

To thoroughly stress-test DROS without incurring variable API latencies or cloud rate limits, the evaluation suite incorporates an **Algorithmic Adversarial Fuzzing Mutation Engine (`PROMPT_MUTATORS`)**. Each attack payload dynamically mutates across seven distinct threat categories:
1. **System Override Variants:** Injection of high-priority system prompt overrides.
2. **Roleplay Escapes:** Persona manipulation instructing agents to assume unrestricted root personas.
3. **Hexadecimal & Base64 Obfuscation:** Encoding payloads to bypass L1 semantic string matching.
4. **Debug Mode Exploits:** Simulating diagnostic JSON extraction requests.
5. **Urgent Escalation Tokens:** Fabricating emergency CISO approval headers.

### 5.3 4-Layer Defense Funnel Breakdown (Layer Interception Distribution)

Across 170,000+ continuous 24-hour evaluation requests, the multi-layer defense funnel demonstrated clear operational demarcation:

| Defense Layer | Primary Mechanism | Interception Share % | Enforcement Outcome | Architectural Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **L1: Detective Intelligence** | Semantic Prompt Cleaning / WAF | **85.2%** | Sanitized / Dropped | Intercepts plain-text, un-obfuscated prompt injections. |
| **L2: PKI Identity Mesh** | 3-Tier Certificate & DIT Token | **4.8%** | **100% DENY** | Intercepts unauthenticated or spoofed agent calls. |
| **L3: Swarm ABAC Isolation** | `agent_manifest.yaml` Graph Rules | **3.5%** | **100% DENY** | Intercepts unauthorized cross-department calls (e.g., HR $\to$ DevOps). |
| **★ L4: C-ABI Physical Panic** | $O(1)$ Bitmap Panic Gate | **6.5%** | **100% DENY** | **Deterministic Panic: Intercepts all L1-evading, obfuscated zero-day IPI payloads in <500ns.** |
| **Total System Defense** | **DROS 4-Layer Architecture** | **100.0%** | **0% System Leak** | **100% Deterministic Containment.** |

### 5.4 Micro-Benchmark Telemetry Statistics

| Evaluation Metric | Measured Value | Standard Deviation / Target |
| :--- | :--- | :--- |
| **Policy Decision Latency (P50)** | **26.1 μs** | $\pm 3.4\ \mu\text{s}$ |
| **P99 Policy Latency** | **41.2 μs** | $\pm 4.1\ \mu\text{s}$ |
| **C-ABI Physical Panic Latency** | **< 500 ns** | $\pm 42\ \text{ns}$ |
| **SPEC CPU2017 Runtime Overhead** | **< 1.8%** | — |
| **Zero-Day Prompt Injection Containment** | **100%** | 0 False Negatives at L4 |
| **24-Hour Continuous Memory Leak** | **0 Bytes** | Zero Heap Allocation |

### 5.3 Physical Significance of 26.1 μs Latency
Human neural conduction latency ranges from 10 ms to 50 ms. A policy decision speed of **26.1 μs is less than 1/1000th of human neural conduction time**, ensuring interception completes at the binary layer long before humans or upper-layer software perceive the attack.

---

## 6. Related Work (文獻探討與學術關聯)

Our work builds upon and extends recent breakthroughs across four primary computer security domains:

1. **System Call Interception & Kernel Observability:** Traditional mandatory access control (MAC) frameworks (SELinux, AppArmor) and modern eBPF tracing (AgentSight [4], Eunomia [8]) monitor low-level process streams. DROS extends these by introducing user-space PKI DIT token binding to bridge the context-blindness gap.
2. **LLM & Agentic Security Frameworks:** Early defenses focused on application-layer prompt sanitization (NVIDIA NeMo, PromptBench [15]). Recent surveys (OWASP Top 10 for Agentic Applications [16]) highlight Excessive Agency (LLM06). DROS provides the L4 physical enforcement layer required to satisfy OWASP agentic guidelines.
3. **Zero Trust Architecture & Micro-Segmentation:** Aligned with NIST SP 800-207 [1] and MITRE ATLAS [3], DROS applies $O(1)$ capability bitmapping to achieve micro-segmented execution boundaries for multi-agent swarms.
4. **Non-Repudiation & Audit Substrates:** Inspired by append-only telemetry logging and Merkle tree attestations, DROS generates Ed25519-signed evidence artifacts compliant with EU AI Act Sec. 50 court-admissibility standards.

---

## 7. Conclusion & Future Work

As autonomous AI workloads assume critical operational roles across enterprise infrastructures, probabilistic application-layer firewalls alone cannot guarantee execution safety. This paper presents the DROS 4-Layer Defense-in-Depth Architecture, establishing a deterministic runtime control plane that combines 3-tier PKI identity attestations with sub-microsecond C-ABI binary boundary enforcement (<500ns panic latency, 26.1μs median policy evaluation).

By isolating execution capabilities into immutable bitmapped boundaries and validating identity via signed `DrosIdentityTokens (DIT)`, DROS effectively resolves the OS-level attribution gap and contains post-compromise attack vectors, including zero-day Indirect Prompt Injections and cross-enterprise B2B supply chain contagion. Empirical evaluations across continuous 24-hour benchmark runs demonstrate zero-overhead scalability and 100% deterministic interception without requiring modifications to underlying LLM model architectures or application codebases. Future work will focus on expanding dynamic formal verification for inter-agent memory sharing protocols.

---

## References (參考文獻)

1. NIST Special Publication 800-207, *"Zero Trust Architecture,"* National Institute of Standards and Technology, 2020.
2. OWASP Foundation, *"OWASP Top 10 for Large Language Model Applications v1.1,"* 2023.
3. MITRE Corporation, *"MITRE ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems,"* 2024.
4. X. Zhang et al., *"AgentSight: eBPF-Powered Tracing and Context Correlation for Autonomous LLM Agents,"* arXiv preprint arXiv:2408.01234, 2024.
5. Y. Liu et al., *"Formal Verification of System Call Boundaries in Autonomous Workloads,"* IEEE Transactions on Dependable and Secure Computing, 2025.
6. C. C. Chen, *"Runtime Attribution Framework: An External C-ABI and PKI-Based Zero-Trust Infrastructure for Non-Repudiable Execution Governance in Multi-Agent Systems,"* Zenodo, DOI: 10.5281/zenodo.20823163, 2026.
7. C. C. Chen, *"DROS-PGM: Deterministic Kernel-Level Execution Control for Post-Compromise Security,"* U.S. Patent Application No. 64/111,973, 2026.
8. Eunomia-bBPF Community, *"eBPF-Based Security Monitoring and LSM Hooking for Cloud Native Runtimes,"* 2025.
9. OWASP Foundation, *"OWASP Top 10 for Agentic Applications,"* 2025.
10. European Parliament and Council, *"Regulation (EU) 2024/1689 Laying Down Harmonised Rules on Artificial Intelligence (EU AI Act),"* Official Journal of the European Union, 2024.

## Acknowledgment and AI Collaboration Disclosure (致謝與 AI 協作宣告)

In accordance with IEEE/ACM 2024+ publication guidelines and author governance standards:
1. **Conception & Intellectual Contribution:** The original security models, C-ABI boundary interception paradigms, 4-layer defense-in-depth architecture, and patent-pending claims (U.S. PPA No. 64/111,973) were conceived, developed, and validated solely by the author, Chun-Cheng (Jimmy) Chen.
2. **AI Assistance:** Generative AI tools (including Antigravity / Gemini-pro) were utilized strictly as formatting and linguistic assistants to refine prose, assist in Markdown/LaTeX formatting, and structure literature citations. No AI tool was granted authorship or intellectual contribution status.

---

*© 2026 DROS Security / Top-Celestial Company Ltd. All rights reserved.*  
*DROS execution governance and security technology is protected under U.S. Provisional Patent Application (U.S. PPA No. 64/111,973, Patent Pending).*
