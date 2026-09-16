# VEP Baseline Open Issues & Technical Debt (OPEN_ISSUES.md)
* **Status**: ACTIVE
* **Baseline ID**: BASELINE-VEP-2026-M5.1
* **Date**: 2026-09-16

---

## 1. Resolved Baseline Reconciliations (This Session)
* **ISSUE-01: Multiple Experiment IDs across M5 Documentation**
  - **Resolution**: Reconciled. `EXP-1789532251-38a4fd` is designated as the sole canonical multi-substrate experiment for `VEP-REPORT-2026-M5.1`. `EXP-1789530057-779a1d` is documented in `EXPERIMENT_MANIFEST.json` as an archived 33-iteration predecessor without the OPA arm.
* **ISSUE-02: Substrate Hash Reconciliation**
  - **Resolution**: Substrate evaluator hash `96d5bdbcf953a98ad3070184df068405d2ada09715a7a698e50fbaa93bd2cce0` (`vep.py`) is verified matching across report text, `reports/evidence_manifest.json`, and filesystem SHA-256.

---

## 2. Active Technical & Epistemic Boundaries (Next Roadmap Phases)
* **BOUNDARY-01A (Loopback IPC Authentication - Windows Native Named Pipe - CLOSED)**:
  - Phase P1 Completed: Formal threat model (`LOOPBACK_IPC_THREAT_MODEL.md`) and requirements (`IPC_AUTHENTICATION_REQUIREMENTS.md`) frozen.
  - Phase P2 Completed: Candidate C hybrid authentication prototype verified against 15/15 adversarial cases (`ipc_p2_evidence.jsonl`, SHA-256: `d2728138...`).
  - Phase P3 Completed: Real OS process identity invariant and PID reuse vulnerability closed via $\langle \text{PID}, \text{create\_time} \rangle$ dual-binding; Windows kernel Named Pipe attribution experimentally validated via `kernel32.GetNamedPipeClientProcessId` (`ipc_p3_real_os_evidence.jsonl`, SHA-256: `d3365d7e...`). BOUNDARY-01A formally CLOSED.
* **BOUNDARY-01B (Loopback IPC Authentication - Linux UDS SO_PEERCRED - OPEN / PRESERVED EPISTEMIC FIREWALL)**:
  - Linux `LinuxPeerIdentityProvider` is fully implemented and unit-tested with fallback handling, but awaiting live-host execution on a native Linux kernel.
  - Phase P5 Status: Formally preserved as **OPEN**. Strictly serves as an Epistemic Firewall: DROS explicitly refuses to package Windows Named Pipe empirical validation as cross-platform Linux proof. Will be executed in dedicated Linux VM verification pack.
* **BOUNDARY-02 (Level-C Feature Conjunction Verification - OPEN / PRESERVED EPISTEMIC FIREWALL)**:
  - Protocol: `PROTO-LANDSCAPE-2026-v1.0`. Candidate Universe: 14 total (11 included, 3 excluded).
  - Empirical Finding: Under Claim Ladder Level 3, no external peer candidate documents primary-source evidence satisfying the complete Level-C conjunction.
  - Phase P5 Status: Formally preserved as **OPEN / SEARCH-BOUNDED EMPIRICAL FINDING**. Serves as an Epistemic Firewall against universal negative overclaim ("nobody in the world has built this"); explicitly acknowledges inductive search boundaries. Ratified in CLAIM-08.
* **BOUNDARY-03 (Agent Server Hub Deployment Model - CLOSED / RATIFIED IN P6)**:
  - Architecture Thesis: DROS deployed once at Agent Server execution boundary governs all downstream tools without per-agent governance overhead.
  - Phase P6 Status: Formally **CLOSED**. Formalized $\mathbf{GIC}(S, E)$ cost vector, demonstrated sub-linear integration scaling, and explicitly bounded the Non-Bypassable Mediation Interface and Execution Privilege Decoupling preconditions. Ratified in CLAIM-09 and `REPORT_P6_CONSOLIDATED_AUDIT.md`.