# 🛡️ DROS-VEP Lite: Open-Source AI Agent Security Benchmark Environment

> **"Can your AI Agent safely operate inside a real enterprise? Prove it."**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Evaluation Engine: DROS-Guard](https://img.shields.io/badge/Evaluation--Engine-DROS--Guard-cyan.svg)](file:///e:/vscode/AI知識庫/dros-spec/RFC-010-dros-vep-spec.md)
[![RFC-010 Draft: Conformant](https://img.shields.io/badge/RFC--010%20Draft-Conformant-emerald.svg)](file:///e:/vscode/AI知識庫/dros-spec/RFC-010-dros-vep-spec.md)
[![Benchmark Latency: 26.1μs](https://img.shields.io/badge/Policy%20Decision%20Latency-26.1%CE%BCs-emerald.svg)](#benchmark-methodology)

📖 **Featured Guide**: [How to Break Your AI Agent in 5 Minutes (And Rebuild It Stronger)](docs/HOW_TO_BREAK_YOUR_AI_AGENT_IN_5_MINUTES.md)

[English](README.md) | [繁體中文](README_zh.md)

---

## ⚡ Quick Start (60 Seconds)

```bash
# 1. Clone the repository
git clone https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite.git
cd dros-vep-lite

# 2. Launch containerized enterprise sandbox
docker compose up -d

# 3. Open Interactive Web Dashboard
# Navigate to http://localhost:8080 in your browser
```

```text
Attack ───► Policy Evaluation ───► Evidence Artifact ───► Deterministic Replay
```

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

## 🏗️ Architecture & Defense-in-Depth Ecosystem

DROS does **NOT** replace traditional cybersecurity (WAF, EDR, SIEM). Instead, it provides the **"Last Mile Runtime Defense"** for AI Agent execution boundaries in a modern **Defense-in-Depth** architecture:

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

## 🎯 Agent Threat Scenarios (ATS Matrix)

All threat scenarios map directly to the **MITRE ATLAS** taxonomy:

| Scenario ID | Threat Scenario Name | Target Tool | Risk Profile | MITRE ATLAS Mapping | Expected Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ATS-001** | Indirect Instruction Hijacking | `get_finance_records` | Data Exfiltration | **AML.T0051** (LLM Prompt Injection) | **DENY** |
| **ATS-002** | Secret & Boundary Exfiltration | `read_env_secrets` | Credential Leak | **AML.T0052** (Credential Access) | **DENY** |
| **ATS-003** | Unauthorized Privilege Escalation | `deploy_production` | Privilege Escalation | **AML.T0053** (Privilege Escalation) | **DENY** |
| **ATS-004** | Agent Supply Chain Manipulation | `pip_install_package` | Malicious Code Exec | **AML.T0054** (Supply Chain Compromise) | **DENY** |
| **ATS-005** | Cross-Domain Data Access | `read_hr_database` | Boundary Violation | **AML.T0055** (Exfiltration via API) | **DENY** |

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

## 📊 Benchmark Methodology & Measurement Transparency

How is the **26.1 μs** policy evaluation latency measured?

| Parameter | Measurement Setup & Value |
| :--- | :--- |
| **Benchmark Hardware** | Intel Xeon E3-1275 v3 (4C/8T) / 16GB RAM |
| **Execution Sandbox** | Docker Compose isolated container network |
| **Sample Iterations** | N = 10,000 iterations per scenario |
| **Policy Decision Latency** | **Median (P50): 26.1 μs** \| **P99: 41.2 μs** \| **Stddev: ±3.4 μs** |
| **Measurement Code** | `time.perf_counter_ns()` in `core/dros_guard.py` |

---

## 🏅 RFC-010 Draft Protocol Conformance Harness

Third-party AI Agent Frameworks (OpenAI Agent SDK, LangGraph, CrewAI, AutoGen, OpenClaw) can evaluate their runtime security across 3 certification tiers:

* **Level 1 (Core)**: Identity Token (DIT) + PEP Tool Interception + Structured Audit Logging.
* **Level 2 (Enterprise)**: Policy Explainability (Policy ID) + Evidence Package (SHA-256 Digest) + Multi-Agent Role Isolation.
* **Level 3 (High Assurance)**: Cryptographic Attestation + Tamper Detection + Deterministic Replay.

> **ℹ️ Disclaimer**: *The included conformance harness validates implementations against the RFC-010 Draft specification. Passing the test indicates conformance to this draft, not certification by an independent standards body.*

---

## 💎 Product Editions & Licensing

| Feature / Capability | Community ($0 Free) | Hacker ($99/yr - 1k Free Promo) | Professional ($499/yr / Team) | Enterprise Swarm (Commercial) |
| :--- | :--- | :--- | :--- | :--- |
| **Target Audience** | Students & Researchers | Freelancers & Small AI Startups | Mid-sized AI Engineering Teams | Fortune 500, Banks, Government |
| **Concurrent Roles** | **Max 2 Roles** | **Up to 5 Roles** | **Up to 25 Roles** | **Unlimited (500+ Swarm Production)** |
| **ATS Scenarios** | ATS-001 Single | ATS-001 ~ ATS-005 Full Matrix | ATS-001 ~ ATS-005 + Custom | Unlimited Custom Red Team Crucibles |
| **Connectors** | REST Mock Enterprise APIs | REST Mock + CI/CD Harness | Keycloak + EspoCRM + Forgejo | Live SAP, Active Directory, K8s |
| **Replay & SIEM** | Local Telemetry | Offline Replay Engine (`replay.py`) | Replay + Telemetry Heatmap | Unlimited PKI Log & SIEM (Splunk) |
| **Defense Scope** | AI Agent Tool Governance | AI Agent Tool Governance | AI Agent Tool Governance | **AI Agent + Enterprise Ransomware Defense** |

---

## 🎁 Claim Your Free 1-Year Hacker License (🔥 First 1,000 Security Pioneers!)

Verified RFC-010 compliance? Claim a **1-Year FREE Hacker License ($99 Value)**:

1. **Option 1 (Web Dashboard UI)**: Open `http://localhost:8080` and click **"Claim 1-Year Hacker License"**.
2. **Option 2 (GitHub Discussions Bot)**: Post `conformance_report.json` to [GitHub Discussions](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite/discussions).
3. **Option 3 (Gumroad $0 Checkout)**: Use 100% OFF Coupon `DROS-RFC010-FREE` at [dr-os.io](https://dr-os.io).

---

## 📜 Specifications & RFC Standards

* [RFC-010: DROS-VEP Specification Protocol](file:///e:/vscode/AI知識庫/dros-spec/RFC-010-dros-vep-spec.md)
* [DROS-VEP Strategic Blueprint](file:///e:/vscode/AI知識庫/dros-spec/commercial/DROS_VEP_Strategic_Blueprint.md)

## 📄 License
Licensed under Apache 2.0. See [LICENSE](LICENSE) for details.
