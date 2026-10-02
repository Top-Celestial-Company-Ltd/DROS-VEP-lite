# README Claim-to-Governance Crosswalk (VEP 2.0)

**Document Identifier:** `README_CLAIM_CEILING_CROSSWALK_20261002`  
**Execution Timestamp:** `2026-10-02T08:15:00+08:00`  
**Governance Protocol:** READ-ONLY / AUDIT-MAPPING  
**Workspace:** `E:\vscode\AI知識庫\DROS-VEP\Work-PublicHygiene`  
**Parent Governance Documents:**
- `docs/evidence/CLAIM_REGISTER.md`
- `reports/evidence/reconciliation/VEP_2_FINAL_RELEASE_GATE_20261001.md`
- `reports/evidence/reconciliation/CLAIM_CLOSURE_GATE_20261001.md`
- `reports/evidence/reconciliation/SCOPE_DOWN_WORDING_MATRIX_20261001.md`

---

## 1. Overview & Purpose

This crosswalk provides an explicit, 1-to-1 verifiable mapping between public-facing statements in `README.md` / `README_zh.md` and the underlying formal governance registers (`CLAIM_REGISTER.md` and `VEP_2_FINAL_RELEASE_GATE_20261001.md`).

Its purpose is to index and bound public-facing statements against approved governance decisions. This document **does not establish new claims**, does not expand existing claims, and does not alter the formal status definitions codified in the parent registers.

---

## 2. Claim-to-Governance Mapping Matrix

| Surface / Section | Public Wording / Visual Presentation | Formal Register ID | Governed Release Status | Safe Scope & Epistemic Ceiling | Primary Governance Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Top Badges** | `Deterministic Gate: C-ABI FFI` | `CLAIM-02`<br>`PUB-01` | **A** (`CLOSED_WITH_SCOPE`)<br>**B** (`CLOSED_SCOPE_DOWN`) | In-process native C-ABI capability bitmask lookup (<1.0 μs pure PDP; ~7.8 μs harness). Historical full policy evaluation aggregate reported separately. Does not claim zero-latency across external IPC/RPC/Python dispatch. | `docs/evidence/CLAIM_REGISTER.md` (§2 CLAIM-02)<br>`reports/evidence/reconciliation/VEP_2_FINAL_RELEASE_GATE_20261001.md` (Table 3) |
| **Top Badges** | `Benchmark Scope: Declared Baseline` | `PUB-01`<br>`PUB-02` | **B** (`CLOSED_SCOPE_DOWN`)<br>**D** (`NARROWED_NO_EXPERIMENT`) | Benchmarks represent historical declared baseline runs under registered harness environments, not real-time or constant-under-load guarantees. | `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md`<br>`reports/evidence/reconciliation/VEP_2_FINAL_RELEASE_GATE_20261001.md` (Table 3) |
| **Open Source Scope** | Evaluation harness & benchmark protocols under RFC-010 | `RFC-010` Specification | *Non-claim open-spec artifact* | Benchmark harness, protocol specs, and validation fixtures are open-spec. Kernel internals and proprietary runtime implementations are decoupled. | `docs/specifications/RFC-010-Multi-Substrate-Execution-Governance.md` |
| **FAQ 2 (Performance)** | Deterministic bitmask lookup vs. full evaluation latency | `CLAIM-02`<br>`PUB-01` | **A** (`CLOSED_WITH_SCOPE`)<br>**B** (`CLOSED_SCOPE_DOWN`) | Constant-time bitmask operations are bounded to pure PDP logic; full policy evaluation and audit dispatch latency is measured separately under declared Xeon E3 baseline ($P50 = 26.1\ \mu\text{s}$, $P99 = 41.2\ \mu\text{s}$). | `docs/evidence/CLAIM_REGISTER.md` (§2 CLAIM-02)<br>`reports/evidence/reconciliation/SCOPE_DOWN_WORDING_MATRIX_20261001.md` |
| **Mobile Section (§5)** | Android Multi-Agent Security Harness | `PUB-06`<br>`TMC-C01` ~ `TMC-C04`<br>`TMC-C07` | **B** (`CLOSED_SCOPE_DOWN`)<br>**A** (`CLOSED_WITH_SCOPE`)<br>**D** (`NARROWED_NO_EXPERIMENT`) | Scoped to declared AVD/emulator test harness. Negative boundaries explicitly disclaim Android-wide, OS-level, or whole-device mediation (`PUB-06`). Downstream oracle claim retracted; bounded to app fixture marker (`TMC-C07`). | `reports/evidence/reconciliation/TMC_C07_INDEPENDENT_O1_FEASIBILITY_20261001.md`<br>`reports/evidence/reconciliation/VEP_2_FINAL_RELEASE_GATE_20261001.md` (Table 3) |
| **Host/Kernel Section (§4)** | OS Process Identity & Process Isolation | `CLAIM-07`<br>`PUB-04` | **B** (`CLOSED_SCOPE_DOWN`) | Experimentally validated on native Windows Named Pipe (`GetNamedPipeClientProcessId`). Linux UDS `SO_PEERCRED` is scoped as future extension; universal equivalence explicitly disclaimed. | `reports/evidence/reconciliation/CLAIM07_LINUX_SCOPE_NECESSITY_20261001.md`<br>`docs/evidence/CLAIM_REGISTER.md` (§2 CLAIM-07) |
| **Drone / Cyber-Physical (§6)** | Drone MAVLink Substrate Evaluation | `S0`, `S1`, `S2-D` | **A** (`CLOSED_WITH_SCOPE`) | Scoped to declared SITL/HITL UDP port mediation (14540 $\to$ 14580) and host perimeter packet filtering. No whole-vehicle airworthiness or safety-of-flight certification is claimed. | `reports/evidence/reconciliation/VEP_2_FINAL_RELEASE_GATE_20261001.md` (Table 3) |
| **Reproducibility Guide** | `REPRODUCIBILITY.md` execution procedures | `PUB-02`<br>`PUB-03` | **D** (`NARROWED_NO_EXPERIMENT`)<br>**B** (`CLOSED_SCOPE_DOWN`) | Reproducibility applies strictly to documented scripts and environments (`python vep.py replay`). Uses relative paths only; sanitized from developer-local paths. | `REPRODUCIBILITY.md`<br>`reports/evidence/reconciliation/VEP_2_FINAL_RELEASE_GATE_20261001.md` (Table 3) |

---

## 3. Governance Invariants Attestation

1. **NO_CLAIM_PROMOTION**: All public descriptions match or stay strictly below the formal statuses in `CLAIM_REGISTER.md` and `VEP_2_FINAL_RELEASE_GATE_20261001.md`.
2. **SANITIZED_REVIEWED_PUBLIC_SURFACES**: The reviewed public surfaces (`README.md`, `README_zh.md`, `REPRODUCIBILITY.md`, `DROS_VEP_TEST_CATALOG_v0.1.0_ZH.md`, `DROS_VEP_v5_Protocol.md`, `DROS_VEP_v6_Protocol.md`, `DROS_AgenticWeb_Defense_Whitepaper_CN.md`, `DROS_AgenticWeb_Defense_Whitepaper_EN.md`, `DROS_VEP_Strategic_Blueprint_CN.md`) contain no confirmed developer-local file paths after Task A remediation.
3. **NEGATIVE_BOUNDARIES_PRESERVED**: All negative boundary disclaimers (e.g., non-assertion of Android-wide coverage, non-assertion of whole-vehicle airworthiness, Win32-only OS attribution scope) remain fully intact.
