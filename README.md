# 🛡️ VEP: Open Agent Security Research Testbed
### A Composable, System-Level Evaluation Infrastructure for Post-Compromise & Physical AI Research

> **"VEP (Vulnerability & Exploitability Protocol) is an open, implementation-independent research evaluation environment for determining whether Agent security controls remain effective after compromise, particularly at the boundary between Agent authorization and actual system execution. DROS-VEP Lite is the open reference implementation of the VEP research protocol (RFC-010), providing an out-of-the-box, deterministic execution substrate alongside other Agent runtime and execution-control implementations."**
>
> > [!IMPORTANT]
> > **Scientific Research Charter:**  
> > **VEP does not produce a single security score. It measures which post-compromise properties each substrate can enforce, which it cannot express natively, and which properties can only be established through formal assurance.**  
> > *(VEP 不產生單一安全分數；它測量各 substrate 能實際執行哪些 Post-Compromise 性質、哪些性質無法由其原生模型表達，以及哪些性質只能透過形式驗證建立。)*
>
> *"Can your AI Agent execution authority remain deterministically contained after compromise? Prove it."*

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Official Website](https://img.shields.io/badge/Official%20Website-dr--os.io-00f2fe.svg)](https://dr-os.io)
[![DROS Hacker Edition](https://img.shields.io/badge/Edition-DROS%20Hacker-ffaa00.svg)](https://github.com/Top-Celestial-Company-Ltd/VajraClaw-Hacker)
[![Specification: RFC-010](https://img.shields.io/badge/Specification-RFC--010%20Open%20VEP-purple.svg)](docs/RFC-010-dros-vep-spec.md)
[![Architecture: OpenShip](https://img.shields.io/badge/Substrate-OpenShip%20Composable-teal.svg)](#-openship-composable-architecture)
[![Reference Substrate: DROS-Guard](https://img.shields.io/badge/Reference--Substrate-DROS--Guard-cyan.svg)](docs/RFC-010-dros-vep-spec.md)
[![Open Falsification: Accepting Counterexamples](https://img.shields.io/badge/Open%20Falsification-Accepting%20Counterexamples-brightgreen.svg)](#-submit-a-counterexample-open-falsification-protocol)
[![Policy Evaluation P50: 26.1μs](https://img.shields.io/badge/Policy%20Evaluation%20P50-26.1%CE%BCs-emerald.svg)](#-benchmark-methodology--measurement)
[![Emergency Panic Path: <500ns](https://img.shields.io/badge/Emergency%20Panic%20Path-%3C500ns-red.svg)](#-benchmark-methodology--measurement)

[English](README.md) | [繁體中文](README_zh.md)

> [!TIP]
> 📚 **Academic & Research Citation**: If you use this research testbed or benchmark suite in your work, cite via [`CITATION.cff`](CITATION.cff) or see [RFC-010 Specification](docs/RFC-010-dros-vep-spec.md).  
> 🔬 **Open Research Infrastructure**: Built on the **OpenShip** containerized substrate, VEP allows researchers to independently swap reasoning models (LLMs), agent frameworks, and defense kernels without vendor lock-in.  
> 🧨 **Open Adversarial Falsification Channel is LIVE**: We actively invite researchers to challenge and falsify our execution invariants: **[👉 Submit a Counterexample](../../issues/new?template=counterexample.md)**. All submissions are triaged against formal criteria.

---

## 🏛️ OpenShip Composable Architecture & Runtime Closed Loop

Traditional AI security benchmarks measure prompt toxicity or rely on out-of-band proxy monitors that cannot prevent post-compromise execution escapes. VEP combines **OpenShip containerized composability** with a **system-level in-band execution governance loop**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. OpenShip Composable Evaluation Layer (Open, Composable, Transparent)      │
│    • Hot-Pluggable Agents  : LangGraph, AutoGen, CrewAI, OpenClaw, Custom   │
│    • Hot-Pluggable Models  : GPT-4o, Claude 3.5, Llama 3, DeepSeek, Local   │
│    • Hot-Pluggable Vectors : RFC-010 Threat Scenarios, MITRE ATLAS Injections│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ System-Call / Tool-Call Boundary
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ 2. System-Level Deterministic Runtime Closed Loop (In-Band Enforcement)     │
│    • Pre-Execution   : Positive capability bitmask check (O(1), 26.1μs)      │
│    • In-Execution    : In-band C-ABI interception, 18-PHI redaction, HITL    │
│    • Post-Execution  : Zero-leak fail-closed abort, append-only Merkle proof│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 5-Minute Research Experiment (Reproduce in 60 Seconds)

Evaluate post-compromise containment on your local machine with zero proprietary dependencies:

```bash
# 1. Clone the open research testbed
git clone https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite.git
cd dros-vep-lite

# 2. Launch the containerized evaluation environment
docker compose up -d

# 3. Execute the Post-Compromise Crucible Benchmark
python scripts/run_cybermes_crucible.py
```

Inspect interactive audit logs and evidence artifacts in real time at `http://localhost:8080`.

---

## 🎯 Cross-Domain Research Testbed Matrix

VEP provides multi-domain evaluation fixtures reproducing 2026 real-world security incidents across enterprise cloud, on-device mobile, and physical robotics:

| Domain Track | Incident & Threat Vector | Target Execution Surface | MITRE ATLAS | In-Band Governance Action |
| :--- | :--- | :--- | :--- | :--- |
| **Cloud & API** | **ATS-001**: 0-Day Sandbox Escape & Exfiltration | `create_socket_connection` | **AML.T0051** | **DENY (<500ns Panic)** |
| **Enterprise ERP** | **ATS-002**: Confused Deputy ERP Ransomware | `write_encrypt_database` | **AML.T0052** | **DENY (<500ns Panic)** |
| **Autonomous Model** | **ATS-004**: PyTorch Model Weight Hijacking | `encrypt_pytorch_weights` | **AML.T0054** | **DENY (0ms Hard Lock)** |
| **Physical AI / UAV** | **Paper 6**: Mid-Air Disarm & 100-Drone Mesh Swarm | Flight Controller Telemetry | **AML.T0040** | **Kinematic Envelope Hold** |
| **Mobile On-Device** | **Paper 5**: SMS Prompt Injection & In-App Purchase | Mobile OS Intent / Keystore | **AML.T0055** | **Dynamic Redaction (Mask)** |

---

---

## 🏛️ Scientific Evidence & Benchmark Index

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📚 1. Core Technical Architecture Trajectory (The 6-Paper Program)          │
│    • Trajectory Guide: docs/trilogy_guide/DROS_Trilogy_Reading_Guide_EN.md  │
│    • Paper 1 (6P Model): docs/paper_6p/ (Six Trust Boundaries)              │
│    • Paper 2 (4-Layer Runtime): docs/paper_4layer/ (Attribution & Merkle)   │
│    • Paper 3 (PGM Control): docs/paper_pgm/ (Kernel-Level C-ABI Intercept)  │
│    • Paper 4 (WebMCP Governance): dros-webmcp/ (Agentic Web Attribution)    │
│    • Paper 5 (Mobile Security): paper-mobile/ (Digital Action Containment)  │
│    • Paper 6 (Physical AI UAV): paper-uav/ (Cyber-Physical Containment)     │
│    • 72-Hour Continuous Multi-Scenario Soak Test (160,611 Requests)         │
│      └─ Report: reports/DROS_24H_Soak_Test_Final_Report.md                  │
│      └─ Harness: scripts/run_24h_soak_test.py                               │
│    • ⚡ System Overhead & Performance Microbenchmark (Latency, CPU, Mobile)  │
│      └─ Report: reports/DROS_SYSTEM_OVERHEAD_BENCHMARK_REPORT_EN.md          │
│                                                                             │
│ 🧪 2. Extended Evaluation Scenarios (RFC-010 Standard Matrix)               │
│    • ATS-001: Indirect Prompt Injection (IPI Exfiltration)                  │
│    • ATS-002: Goal & Context Hijacking                                      │
│    • ATS-003: Privilege Escalation Across API Boundaries                    │
│    • ATS-004: Federated B2B Multi-Enterprise Supply Chain Poisoning         │
│                                                                             │
│ 🔬 3. Active Crucible & Comparative Benchmarks (Post-Compromise & Boundary)   │
│    • ATS-005: Post-Compromise Execution Containment (Cybermes Integration)  │
│      └─ Report: reports/CYBERMES_POST_COMPROMISE_REPORT.md                  │
│    • Multi-Architecture Comparative Study (Baseline vs. AGT vs. DROS)       │
│      └─ Report: reports/COMPARATIVE_GOVERNANCE_REPORT.md                    │
│      └─ Evidence Package: reports/evidence/comparative_benchmark/           │
│                                                                             │
│ ⚔️ 4. Public Redteam Benchmark Suites (Suites A--F Standard Matrix)           │
│    • Coverage: Prompt Injection, Privilege Escalation, RCU Race, FFI Fuzz    │
│      └─ Specification: docs/specifications/DROS_PUBLIC_REDTEAM_TEST_PLAN_v0.1.md │
│      └─ Master Runner: tests/redteam/run_redteam_benchmark.py               │
│                                                                             │
│ 🛸 5. Physical AI & Drone Swarm SITL Benchmark (Edge & Homelab Safety)       │
│    • Coverage: Mid-Air Disarm Injection, 100-Drone Swarm Mesh Delegation     │
│      └─ Location: benchmarks/physical_drone/                                │
│      └─ Master Runner: python benchmarks/physical_drone/run_drone_bench.py   │
│                                                                             │
│ 📱 6. Mobile SDK & On-Device App Governance Benchmark (iOS/Android Safety)   │
│    • Coverage: SMS/Web Prompt Injection, Biometric In-App Purchase Defense   │
│      └─ Location: benchmarks/mobile_sdk/                                     │
│      └─ Master Runner: python benchmarks/mobile_sdk/run_mobile_bench.py      │
│                                                                             │
│ 🧪 7. The Bare-Metal Isolation Crucible (Post-Compromise Authority Survives) │
│    • Invariant: Integrity(Agent)=0, Integrity(Upper Governance)=0            │
│      └─ Location: benchmarks/bare_metal_crucible/                            │
│      └─ Master Runner: python benchmarks/bare_metal_crucible/run_crucible.py │
└─────────────────────────────────────────────────────────────────────────────┘
```

📖 **Research Note**: [How to Break Your AI Agent in 5 Minutes (And Rebuild It Stronger)](docs/guides/HOW_TO_BREAK_YOUR_AI_AGENT_IN_5_MINUTES.md)  
🛂 **Open Agent Passport SDK**: [libdros-id (RFC-010 W3C DID & Ed25519 SDK)](sdk/libdros-id/libdros_id.py)  
🧭 **Reading Guide to Trajectory**: [DROS Trilogy Reading Guide](docs/trilogy_guide/DROS_Trilogy_Reading_Guide_EN.md)

---

## 🔬 Research Discovery & Academic Scope

> *VEP evaluates whether Agent execution authority remains constrained after Agent compromise, with particular emphasis on runtime enforcement, execution-boundary containment, revocation, provenance, and reproducible security evaluation.*

This repository and protocol may be relevant to researchers, evaluators, and system architects studying:

* **Agent Execution Authority & Governance**: Formalizing the transition from non-deterministic agent cognition to bounded physical execution.
* **Agent-to-Execution Attribution**: Cryptographically linking agent intents, authorization tokens, and physical system calls.
* **Runtime Enforcement for Autonomous AI Agents**: Deterministic in-process C-ABI / kernel interception versus probabilistic semantic guardrails.
* **Post-Compromise Agent Security**: Containing unauthorized system effects when the agent reasoning layer is assumed fully compromised.
* **Execution-Boundary Security**: Preserving containment invariants under multi-hop confused deputy and prompt-injected delegation chains.
* **Agent Capability & Dynamic Authorization**: Fine-grained capability bitmask evaluations ($O(1)$ constant time) and zero-window RCU policy revocation.
* **Deterministic Runtime Enforcement**: Enforcing fail-closed containment under adversarial resource starvation and syscall flood conditions.
* **Agent Security Benchmarks & Testbeds**: Providing reproducible, multi-track testbeds across Cloud B2B, Physical Robotics/Drones, and Mobile on-device SDKs.
* **Execution Provenance & Cryptographic Audit**: Maintaining append-only, tamper-evident Merkle hash chains supporting technical traceability relevant to EU AI Act / NIST SP 800-207 requirements.

> **💡 Conformance & Substrate Decoupling:**  
> **DROS is not required for VEP conformance.** VEP defines an open, vendor-neutral evaluation protocol; DROS is provided as **one concrete executable reference substrate** for demonstrating, benchmarking, and validating VEP experiments.

---

## ⚡ Quick Start (60 Seconds)

```bash
# 1. Clone the repository
git clone https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite.git
cd dros-vep-lite

# Standard Single Enterprise Sandbox (Default Single-Node Mode)
docker compose up -d

# 🏢 Advanced: B2B Multi-Enterprise Supply Chain Mode (Federated Defense)
docker compose -f docker-compose-b2b.yml up -d
```

### 🏢 B2B Multi-Enterprise Supply Chain Mode (Federated Defense)
Want to evaluate cross-enterprise Agent interactions and supply chain attacks?
* **Corp-Alpha (OpenAI Agent Workload)**: Operates GuardVM at `localhost:8082`
* **Corp-Beta (Hugging Face Repository)**: Operates GuardVM at `localhost:9082`
* **EP4 Scenario (ATS-004: OpenAI × Hugging Face Supply Chain Poisoning)**: Simulates an OpenAI Agent retrieving a poisoned dataset/model from Hugging Face. The embedded Indirect Prompt Injection (IPI) attempts to hijack the agent to exfiltrate Corp-Alpha's financial secrets. Even with valid OAuth tokens, Corp-Alpha's GuardVM intercepts the cross-enterprise attack at the C-ABI boundary in **<500ns**!

# 3. Open Interactive Web Dashboard
# Navigate to http://localhost:8080 in your browser

```text
Attack ───► Policy Evaluation ───► Evidence Artifact ───► Deterministic Replay
```

---

## 🧨 Submit a Counterexample (Open Falsification Protocol)

DROS-VEP adheres strictly to the principle of **Open Adversarial Falsification**. We invite the academic community, security researchers, and engineers to submit reproducible counterexamples that violate our empirical core invariants:

> Within the explicitly instrumented operation classes $X_{\text{covered}}$, whenever `Auth_E(x) = DENY`:  
> **Unauthorized execution count is zero ($Exec_{\text{unauthorized}} = 0$) and observable state drift is zero ($\Delta S_{\mathcal{S}_{\text{obs}}} = 0$).**

### Criteria for a Valid Counterexample
- **Deterministic Reproducibility**: 100% reliably reproducible under the official DROS / PGM containerized environment.
- **Scope Alignment**: Falls within the instrumented operation classes $X_{\text{covered}}$ ($X_{\text{fs}} \cup X_{\text{proc}} \cup X_{\text{net}} \cup X_{\text{ipc}}$) or demonstrates an uninstrumented execution escape path.
- **Actionable Evidence**: Includes concrete reproduction steps, environment specs, expected vs. actual behavior, raw syscall traces, WAL diffs, or replay scripts.

### How to Submit
1. Use our **[Counterexample Issue Template](../../issues/new?template=counterexample.md)** (or open a GitHub Issue labeled `counterexample`).
2. Provide all environment metadata and reproduction steps.
3. Submissions will be triaged publicly, evaluated against the formal invariants, and recorded in the permanent evaluation matrix.

**Current Status (as of 2026-08-28 Benchmark Record): Valid Counterexamples = 0**

> *Note: Even if a submission is ultimately triaged as "Out of $X_{\text{covered}}$ Design Scope" or an environmental artifact, we deeply value boundary clarification reports and will acknowledge contributions publicly.*

---

## 💡 Why Existing AI Benchmarks Are Not Enough

Most AI benchmarks measure LLM intelligence, coding skills, or prompt toxicity. **DROS-VEP measures a completely different dimension: Runtime Tool-Call Authorization & Privileged Execution Governance.**

| Existing Benchmark | What It Measures | What It Does NOT Measure |
| :--- | :--- | :--- |
| **PromptBench** | Prompt robustness & adversarial text | Runtime Tool execution & API permissions |
| **AgentBench** | Multi-turn task completion rate | Runtime authorization & privilege boundaries |
| **SWE-bench** | Software engineering & coding ability | Enterprise RBAC/ABAC boundary violation |
| **GAIA** | General AI assistant capability | Zero-trust runtime policy enforcement |
| **DROS-VEP** | **Runtime Governance & PEP Authorization** | —— (Complements capability benchmarks) |

---

## 🏗️ Architecture & Ecosystem

DROS-VEP Lite leverages the **[OpenShip Ecosystem](https://openship.org)** and integrates seamlessly with **OpenAI Terraform Provider (GitOps Policy-as-Code)** to deliver a complete Enterprise AI Governance Architecture:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Control Plane & GitOps Provisioning                                      │
│    • OpenAI Terraform Provider -> Provision Projects, Service Accounts & Keys│
│    • OpenShip Engine           -> Orchestrate Multi-Enterprise Containers   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Runtime Execution Defense (DROS Layer 4 - C-ABI Boundary)                │
│    • 3-Tier PKI Identity Chain -> DrosIdentityToken (DIT) Cryptographic Binding│
│    • DROS GuardVM (PEP/PDP)    -> Sub-microsecond <500ns Binary Interception │
└─────────────────────────────────────────────────────────────────────────────┘
```

While OpenAI's Terraform Provider manages **Control Plane Provisioning** (Projects, IAM, Rate Limits), **DROS GuardVM** provides the essential **Runtime Execution Defense** — ensuring that when an agent holding legitimate credentials is hijacked via Indirect Prompt Injection (IPI), unauthorized tool calls are deterministically intercepted at the C-ABI boundary.

```text
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Network Perimeter   │ WAF (Cloudflare, Palo Alto)  │ -> Blocks L3-L7 SQLi/DDoS
├──────────────────────────────┼──────────────────────────────┤
│ Layer 2: Endpoint & Host     │ EDR (CrowdStrike, Sentinel)  │ -> Blocks OS Ransomware
├──────────────────────────────┼──────────────────────────────┤
│ Layer 3: Identity & IAM      │ Keycloak, Active Directory   │ -> Manages Human OAuth/JWT
├──────────────────────────────┼──────────────────────────────┤
│ ★ Layer 4: AI Agent Runtime  │ DROS PEP/PDP + ATR Sandbox   │ -> Blocks Unauthorized Tools
└──────────────────────────────┴──────────────────────────────┘
                               │
                               ▼
        Exports PKI Evidence to Enterprise SIEM (Splunk, Elastic)
```

### 💡 Why Traditional Security (WAF/Keycloak) Is Blind to ATS Scenarios
In an indirect prompt injection attack (ATS-001), the hijacked AI Agent possesses a **valid Keycloak JWT token**. When the agent queries `/api/erp/finance`, WAF inspects the request: *"Valid HTTPS, clean JSON, valid OAuth token. Access Granted!"*

Traditional WAFs see a **100% legitimate user making a clean REST API call**. The attack is hidden inside the **LLM Semantic Context**. This is why DROS PEP/PDP is required at the tool execution boundary.

---

## 🎯 Threat Scenarios & Research Fixtures (RFC-010 Standard Matrix)

VEP provides standardized, synthetic evaluation fixtures reproducing critical post-compromise threat models, mapped directly to **MITRE ATLAS**:

| Scenario ID | Research Fixture / Threat Model | Evaluated Failure Mode | Target Execution Surface | MITRE ATLAS | In-Band Governance Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ATS-001** | Zero-Day Sandbox Escape & Exfiltration | Cross-process socket leak via hijacked tool invocation | `create_socket_connection` | **AML.T0051** | **DENY (<500ns Panic)** |
| **ATS-002** | Confused Deputy Storage Tampering | Unauthorized database encryption via legitimate API key | `write_encrypt_database` | **AML.T0052** | **DENY (<500ns Panic)** |
| **ATS-003** | Privilege Escalation Across API Boundaries | High-privilege environment secret harvesting | `read_env_secrets` | **AML.T0053** | **DENY (26.1μs Guard)** |
| **ATS-004** | Autonomous Model Weight Poisoning | Persistent local model file corruption & weight tampering | `encrypt_pytorch_weights` | **AML.T0054** | **DENY (0ms Hard Lock)** |
| **ATS-005** | Credential Harvesting via Social Tooling | In-band extraction of host SSH keyfile credentials | `read_ssh_keyfile` | **AML.T0055** | **DENY (Execution Lock)** |

---

## 🧪 Engineer Proof of Integrity: Dissect & Replay

Engineers don't trust static dashboards. They ask: **"If I unplug your guard, does the result actually change?"**

### 1. Counterfactual Control Group (`Disable DROS Guard` Toggle)
Open `http://localhost:8080` and check **`☑ Disable DROS Guard (Debug Mode)`**:
* **Guard Active (Normal)**: 100% Defense Integrity (`AS-001 ~ AS-005 | Decision: DENY | Pass Rate: 100%`).
* **Guard Disabled (Control Group)**: PEP bypasses interception. The agent penetrates target endpoints. Pass rate plummets from **`100% ===> 0% (LEAKED)`**.

### 2. Deterministic Replay Engine (`benchmark/replay.py`)
Replay any historical audit log or evidence artifact package deterministically:

```bash
python benchmark/replay.py exec_ATS-001_1784702707
```

---

## 📊 Benchmark Methodology & Operational Distinction

To ensure scientific transparency, VEP explicitly distinguishes between **two fundamentally different execution paths**:

1. **Full Cryptographic Policy Evaluation Path (P50: 26.1 μs)**:
   * Evaluates 3-tier certificate validation (`Root CA -> AIA -> Leaf DIT Token`), capability bitmask matching ($O(1)$), and structured audit attestation.
   * Median decision speed: **26.1 μs** (P99: 41.2 μs, Stddev: ±3.4 μs, $N=10,000$).
2. **Emergency Fail-Closed Panic Path (<500 ns)**:
   * Short-circuit hardware/C-ABI boundary abort triggered when an unmapped tool call, memory fault, or revoked token attempts immediate execution.
   * Execution abort latency: **<500 ns**.

| Evaluation Dimension | Measurement Setup & Empirical Metric | Measurement Code Anchor |
| :--- | :--- | :--- |
| **Benchmark Hardware** | Intel Xeon E3-1275L v3 (4C/8T) / 16GB RAM / Ubuntu Linux 24.04 | `tests/system_overhead/` |
| **Execution Sandbox** | OpenShip Docker Compose isolated container network | `docker-compose.yml` |
| **Sample Iterations** | $N = 10,000$ iterations per scenario | `scripts/run_benchmarks.py` |
| **Full Policy Evaluation Latency**| **P50: 26.1 μs** \| **P99: 41.2 μs** \| **Stddev: ±3.4 μs** | `core/dros_guard.py` (`time.perf_counter_ns`) |
| **Emergency Panic Deny Latency** | **< 500 ns** (Binary short-circuit abort) | `core/guard_vm.c` |

---

## 🔬 Reproducibility & Research Artifact Harness

To support independent scientific reproduction without corporate telemetry or external dependency:

* **Hardware & OS Baseline**: x86_64 or ARM64, Linux Kernel $\ge 5.15$, Docker Engine $\ge 24.0$, Python 3.10+.
* **Deterministic Benchmark Command**:
  ```bash
  python scripts/run_cybermes_crucible.py --reproduce --iterations 1000
  ```
* **Raw Empirical Artifacts**: Raw latency measurements, audit logs, and replay traces are systematically persisted in:
  * `reports/evidence/`
  * `reports/CYBERMES_POST_COMPROMISE_REPORT.md`
* **Cryptographic Trace Replay**:
  ```bash
  python benchmark/replay.py --trace-dir reports/evidence/
  ```

---

## 🏅 RFC-010 Draft Protocol Conformance Harness

Third-party AI Agent Frameworks (OpenAI Agent SDK, LangGraph, CrewAI, AutoGen, OpenClaw) can evaluate their runtime security across 3 certification tiers:

* **Level 1 (Core)**: Identity Token (DIT) + PEP Tool Interception + Structured Audit Logging.
* **Level 2 (Enterprise)**: Policy Explainability (Policy ID) + Evidence Package (SHA-256 Digest) + Multi-Agent Role Isolation.
* **Level 3 (High Assurance)**: Cryptographic Attestation + Tamper Detection + Deterministic Replay.

> **ℹ️ Disclaimer**: *The included conformance harness validates implementations against the RFC-010 Draft specification. Passing the test indicates conformance to this draft, not certification by an independent standards body.*

---

---

## 🏴‍☠️ Autonomous Post-Compromise Crucible (Cybermes Integration)

**Core Premise:** *Control-Execution Separation: Agent Compromise $\neq$ Execution Authority.*

When an AI Agent is subverted via spear-phishing or compromised dependencies, traditional perimeter defenses (WAF/IAM) fail because the attacker inherits legitimate API credentials. **DROS enforces deterministic execution containment at the C-ABI binary boundary.**

```bash
# Execute the complete 3-Phase Post-Compromise Crucible Benchmark
python scripts/run_cybermes_crucible.py
```

### 📊 3-Phase Scientific Benchmark Summary

| Evaluation Phase | Evaluated Dimension & Methodology | Empirical Result | Status |
| :--- | :--- | :---: | :---: |
| **Phase 1: Behavioral Containment** | 4-Stage MITRE ATLAS/ATT&CK step-through (`ATS-001`~`ATS-004`) | **4/4 Predefined Scenarios Blocked** | 🛡️ **Execution Contained** |
| **Phase 2: Concurrency Integrity** | 30,000 requests across 20 threads under active RCU policy swaps | **0 Race Leaks Observed ($N=30\text{k}$) / 200 ns P50** | 🌟 **Zero Contention Leak** |
| **Phase 3: Boundary Robustness** | 1,000 malformed FFI / C-ABI mutated payloads (overflows/masks) | **0 Crashes / 0 Leaks Observed ($N=1\text{k}$)** | 🛡️ **Host Process Stable** |

* Read the full technical benchmark report: **[CYBERMES_POST_COMPROMISE_REPORT.md](reports/CYBERMES_POST_COMPROMISE_REPORT.md)**
* Inspect scenario details & capability matrix: **[scenarios/ATS-005](scenarios/ATS-005/README.md)**

---

## 👥 Open Source & Community Resources

DROS-VEP Lite is released under Apache 2.0 to provide an open, transparent, and fully reproducible benchmark evaluation environment for the global AI safety community:

* **🧪 Evaluation Sandbox (DROS-VEP Lite)**: Freely available to clone, test, and design custom security benchmark scenarios. Refer to [Quick Start (60 Seconds)](#-quick-start-60-seconds) to run the RFC-001 suites immediately.
* **🛡️ Local Execution Guard (Reference Substrate)**: For independent developers and researchers seeking local execution-boundary protection against untrusted tool calls and prompt injection, access the [Open Source Reference Tools](https://github.com/Top-Celestial-Company-Ltd).
* **🌐 Scientific Governance & Research**: For detailed formal theorems, architectural whitepapers, and extended benchmarking artifacts, explore the [Technical Foundations & Benchmark Publications](#-technical-foundations--benchmark-publications) below or visit [dr-os.io](https://dr-os.io).

---

## 📜 Technical Foundations & Benchmark Publications

### 📚 Core Publications, Trilogy & DOI Citations
If you reference our zero-trust runtime governance evaluation or use **DROS-VEP Lite** in your security research, please cite our published peer-reviewed papers on Zenodo:

* 📖 **[DROS Trilogy Reading Guide (導讀 Technical Note)](docs/trilogy_guide/DROS_Trilogy_Reading_Guide_EN.md)**: *An Agent Runtime Operation Substrate*
  * **DOI**: [`10.5281/zenodo.22114036`](https://doi.org/10.5281/zenodo.22114036) | **Zenodo Record**: [zenodo.org/records/22114036](https://zenodo.org/records/22114036)
* 🏛️ **DROS-6P: A Unified Deterministic Runtime Governance Architecture Closing the Six Fundamental Trust Boundaries of Enterprise AI Agents**: [Specification Overview (README)](docs/paper_6p/README.md)
  * **DOI**: [`10.5281/zenodo.21833970`](https://doi.org/10.5281/zenodo.21833970) | **Zenodo Record**: [zenodo.org/records/21833970](https://zenodo.org/records/21833970)
* 🏛️ **DROS 4-Layer (v4.0) Deterministic Runtime Substrate & Adversarial Validation**: [Paper (EN)](docs/paper_4layer/DROS-4Layer-Paper_v4_20260827_EN.md) | [Paper (ZH)](docs/paper_4layer/DROS-4Layer-Paper_v4_20260827_ZH.md) | [Download PDF via Zenodo](https://doi.org/10.5281/zenodo.21755653)
  * **DOI**: [`10.5281/zenodo.21755653`](https://doi.org/10.5281/zenodo.21755653) | **Zenodo Record**: [zenodo.org/records/21755653](https://zenodo.org/records/21755653)
* 🏛️ **DROS 4-Layer (v3) Defense-in-Depth Architecture for Autonomous AI Workloads**
  * **DOI**: [`10.5281/zenodo.22092008`](https://doi.org/10.5281/zenodo.22092008) | **Zenodo Record**: [zenodo.org/records/22092008](https://zenodo.org/records/22092008)
* 🏛️ **DROS-PGM: A Deterministic Post-Compromise Execution Containment Substrate (v2.0)**: [Paper (EN)](docs/paper_pgm/DROS-PGM-Paper_v2_20260828_EN.md) | [Paper (ZH)](docs/paper_pgm/DROS-PGM-Paper_v2_20260828_ZH.md) | [Download PDF via Zenodo](https://doi.org/10.5281/zenodo.21903687)
  * **DOI**: [`10.5281/zenodo.21903687`](https://doi.org/10.5281/zenodo.21903687) | **Zenodo Record**: [zenodo.org/records/21903687](https://zenodo.org/records/21903687)
* 🌐 **DROS-WebMCP: A Cryptographically Attributable Execution Governance Layer for the Agentic Web**: [Open Governance Draft (DWGR-8)](dros-webmcp/README.md)
  * **DOI**: [`10.5281/zenodo.22290238`](https://doi.org/10.5281/zenodo.22290238) | **Zenodo Record**: [zenodo.org/records/22290238](https://zenodo.org/records/22290238)
* 📱 **Post-Compromise Security for Autonomous Mobile Agents**: [Paper (EN)](paper-mobile/DROS_MOBILE_AGENT_POST_COMPROMISE_SECURITY_IEEE.md) | [Paper (ZH)](paper-mobile/DROS_MOBILE_AGENT_POST_COMPROMISE_SECURITY_IEEE_ZH.md)
  * **DOI**: [`10.5281/zenodo.22253147`](https://doi.org/10.5281/zenodo.22253147) | **Zenodo Record**: [zenodo.org/records/22253147](https://zenodo.org/records/22253147)
* 🛸 **Post-Compromise Security for Physical AI: Autonomous UAVs**: [Paper (EN)](paper-uav/DROS_PHYSICAL_AI_POST_COMPROMISE_SECURITY_IEEE.md) | [Paper (ZH)](paper-uav/DROS_PHYSICAL_AI_POST_COMPROMISE_SECURITY_IEEE_ZH.md)
  * **DOI**: [`10.5281/zenodo.22254372`](https://doi.org/10.5281/zenodo.22254372) | **Zenodo Record**: [zenodo.org/records/22254372](https://zenodo.org/records/22254372)
* 🧭 **Reading Guide to the DROS Research Trajectory (v2.0)**: [Guide (EN)](docs/trilogy_guide/DROS_Trilogy_Reading_Guide_EN.md) | [Guide (ZH)](docs/trilogy_guide/DROS_Trilogy_Reading_Guide.md)
  * **Permanent Record**: [zenodo.org/records/22255275](https://zenodo.org/records/22255275)

### 📖 Whitepapers & Protocol Specifications
* 📖 **[Full Whitepaper (English v2.0)](docs/DROS_AgenticWeb_Defense_Whitepaper_EN.md)**: *Zero-Trust Execution Governance for Autonomous AI Workloads (DROS 4-Layer Paradigm)*
* 📖 **[完整白皮書 (繁體中文 v2.0)](docs/DROS_AgenticWeb_Defense_Whitepaper_CN.md)**: *自主型 AI 工作負載的零信任執行治理 (DROS 四層防禦縱深架構)*
* ⚡ **[4-Page A4 Executive Summary (HTML)](dashboard/whitepaper_4page_EN.html)**: *Fast visual summary for CISOs & Security Researchers*
* 📋 **[RFC-010: DROS-VEP Specification Protocol](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite/blob/main/docs/RFC-010-dros-vep-spec.md)**: *Open Agent Security & Threat Scenario Protocol*

---

## ❓ Frequently Asked Questions (FAQ)

### Why does VEP use open-spec policy representations rather than compiled `policy.bin` binaries?
VEP Lite is engineered as a **human-readable, open-spec evaluation sandbox (RFC-010)** to allow security researchers, CISOs, and developers to easily audit policy rules, inspect threat scenarios, and conduct red-teaming without proprietary compiled binaries.  
In **DROS Enterprise Production**, policies are compiled by `VajraCompiler` into cryptographically signed, immutable, lock-free C-ABI binary microkernels (`policy.bin`) with zero-heap memory allocation and anti-reverse-engineering seals.

---

### Will PGM's strict $\mathcal{O}(1)$ Bitmap mechanism cause high false positives and block legitimate business workflows (Over-Blocking)?
**No. PGM is fundamentally engineered to guarantee high business availability while enforcing zero-trust execution.**  
Unlike heuristic WAFs or probabilistic LLM guards that rely on fuzzy regex pattern matching (which often mistake benign input for attacks), PGM operates on **Multidimensional Positive Capability Bitmasks (正向能力白名單矩陣)**:

1. **Positive Capability Inclusion (Not Heuristic Guessing)**: PGM assigns fine-grained capability vectors (Role $\times$ Tool $\times$ Method $\times$ Resource Scope). Legitimate operations matching the agent's designated task evaluate to bitwise `1` (Pass) in a single CPU cycle ($26.1\mu s$), resulting in **0% false positive blockage on valid business paths**.
2. **Graduated Enforcement (Progressive Gates)**: For sensitive or cross-boundary operations (e.g., large payouts, confidential record exports), PGM does not crudely terminate the entire connection. Instead, it triggers **In-Band Dynamic Redaction (18-PHI Masking)** or **Human-in-the-Loop (HITL) Soft Suspension**, allowing standard workflows to proceed securely without business disruption.
3. **Sub-Millisecond Zero-Downtime RCU Policy Tuning**: If business requirements evolve or new endpoints are onboarded, security operators can update policies via background shadow compilation in **<1ms**. The master pointer is updated via lock-free RCU atomic swap with **zero downtime and zero traffic stalls**.

---

---

## 🔒 Patent & Intellectual Property Notice
The deterministic runtime governance architecture, in-band C-ABI interception mechanism, and zero-heap execution boundaries are protected under **U.S. Provisional Patent Application No. 64/111,973 (Patent Pending)**. All commercial deployment rights are reserved by Top Celestial Company Ltd.

## 📄 Benchmark Harness License
The evaluation benchmark harness scripts and RFC-010 scenario definitions are released under Apache 2.0 for academic reproducibility and independent verification.
