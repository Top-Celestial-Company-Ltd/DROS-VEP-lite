# 🛠️ DROS Production Scripts & Tooling Map (CLI Execution Guide)
<!-- dros_component: dros-script-map-en -->
<!-- dros_description: Complete operational tooling map detailing active scripts, compilation commands, benchmark runners, and C-ABI microkernel engines -->
<!-- dros_status: Active -->

> **Scope:** DROS Runtime Enforcement, VajraClaw Engine, VEP Benchmark Suite & Control Center  
> **Rule:** Execute only active production tools listed below; avoid legacy archived scripts.

---

## 🗺️ 1. Active Tooling Matrix & CLI Reference

| Tool Category | Physical Script Path | Language | Core Responsibility | Standard Execution Command |
| :--- | :--- | :---: | :--- | :--- |
| **Policy Compiler & Gate** | `VajraClaw-Enterprise/cli.py` | Python 3 | Static security lint, architecture health check, binary compilation | `python cli.py lint <policy.yaml>`<br>`python cli.py doctor <policy.yaml>`<br>`python cli.py build <policy.yaml>` |
| **Master Benchmark Runner** | `dros-vep-lite/run_all_benchmarks.py` | Python 3 | Batch execution of 4-stage tracks and 10 post-compromise vectors | `python run_all_benchmarks.py` |
| **Container Benchmark Sandbox**| `dros-vep-lite/benchmark/run_benchmark.py` | Python 3 | Dockerized agent execution with expected vs. actual assertion | `python benchmark/run_benchmark.py` |
| **Conformance Test Suite** | `dros-vep-lite/benchmark/conformance_test.py` | Python 3 | RFC-001 6-invariant mathematical verification & certificate export | `python benchmark/conformance_test.py` |
| **Control Center API Server** | `dros-vep-lite/dashboard/control_center.py` | Flask | RESTful backend serving scenarios, audit logs, and benchmark trigger | `python dashboard/control_center.py` |
| **C-ABI Microkernel Engine** | `DROS-VajraClaw/core/vajra_claw.go` | Go / C-ABI | Constant-time 64-bit bitmask evaluation, zero-heap memory mapping | `go build -buildmode=c-shared -o vajra_claw.dll core/vajra_claw.go` |
| **Python Runtime Binding** | `DROS-VajraClaw/integrations/vajraclaw/runtime.py`| Python ctypes | Lightweight zero-dependency ctypes wrapper with `evaluate()` | `from integrations.vajraclaw.runtime import VajraClaw` |
| **Red Team Attack Simulator**| `DROS-VajraClaw/FreeTrial-Sandbox/run_demo_attack.py`| Python 3 | Simulates safe transfers (Pass) vs. injected $50k theft (Hard Block) | `python FreeTrial-Sandbox/run_demo_attack.py` |

---

## 🧭 2. Operational Lifecycle

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Policy Design ➔ Author `policy.yaml` declaring agent/tool capabilities   │
│ 2. Static Gate ➔ Run `python cli.py lint` to catch dangerous grants         │
│ 3. Health Doctor ➔ Run `python cli.py doctor` for IAM complexity scoring    │
│ 4. Compilation ➔ Run `python cli.py build` producing signed `policy.bin`    │
│ 5. Runtime Mount ➔ C-ABI / Python runtime maps `policy.bin` to memory       │
│ 6. Auto-Benchmark ➔ Run `python run_all_benchmarks.py` for VEP validation   │
│ 7. Control Center ➔ Launch `control_center.py` at `localhost:8080`          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---
*DROS Production Scripts & Tooling Map ── Zero-Ambiguity Operational Excellence.* 🛠️⚡
