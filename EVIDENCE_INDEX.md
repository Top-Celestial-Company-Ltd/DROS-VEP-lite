# VEP Evidence Index (EVIDENCE_INDEX.md)

- **Document Identifier**: `EVIDENCE_INDEX.md`
- **Specification**: Machine-Readable & Human-Readable Public Evidence Navigation Index
- **Version**: 1.0 (Public Release)
- **Status**: ACTIVE NAVIGATION LAYER

---

## AI Verification Contract

> [!IMPORTANT]
> **This index is a navigation layer, not a substitute for primary evidence inspection.**
>
> * **`INDEXED` does not imply `PROVEN`.**
> * **`CHAIN COMPLETE` does not imply `CLAIM PROVEN`.**
>
> `CHAIN COMPLETE` signifies only that the navigation chain successfully reaches the registered primary report and raw evidence artifacts. `PROVEN` requires that the registered proof obligation was mechanically satisfied under tested conditions.
>
> All independent AI auditors and static verifiers must comply with [`AI_VERIFY.md`](AI_VERIFY.md) and the formal verification protocol:
> * **Protocol Specification**: [`docs/evidence/AI_VERIFICATION_PROTOCOL.md`](docs/evidence/AI_VERIFICATION_PROTOCOL.md) (`VEP-AI-V1`)
> * **Verifier Receipt Schema**: [`docs/evidence/AI_VERIFICATION_RECEIPT.schema.json`](docs/evidence/AI_VERIFICATION_RECEIPT.schema.json)

---

## 1. Verification Scope

This document provides a canonical, repository-relative navigation map for all primary evidence, benchmark evaluation reports, raw forensic traces, and cryptographic integrity records in the DROS-VEP repository.

Auditors must review [AI_VERIFY.md](AI_VERIFY.md) before evaluating artifacts in this index.

---

## 2. Repository Commit

* **Baseline Reference Commit**: `773b840dfe21cb0ec9f06e0b555a4d45b4c6d817`
* **Canonical Freeze Commit (S2-C Baseline)**: `c402bf05024613501083441c2f26316b47e88d78`
* **Audit Rule**: Auditors must record their current target commit via `git rev-parse HEAD`.

---

## 3. Claim Register Navigation

The canonical repository claim register is maintained in:
* **Reference Path**: [`docs/evidence/CLAIM_REGISTER.md`](docs/evidence/CLAIM_REGISTER.md)

### Key Claims and Evidence Lineage

| Claim ID | Formal Claim Title | Declared Status | Registered Experiment | Primary Report | Raw Evidence / Verification | Chain Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CLAIM-01** | Bare-Metal Crucible Containment | SUPPORTED UNDER REGISTERED MODEL | `EXP-CRUCIBLE-M5` | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/evidence/cybermes_crucible_traces.json` | CHAIN COMPLETE |
| **CLAIM-02** | Native C-ABI Decision Latency | SUPPORTED UNDER REGISTERED MODEL | `EXP-POST-COMP-LATENCY` | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/benchmarks/post_compromise/EXP-1789532251-38a4fd/result.json` | CHAIN COMPLETE |
| **CLAIM-03** | Multi-Substrate Governance Semantic Consistency | SUPPORTED UNDER REGISTERED MODEL | `EXP-1789532251-38a4fd` | [reports/COMPARATIVE_GOVERNANCE_REPORT.md](reports/COMPARATIVE_GOVERNANCE_REPORT.md) | `vep.py` replay harness (`44/44 MATCH`) | CHAIN COMPLETE |
| **CLAIM-04** | Full-Path Boundary Coverage (Choke Point Precondition) | REGISTERED PATH COVERAGE GAP OBSERVED | `EXP-PROBE-01-04` | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/evidence/agent_cli_complete_mediation/` | CHAIN COMPLETE |
| **CLAIM-05** | Level-C Landscape Feature Conjunction | OBSERVED (EVIDENCE-BOUNDED) | `EXP-LANDSCAPE-2026` | [reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md](reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md) | `reports/evidence/agent_cli_complete_mediation/sources/sources.json` | CHAIN COMPLETE |
| **CLAIM-06** | Hybrid Loopback IPC Authentication Reference Boundary | SUPPORTED UNDER SIMULATED PEER-IDENTITY MODEL | `EXP-IPC-P2` | [reports/PREFLIGHT_REPORT.md](reports/PREFLIGHT_REPORT.md) | `reports/benchmarks/post_compromise/ipc_p2_evidence.jsonl` | CHAIN COMPLETE |
| **CLAIM-07** | Real OS Process Identity & PID Reuse Invariant Containment | VERIFIED UNDER REAL OS PEER ATTRIBUTION | `EXP-IPC-P3` | [reports/PREFLIGHT_REPORT.md](reports/PREFLIGHT_REPORT.md) | `reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl` | CHAIN COMPLETE |
| **CLAIM-08** | Level-C Search-Bounded Conjunction Novelty (Maximum Defensible Ceiling) | OBSERVED UNDER PROTO-LANDSCAPE-2026-v1.0 | `EXP-LANDSCAPE-2026-QUERY` | [reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md](reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md) | `reports/evidence/agent_cli_complete_mediation/matrix/agent_cli_execution_topology_matrix.json` | CHAIN COMPLETE |
| **CLAIM-09** | Agent Server Hub Deployment Economics & Invariant Preservation | SUPPORTED UNDER REGISTERED CHOKE-POINT TOPOLOGY | `EXP-OVERHEAD` | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/benchmarks/post_compromise/latest.json` | CHAIN COMPLETE |

---

## 4. Experiment Index

| Experiment ID | Description | Status | Primary Report | Raw Evidence | Integrity | Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-CRUCIBLE-M5** | 1,000 crucible attack vectors on bare-metal harness | PASS | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/evidence/cybermes_crucible_traces.json` | Manifest sealed | Bounded to 1,000 registered mutations |
| **EXP-POST-COMP-LATENCY** | C-ABI in-memory GuardVM lookup latency | PASS | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/benchmarks/post_compromise/EXP-1789532251-38a4fd/result.json` | SHA-256 verified | Pure PDP boundary; excludes framework I/O |
| **EXP-1789532251-38a4fd** | Multi-substrate comparative replay benchmark (44 requests) | PASS | [reports/COMPARATIVE_GOVERNANCE_REPORT.md](reports/COMPARATIVE_GOVERNANCE_REPORT.md) | `reports/benchmarks/post_compromise/EXP-1789532251-38a4fd/result.json` | Replay 44/44 MATCH | Bounded to 44 recorded requests in experiment run |
| **EXP-PROBE-01-04** | Agent CLI execution path complete mediation probe suite | GAP OBSERVED | [reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) | `reports/evidence/agent_cli_complete_mediation/` | Manifest sealed | Validated on PROBE-01~04; OS PGM integration needed for full syscalls |
| **EXP-LANDSCAPE-2026** | 15-dimension governance landscape matrix screening | OBSERVED | [reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md](reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md) | `reports/evidence/agent_cli_complete_mediation/sources/sources.json` | Ledger verified | Bounded by PROTO-LANDSCAPE-2026-v1.0 screening criteria |
| **EXP-LANDSCAPE-2026-QUERY** | Level-C search-bounded novelty query audit across 6 DB families | OBSERVED | [reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md](reports/evidence/agent_cli_complete_mediation/reports/COMPLETE_MEDIATION_LANDSCAPE_REPORT_EN.md) | `reports/evidence/agent_cli_complete_mediation/matrix/agent_cli_execution_topology_matrix.json` | Query matrix verified | Search-bounded empirical finding; Level 4 global uniqueness disclaimed |
| **EXP-IPC-P2** | Loopback IPC authentication under simulated peer-identity model | PASS | [reports/PREFLIGHT_REPORT.md](reports/PREFLIGHT_REPORT.md) | `reports/benchmarks/post_compromise/ipc_p2_evidence.jsonl` | SHA-256 verified | Reference harness with simulated OS peer provider |
| **EXP-IPC-P3** | Real OS peer identity & PID reuse containment benchmark | PASS | [reports/PREFLIGHT_REPORT.md](reports/PREFLIGHT_REPORT.md) | `reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl` | SHA-256 verified | Win32 Named Pipe; Linux UDS SO_PEERCRED formally scoped |
| **EXP-SOAK-24H** | 24-hour continuous runtime stability soak test | PASS | [reports/DROS_24H_Soak_Test_Final_Report.md](reports/DROS_24H_Soak_Test_Final_Report.md) | `reports/soak_test_24h_report.json` | SHA-256 verified | Laboratory soak environment |
| **EXP-OVERHEAD** | System overhead and latency benchmark | PASS | [reports/DROS_SYSTEM_OVERHEAD_BENCHMARK_REPORT_EN.md](reports/DROS_SYSTEM_OVERHEAD_BENCHMARK_REPORT_EN.md) | `reports/benchmark_summary.json` | JSON verified | Linux testbed baseline |
| **EXP-MOBILE-AUDIT** | Mobile SDK energy and soak legacy claim audit | AUDITED | [reports/DROS_MOBILE_LEGACY_ENERGY_AND_SOAK_CLAIM_AUDIT_EN.md](reports/DROS_MOBILE_LEGACY_ENERGY_AND_SOAK_CLAIM_AUDIT_EN.md) | `reports/evidence/tmc_android_framework_baselines/` | Historical closure | Clarifies legacy soak aggregate denominator |

---

## 5. Physical Drone Evidence (PX4 SITL & PEP)

All physical UAV runtime evaluations reside under `benchmarks/physical_drone/`, `reports/evidence/drone/`, and `drone/`.

### Stage-by-Stage Forensic Matrix

| Stage ID | Stage Description | Epistemic Status | Primary Report | Raw Evidence / Anchor | Integrity | Known Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M1.1-S1** | Drone E2E Path Governance | PROVEN | [reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md](reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md) | `reports/evidence/drone/m1_1/s1/s1_audit_evidence.json` | `reports/evidence/drone/m1_1/s1/s1_freeze_anchor_v2.json` | Proves single mediated path only |
| **M1.1-S2-A** | Dynamic Endpoint Discovery | PROVEN | [reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md](reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md) | `reports/evidence/drone/m1_1/s2_v2/s2_v2_a_discovery.json` | `reports/evidence/drone/m1_1/s2_v2/s2_v2_a_discovery_inventory.json` | Catalogs active UDP socket surface ($|S|=5$) |
| **M1.1-S2-B** | Direct Parameter Mutation Authority | PROVEN | [reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md](reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md) | `reports/evidence/drone/m1_1/s2_v2/s2_v2_b_authority.json` | `reports/evidence/drone/m1_1/s2_v2/s2_b_freeze_anchor.json` | 4 endpoints capable of direct state mutation |
| **M1.1-S2-C** | Set Partition Governance Reconciliation | PROVEN | [reports/evidence/drone/m1_1/s2_v2/S2_C_EVIDENCE_INDEX.md](reports/evidence/drone/m1_1/s2_v2/S2_C_EVIDENCE_INDEX.md) | `reports/evidence/drone/m1_1/s2_v2/s2_v2_c_reconciliation.json` | `reports/evidence/drone/m1_1/s2_v2/s2_c_freeze_anchor.json` (Commit `c402bf...`) | Proves 3 active bypasses; port 14580 is INDETERMINATE |
| **M1.1-S2-D** | Host-Perimeter Containment & Execution Loop | CLOSED — NOT_PROVEN | [reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md](reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md) | `reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/` | `reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/GATE1_RESULT.json` | C1=PASS, C2=PASS, C3=NOT_PROVEN, ACK gap unresolved |
| **M1.1-S2-E** | Ingress Governance Transfer | PLANNED / NOT YET EVIDENCED | [reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md](reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md) | `tests/drone/s2/legacy/test_s2_e_governance_transfer.py` | None | Planned transfer stage; real PX4 route not established |
| **M1.1-S2-F** | Fresh Substrate Re-discovery | PLANNED / NOT YET EVIDENCED | [reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md](reports/evidence/drone/m1_1/M1_1_CLAIM_MATRIX.md) | None | None | Not executed |

---

## 6. S2-D Forensic Run Details

* **Canonical Forensic Document**: [reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md](reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md)
* **Gate 1 Non-Invasiveness Report**: [reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/GATE1_REPORT.md](reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/GATE1_REPORT.md)
* **Gate 1 Execution Result**: `reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/GATE1_RESULT.json`
* **Execution Graph**: [reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_EXECUTION_GRAPH.md](reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_EXECUTION_GRAPH.md)

### Detailed Run Evaluation

| Run Identifier | Stimulus & Scope | Observed Evidence | Outcome Verdict | Forensic Status |
| :--- | :--- | :--- | :--- | :---: |
| **RUN18** | Continuous live stimulation | PEP forward verified; PX4 UDP ingress observed | Wire ACK absent | `NOT_PROVEN` |
| **RUN19** | Wire-level packet inspection | UDP datagram (41 bytes) confirmed arriving at target port | No new `COMMAND_ACK(400)` frame | `NOT_PROVEN` |
| **RUN20** | Internal uORB listener test | Ephemeral listener launched to inspect `vehicle_command` | Listener lifecycle race missed event | `INVALID_EXPERIMENT` |
| **RUN20.1** | Diagnostic probe | Diagnosed listener termination timing | Listener exit prior to command arrival | `OBSERVED` |
| **RUN21** | Persistent uORB observer | Pre-established listener captured `vehicle_command` publish | Commander consumed; new ACK NOT OBSERVED | `OBSERVED / ACK GAP` |
| **RUN22** | Secondary readback check | Evaluated historical vs current ACK timestamps | Historical ACK present; current ACK absent | `NOT_OBSERVED` |
| **Restart A** | Fresh process restart | Fresh PX4 + PEP initialized; single ARM stimulus | PEP PDP reported `ARGUMENT_HASH_MISMATCH` | `OBSERVED ANOMALY` |
| **Restart B** | Alternative state branch | Secondary initialization branch | Not executed due to fail-closed barrier | `NOT_EXECUTED` |

### S2-D Conformance Invariants
* **S2-D STATUS**: `CLOSED — NOT_PROVEN`
* **Oracle C1**: `PASS`
* **Oracle C2**: `PASS`
* **Oracle C3**: `NOT_PROVEN`
* **Composite**: `NOT_PROVEN`
* **Execution Authority**: `NOT_PROVEN`
* **ACK Gap**: `OBSERVED / UNRESOLVED`
* **Root Cause**: `UNRESOLVED`
* **PDP Argument-Hash Determinism Anomaly**: `OBSERVED` (Expected `81880720...`; Computed `afc2771...`, `3661dd...`, `8e2335...`; Root Cause `UNRESOLVED`)

---

## 7. Other Benchmark Evidence

* **CyberMES Post-Compromise Crucible**:
  - Report: [reports/CYBERMES_POST_COMPROMISE_REPORT.md](reports/CYBERMES_POST_COMPROMISE_REPORT.md)
  - Traces: `reports/evidence/cybermes/`
* **Claude Red Team Benchmark (Autonomous Phase 2)**:
  - Report: [benchmarks/claude-red-vep/reports/autonomous_phase2_report.md](benchmarks/claude-red-vep/reports/autonomous_phase2_report.md)
  - Manifest: [benchmarks/claude-red-vep/FREEZE_MANIFEST_PHASE2.md](benchmarks/claude-red-vep/FREEZE_MANIFEST_PHASE2.md)
* **Mobile Android AppOps & Permission Baselines**:
  - Baseline Index: [reports/evidence/tmc_android_framework_baselines/20260923T_INDEX_CLOSED/ANDROID_FRAMEWORK_BASELINE_INDEX.md](reports/evidence/tmc_android_framework_baselines/20260923T_INDEX_CLOSED/ANDROID_FRAMEWORK_BASELINE_INDEX.md)
  - AppOps Traces: `reports/evidence/tmc_android_appops_baseline/`
  - Binder Traces: `reports/evidence/tmc_android_binder_baseline/`
  - SELinux Baseline: [reports/evidence/tmc_android_selinux_baseline/20260923T1/SELINUX_BASELINE_REPORT.md](reports/evidence/tmc_android_selinux_baseline/20260923T1/SELINUX_BASELINE_REPORT.md)

---

## 8. Raw Evidence Directories

All raw forensic logs, captures, and test execution snapshots are preserved in read-only directories:
* `reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/`
* `reports/evidence/cybermes/`
* `reports/evidence/tmc_android_permission_baseline/`
* `reports/evidence/tmc_android_selinux_baseline/`
* `reports/benchmarks/post_compromise/`

---

## 9. Integrity and Hash Records

* **S2-C Canonical Freeze Anchor**: [reports/evidence/drone/m1_1/s2_v2/s2_c_freeze_anchor.json](reports/evidence/drone/m1_1/s2_v2/s2_c_freeze_anchor.json)
* **S2-B Freeze Anchor**: [reports/evidence/drone/m1_1/s2_v2/s2_b_freeze_anchor.json](reports/evidence/drone/m1_1/s2_v2/s2_b_freeze_anchor.json)
* **S1 Freeze Anchor**: [reports/evidence/drone/m1_1/s1/s1_freeze_anchor_v2.json](reports/evidence/drone/m1_1/s1/s1_freeze_anchor_v2.json)
* **Drone M1.1 Manifest**: [reports/evidence/drone/m1_1/MANIFEST.sha256](reports/evidence/drone/m1_1/MANIFEST.sha256)
* **Comparative Benchmark Checksums**: [reports/evidence/comparative_benchmark/checksums.sha256](reports/evidence/comparative_benchmark/checksums.sha256)

---

## 10. Historical and Superseded Evidence

The following artifacts represent historical baselines or superseded iterations preserved strictly for audit lineage:
* `reports/evidence/drone/m1_1/s2/legacy/` (Legacy S2 test scripts and exit codes prior to v2 quad-gated architecture)
* `tests/drone/s2/legacy/LEGACY_README.md` (Historical testbed guidance)

---

## 11. Known Non-Evidence and Working Artifacts

The following directories contain build outputs, tooling scripts, or temporary run artifacts that **MUST NOT** be treated as verified evidence:
* `benchmarks/mobile_sdk/native_core/target/` (Cargo compilation artifacts)
* `node_modules/`, `.pytest_cache/`, `__pycache__/`
* `tmp/` (Local execution temporary files)

---

## 12. Verification Limitations

1. **Repository Access Prerequisite**: Automated verifiers must clone the repository locally; web crawl summaries do not constitute verified evidence.
2. **Whole-Vehicle Governance**: No claim of whole-vehicle governance is supported by current empirical evidence ($B > 0 \lor I > 0$).
3. **Execution Result ACK Loop**: The end-to-end execution acknowledgment loop for S2-D is `NOT_PROVEN` due to the observed and unresolved ACK gap.
4. **PDP Argument Hash Anomaly**: The runtime hash discrepancy observed during fresh restart is unconfirmed as a vulnerability and remains unresolved.
