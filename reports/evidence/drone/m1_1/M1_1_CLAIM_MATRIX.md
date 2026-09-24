# DROS Drone Governance Extension — Milestone M1.1 Claim Matrix
## Real C++ PX4 SITL Autopilot Verification & Execution Path Attestation

> **Epistemic Invariant**:
> $\text{Phase 0 PASS} \not\equiv \text{M1 PASS} \land \text{REAL\_SUBJECT} \not\equiv \text{COMPLETE\_SUBJECT}$.
> 
> *“S1 proves path governance. S2 determines whether path governance is vehicle-wide.”*
> 
> Any claim without a direct pointer to physical, byte-level raw artifacts is `NOT_PROVEN` by default.

---

### 1. Milestone Sub-Stage Definitions & Evidence Ladder

| Level / Stage | Epistemic Designation | Core Focus | Execution Subject | Transport / Boundary | Scope & Governance Status |
|---|---|---|---|---|---|
| **$L_0$** | In-Process Mock | Policy Logic Baseline | Python in-memory classes | Direct Python in-process calls | **PROVEN** (Phase 0 Baseline, ATS-006~ATS-010) |
| **$L_1$** | Real Process / Network | Socket Wire Mediation | Python `pymavlink` mock server | OS UDP sockets (14540 $\to$ 14550) | **PROVEN** (EV-DRONE-REAL-NET-002, Tickets 01~04) |
| **$M1.1\text{-}S0$** | Subject Authenticity | Native Binary Identity | Genuine C++ PX4 SITL ELF (`v1.14.3`) | Localhost `/proc` & `ss -lunp` | **PROVEN** (SHA256, runtime PID, socket inventory) |
| **$M1.1\text{-}S1$** | Path Governance | Single Execution Path | Genuine C++ PX4 SITL ELF | UDP 14540 $\to$ PEP $\to$ Tap (14588) $\to$ 14580 PX4 | **PROVEN** (5/5 pytest passed, symmetric pair verified) |
| **$M1.1\text{-}S2\text{-}A$** | Dynamic Discovery | Execution Endpoint Surface | Genuine C++ PX4 SITL ELF | Dynamic Linux kernel socket table (`ss -lunp`) | **PROVEN within observed execution surface** (5 endpoints cataloged) |
| **$M1.1\text{-}S2\text{-}B$** | Execution Authority | Direct Parameter Mutation | Genuine C++ PX4 SITL ELF | Raw MAVLink PARAM_SET injection & readback | **PROVEN for dynamically discovered/tested endpoints** (4 capable, 1 unreachable) |
| **$M1.1\text{-}S2\text{-}C$** | Governance Reconciliation | Empirical Set Reconciliation | Genuine C++ PX4 SITL ELF | Dual-reader exact route matching ($G, B, I, U, N$) | **PROVEN as an executed reconciliation method/result** (Whole-Vehicle Governance = **NOT_PROVEN**) |
| **$M1.1\text{-}S2\text{-}D$** | Reversible Containment | Host-Level Perimeter Control | Genuine C++ PX4 SITL ELF | Host-level packet filter (Containment $\neq$ Transfer) | **PLANNED / NOT YET EVIDENCED** |
| **$M1.1\text{-}S2\text{-}E$** | Governance Transfer | Semantic Path Ingress Transfer | Genuine C++ PX4 SITL ELF | Correlated transaction $\to$ wire $\to$ effect (14580) | **PLANNED / NOT YET EVIDENCED** |
| **$M1.1\text{-}S2\text{-}F$** | Fresh Re-discovery | Post-Transfer Surface Re-scan | Genuine C++ PX4 SITL ELF | Unbiased substrate discovery from zero | **PLANNED / NOT YET EVIDENCED** |
| **$L_3$** | Hardware-in-the-Loop | Physical Avionics Interface | Physical FC (e.g. Pixhawk 6X) | Serial / CAN / Ethernet | **NOT_PROVEN** (Out of M1.1 scope) |
| **$L_4$** | Physical UAV Airframe | Full Flight Operations | Real drone in flight envelope | RF telemetry / companion computer | **NOT_PROVEN** (Out of M1.1 scope) |

---

### 2. Milestone M1.1 Detailed Claim Matrix

| Claim Identifier | Detailed Claim Description | Sub-stage & Focus | Physical Evidence Pointer | Status |
|---|---|---|---|---|
| **CLM-M1.1-S0-01** | Real C++ PX4 SITL native executable identity and SHA-256 integrity attested on Linux OS | M1.1-S0 (Subject Authenticity) | [s0_runtime_attestation.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s0_runtime_attestation.log) | **PROVEN** |
| **CLM-M1.1-S0-02** | Active runtime execution attestation via Linux `/proc/<PID>/exe` and command line flags | M1.1-S0 (Subject Authenticity) | [s0_runtime_attestation.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s0_runtime_attestation.log) | **PROVEN** |
| **CLM-M1.1-S0-03** | Comprehensive socket inventory and unmediated bypass discovery (`18570`, `14280`, `13030`) | M1.1-S0 (Subject Authenticity) | [s0_runtime_attestation.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s0_runtime_attestation.log) | **PROVEN** |
| **CLM-M1.1-S1-01** | Authorized command translation produces a valid binary MAVLink `COMMAND_LONG` frame (41 bytes) observed at the instrumented downstream observation point (UDP 14588 Tap) | M1.1-S1 (Path Governance) | [s1_px4_e2e.stdout.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_px4_e2e.stdout.log), [s1_audit_evidence.json](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_audit_evidence.json) | **PROVEN** |
| **CLM-M1.1-S1-02** | Cryptographic signature forgery rejected at PEP boundary; produces zero observed downstream packets on the tested mediated path | M1.1-S1 (Path Governance) | [s1_px4_e2e.stdout.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_px4_e2e.stdout.log), [s1_audit_evidence.json](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_audit_evidence.json) | **PROVEN** |
| **CLM-M1.1-S1-03** | Unauthorized capability request is denied by DROS policy engine and produces zero observed downstream packets on the tested mediated path | M1.1-S1 (Path Governance) | [s1_px4_e2e.stdout.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_px4_e2e.stdout.log), [s1_audit_evidence.json](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_audit_evidence.json) | **PROVEN** |
| **CLM-M1.1-S1-04** | A tested malformed/unparseable wire input is rejected and produces zero observed downstream packets across the tested PEP UDP 14540 ingress path (*Not a fuzzing claim) | M1.1-S1 (Path Governance) | [s1_px4_e2e.stdout.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_px4_e2e.stdout.log), [s1_audit_evidence.json](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_audit_evidence.json) | **PROVEN\*** |
| **CLM-M1.1-S1-05** | After OS-level SIGKILL of the tested PEP process, a subsequent request sent to the PEP ingress produced zero observed downstream packets on the tested mediated path | M1.1-S1 (Path Governance) | [s1_px4_e2e.stdout.log](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_px4_e2e.stdout.log), [s1_audit_evidence.json](file:///e:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/reports/evidence/drone/m1_1/s1_audit_evidence.json) | **PROVEN\*** |
| **CLM-M1.1-S2-A-01** | Dynamic kernel socket discovery identifies the active execution endpoint surface of running PX4 SITL without static assumptions | M1.1-S2-A (Dynamic Discovery) | `s2_v2_a_discovery.json`, `s2_v2_a_kernel_ss_raw.log` | **PROVEN within observed execution surface** |
| **CLM-M1.1-S2-B-01** | Empirical execution authority attestation proves state-mutation capability via quad-gated physical injection across discovered endpoints | M1.1-S2-B (Authority Proof) | `s2_v2_b_authority.json`, `s2_v2_b_authority_summary.json` | **PROVEN for dynamically discovered/tested endpoints** |
| **CLM-M1.1-S2-C-01** | Mathematical partition reconciliation between frozen S1 governance topology and S2-B authority surface ($S = G(0) \uplus B(3) \uplus I(1) \uplus U(1) \uplus N(0)$) | M1.1-S2-C (Reconciliation) | `s2_v2_c_reconciliation.json`, `s2_v2_c_reconciliation_summary.json`, `s2_c_freeze_anchor.json` | **PROVEN as an executed reconciliation method/result** |
| **CLM-M1.1-S2-C-02** | Conservative fail-closed classification of port 14580 as `INDETERMINATE_BOUNDARY` due to target overlap without PEP ingress path identity | M1.1-S2-C (Reconciliation) | `s2_v2_c_reconciliation.json` | **PROVEN as an executed reconciliation method/result** |
| **CLM-M1.1-S2-C-03** | Whole-vehicle execution governance across all discovered autopilot execution endpoints | M1.1-S2-C (Reconciliation) | `s2_v2_c_reconciliation_summary.json` | **NOT_PROVEN** ($B > 0 \lor I > 0 \implies \text{WVG} = \text{NOT\_PROVEN}$) |
| **CLM-M1.1-S2-D-01** | Reversible host-level perimeter containment of unmediated bypasses without modifying PX4 flight control binary (Containment $\neq$ Transfer) | M1.1-S2-D (Containment) | — | **PLANNED / NOT YET EVIDENCED** |
| **CLM-M1.1-S2-E-01** | Empirical governance transfer correlating transaction $\to$ wire $\to$ effect, transitioning port 14580 from indeterminate to governed | M1.1-S2-E (Governance Transfer) | — | **PLANNED / NOT YET EVIDENCED** |
| **CLM-M1.1-S2-F-01** | Fresh substrate re-discovery from zero verifying post-transfer execution surface without reusing historical endpoint lists | M1.1-S2-F (Re-discovery) | — | **PLANNED / NOT YET EVIDENCED** |
| **CLM-M1.1-E2E-ALL** | Complete whole-drone execution governance across all autopilot physical interfaces | M1.1 (Whole Vehicle) | — | **NOT_PROVEN** (Permanent restriction until complete S2 lifecycle verified) |

---

### 3. Epistemic Baseline & Core Conclusions

1. **M1.1-S0 establishes that the execution subject is a genuine native C++ PX4 SITL binary and identifies its active network interfaces.**
   - Physical binary confirmed at `/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/bin/px4`.
   - SHA-256 (`91fbf68980835c3272b0b9d77690ea366deed760f2da2c00365c790341d095eb`) and Linux `/proc/<PID>/exe` attestation verified.
   - Comprehensive socket inventory proved PX4 listens on multiple ports (`18570`, `14580`, `14280`, `13030`), preventing any premature "whole-vehicle" claim.

2. **M1.1-S1 establishes that a specific execution path can be deterministically mediated by DROS PEP: an authorized request produces a binary MAVLink `COMMAND_LONG` frame at the instrumented downstream observation point, while forged signatures, unauthorized capability requests, malformed/raw input, and post-termination requests produce zero observed downstream bytes on that path.**
   - Testing path: `Client (Ephemeral) → DROS PEP (UDP 14540) → Instrumented Downstream Observation Point (UDP 14588 Tap) → Real PX4 SITL (UDP 14580)`.
   - Note on Instrumentation: The Tap on UDP 14588 serves as an *instrumented downstream observation point* capturing byte-level traffic emitted by PEP before forwarding to PX4, rather than an uninstrumented direct-wire observation.
   - Byte-level physical proofs:
     - Authorized: `COMMAND_LONG` (41 bytes) emitted and captured.
     - Forged Signature: `0` packets / `0` bytes delivered downstream.
     - Unauthorized Capability Escalation: `0` packets / `0` bytes delivered downstream.
     - Wire Malformed Fuzzing: `0` packets / `0` bytes delivered downstream.
     - Post-SIGKILL: `0` packets / `0` bytes delivered downstream.

3. **M1.1-S2 Lifecycle establishes an empirical, multi-stage governance assessment framework:**
   - **S2-A (Dynamic Discovery)**: Evaluated directly from OS kernel tables (`ss -lunp`), establishing the empirical endpoint surface ($|S| = 5$).
   - **S2-B (Authority Proof)**: Quad-gated mutation probes confirmed 4 endpoints possess genuine execution authority (`18570`, `13030`, `14280`, `14580`), while 1 endpoint is unreachable under probe method (`36287 → 8888`).
   - **S2-C (Governance Reconciliation)**: Formal dual-reader set reconciliation against frozen S1 governance evidence demonstrated:
     $$S = G(0) \uplus B(3) \uplus I(1) \uplus U(1) \uplus N(0)$$
     $$E = G(0) \uplus B(3) \uplus I(1) = 4$$
     - Port 14580 is classified strictly as `INDETERMINATE_BOUNDARY` because while target overlap exists with S1, S2-B lacks PEP ingress path proof and exact route match count is 0.
     - Under fail-closed governance axioms ($B > 0 \lor I > 0$), **Whole-Vehicle Governance is NOT PROVEN**.
   - **S2-D ~ S2-F**: Define the forward trajectory from reversible risk containment (S2-D) to empirical governance transfer (S2-E) and clean-state re-discovery (S2-F). Each stage remains `PLANNED / NOT YET EVIDENCED` until executed and sealed under canonical freeze anchors.

---

### 4. Physical Test Execution Summary

* **Execution Host**: Ubuntu Server 24.04.4 LTS (`6.8.0-139-generic x86_64`) on Intel Core i5-3450/i5-3450T (16GB RAM).
* **Test Suite**: `tests/drone/test_m1_1_s1_px4_e2e.py`
* **Test Result**: `5 passed in 9.63s` (Exit Code: `0`).
* **Artifact Files**:
  - Raw stdout: `reports/evidence/drone/m1_1/s1_px4_e2e.stdout.log`
  - Exit code: `reports/evidence/drone/m1_1/s1_px4_e2e.exit_code`
  - Downstream Tap Audit Evidence: `reports/evidence/drone/m1_1/s1_audit_evidence.json`
