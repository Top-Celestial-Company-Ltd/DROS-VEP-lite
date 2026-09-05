# 🏢 DROS Enterprise Operations & Architecture Guide
<!-- dros_component: dros-enterprise-guide-en -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md, RFC-001-VEP-Execution-Governance-Spec.md] -->
<!-- dros_description: Comprehensive enterprise operational manual covering topologies, deployment SOPs, graduated eviction state machine, forensics, and emergency lockdown -->
<!-- dros_status: Active -->

> **Applicable Products:** DROS Enterprise Commercial SKU 1--4 (Production-Ready)  
> **Target Audience:** CISOs, DevOps / SecOps Engineers, Platform Architects, Compliance Officers

---

## 🧭 Table of Contents
1. **Enterprise Runtime Topologies (Sidecar Gateway vs. In-Process FFI Gate)**
2. **VajraCLI Enterprise Toolchain (`cli.py: lint / doctor / build`)**
3. **Policy Configuration Specification (`policy.yaml` / Bitmask Mapping)**
4. **Graduated Eviction & Physical Hard Kill State Machine**
5. **DROS-VEP Proving Ground Console Guide (UI Switches & Telemetry)**
6. **B2B Multi-Enterprise PKI Federation (3-Tier ECDSA-P256 Trust Chain)**
7. **Immutable Merkle Audit Forensics (`audit.jsonl` / EU AI Act Export)**
8. **Operational CLI Cheat-Sheet**
9. **High Availability & Deterministic State Reset ($\Delta S \equiv 0$)**
10. **Troubleshooting & Emergency Lockdown SOP**

---

## 1. Enterprise Runtime Topologies

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DROS Enterprise Production Topologies                  │
└─────────────────────────────────────────────────────────────────────────────┘

  [ Topology A: Sidecar / API Gateway ]          [ Topology B: In-Process C-ABI Gate ]
   Target: K8s / Microservices Swarm              Target: Ultra-low latency (<5μs) / Edge
   
   [ Agent Pod (LangChain / AutoGen) ]         [ Agent Process (Python / Node / Go) ]
                 │                                                │
       (HTTP / gRPC / Unix Socket)                                │ (Direct Native FFI)
                 ▼                                                ▼
   ┌───────────────────────────────┐           ┌────────────────────────────────────┐
   │ 🛡️ DROS-Guard Gateway Daemon   │           │ ⚡ dros_pgm_core.so / .dll (C-ABI) │
   │  - 64-bit Bitmask PDP/PEP     │           │  - Zero-heap bitmask evaluation    │
   │  - Sliding window eviction    │           │  - Atomic RCU state pointer swap   │
   │  - Continuous SHA-256 Merkle  │           │  - In-process Fail-Closed block    │
   └──────────────┬────────────────┘           └─────────────────┬──────────────────┘
                  │                                              │
                  ▼                                              ▼
   [ Enterprise ERP / DB / OS Syscall ]        [ Physical Filesystem / Net / APIs ]
```

---

## 2. Graduated Eviction State Machine

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   DROS Graduated Eviction Decision Matrix                   │
├─────────────────┬───────────────────────────────────┬───────────────────────┤
│ Tier Level      │ Trigger Conditions                │ Defensive Action      │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 1. Soft Deny    │ Isolated violation (LLM hallucination)│ DENY call, return error│
│                 │ without fatal escape vectors      │ for agent self-repair │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 2. Quarantine   │ Sliding window threshold exceeded │ RCU switch to Read-   │
│                 │ (e.g., 3 violations in 10s)       │ Only sandbox + alert  │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 3. Hard Kill    │ Fatal exploit (Direct Syscall,    │ Send SIGKILL to abort │
│                 │ Audit tampering, PKI forgery)     │ process, purge state, │
│                 │ or persistent breach attempts     │ blacklist W3C DID     │
└─────────────────┴───────────────────────────────────┴───────────────────────┘
```

---

## 3. Operational CLI Reference

| Category | Command | Description |
| :--- | :--- | :--- |
| **Static Lint** | `python cli.py lint <policy.yaml>` | Scan for dangerous grants, unreachable tools, unused caps |
| **Doctor Check** | `python cli.py doctor <policy.yaml>` | Assess IAM complexity (A--D) and rule conflict risks |
| **Deterministic Build**| `python cli.py build <policy.yaml> -o policy.bin` | Compile into signed binary signature with SHA-256 hash |
| **Master Benchmark** | `python run_all_benchmarks.py` | Execute all 4 test tracks and 10 post-compromise vectors |
| **Launch Console** | `python dashboard/control_center.py` | Start web console at `http://localhost:8080` |

---
*DROS Enterprise Operations Guide ── Deterministic Governance for Mission-Critical AI.* 🏢🛡️⚡
