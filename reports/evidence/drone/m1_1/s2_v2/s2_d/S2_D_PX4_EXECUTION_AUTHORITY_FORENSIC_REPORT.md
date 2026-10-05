# S2-D PX4 Execution Authority Forensic & Reconciliation Report

- **Document Identifier**: `S2-D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md`
- **Milestone / Investigation Scope**: Milestone M1.1 S2-D Live Investigation & Post-Failure Forensics (RUN18, RUN19, RUN20, RUN20.1, RUN21, RUN22, Restart A/B)
- **Status**: `CLOSED — NOT_PROVEN`
- **Subject Under Evaluation**: PX4 Autopilot SITL & DROS PEP Control Boundary
- **Classification**: Forensic Audit & Public Reconciliation

---

## 1. Scope

This report documents the forensic campaign, empirical execution trace, and evidence reconciliation for Milestone M1.1 Stage S2-D. The objective of S2-D was to evaluate whether unmediated bypasses identified during S2-C could be reversibly contained at the host perimeter while preserving designated DROS-mediated execution authority to the PX4 autopilot without restarting the process.

This document serves as the canonical public forensic summary for the campaign comprising:
* RUN18
* RUN19
* RUN20
* RUN20.1
* RUN21
* RUN22
* Fresh-Restart Experiment (State A / State B)

---

## 2. Experimental Boundary

The investigation operated under strict physical and architectural boundaries:
* **Autopilot Substrate**: Native Linux 64-bit ELF `px4` execution binary in SITL configuration.
* **Mediation Interface**: DROS Policy Enforcement Point (`drone/pep_proxy.py`) bound to UDP port `14540`.
* **Execution Boundary / Downstream Target**: Ingress to PX4 flight control port `14580` (with historical tap references at `14588`).
* **Containment Perimeter**: Linux kernel `iptables` packet filtering on bypass ports `18570`, `14280`, and `13030`.
* **Zero Runtime Re-experimentation Rule**: Following the formal closure of the forensic campaign, no further live executions, arms, disarms, restarts, or retries are permitted.

---

## 3. Environment

The forensic measurements were conducted in the standardized live drone bench environment:
* **Target Operating System**: Ubuntu Linux 24.04 LTS (`192.168.100.31`)
* **Autopilot Software**: PX4 Autopilot SITL `v1.14.3`
* **Network Topology**: Local loopback interface `127.0.0.1` and target host interfaces
* **Ingress Protocols**: MAVLink 1.0 and 2.0 frames encapsulated in UDP datagrams

---

## 4. Integrity Anchors

The investigation anchored on verified cryptographic artifacts:

| Component | Identifier / Path | SHA-256 Digest / Invariant | Status |
| :--- | :--- | :--- | :---: |
| **PX4 SITL ELF** | `bin/px4` (Linux 64-bit) | `91fbf68980835c3272b0b9d77690ea366deed760f2da2c00365c790341d095eb` | Verified (`/proc/<PID>/exe`) |
| **PEP Proxy** | `drone/pep_proxy.py` | `cf26be19...` (prefix confirmed in runtime audit) | Verified |
| **S2-C Frozen Anchor** | `reports/evidence/drone/m1_1/s2_v2/s2_c_freeze_anchor.json` | Commit: `c402bf05024613501083441c2f26316b47e88d78` | Sealed Baseline |
| **S2-D Live Run #1 Result** | `reports/evidence/drone/m1_1/s2_v2/s2_d_live/S2_D_LIVE_RESULT.json` | Preserved failure: `pre=d4317524205c != post=a0a620d5146b` | Sealed (FAIL) |
| **Historical Forensic Report** | `reports/evidence/drone/m1_1/s2_v2/S2_D_LIVE_FAILURE_FORENSIC_REPORT.md` | Rollback representation flaw & counter noise analysis | Sealed Historical |

*(Note: Full 64-character hex digests are reproduced where available; prefixes are preserved exactly as verified without synthetic padding).*

---

## 5. Run-by-Run Evidence Summary

The forensic campaign progressed across discrete diagnostic runs to isolate execution authority and response behavior:

| Run ID | Scope / Stimulus | Observed Physical Event | Outcome | Classification |
| :--- | :--- | :--- | :--- | :---: |
| **RUN18** | Continuous live stimulation | PEP forward verified; PX4 UDP ingress observed | No current ACK returned on wire | `NOT_PROVEN` |
| **RUN19** | Wire-level packet inspection | UDP datagram (41 bytes) confirmed arriving at target port | No new `COMMAND_ACK(400)` frame | `NOT_PROVEN` |
| **RUN20** | Internal uORB listener test | Ephemeral listener launched to inspect `vehicle_command` | Listener lifecycle race; listener missed event | `INVALID_EXPERIMENT` |
| **RUN20.1** | Diagnostic uORB probe | Diagnosed listener termination timing | Listener exit prior to command arrival | `OBSERVED` |
| **RUN21** | Persistent uORB observer | Pre-established listener captured `vehicle_command` publish | `vehicle_command` consumed by Commander; no new ACK | `OBSERVED / ACK GAP` |
| **RUN22** | Secondary readback check | Evaluated historical vs current ACK timestamps | Historical ACK present; current ACK absent | `NOT_OBSERVED` |
| **Restart A** | Fresh process restart | Fresh PX4 and fresh PEP initialized; single ARM stimulus | PDP reported `ARGUMENT_HASH_MISMATCH`; probe blocked | `OBSERVED ANOMALY` |
| **Restart B** | Alternative state path | Planned secondary branch | Not executed due to fail-closed boundary | `NOT_EXECUTED` |

---

## 6. Proven Runtime Path

Empirical observations across RUN18 through RUN21 established the following ingress and consumption path:

```text
PEP Authorization
      │ [PASS: verdict == ALLOW]
      ▼
PEP Forwarding
      │ [PASS: UDP datagram transmitted downstream]
      ▼
PX4 UDP Ingress
      │ [PASS: Socket readback confirms arrival on target port]
      ▼
COMMAND_LONG(400)
      │ [PASS: MAVLink message parsed as ARM request]
      ▼
vehicle_command Publish
      │ [PASS: Internal uORB topic published]
      ▼
Commander Consume
      │ [PASS: PX4 Commander module consumes command]
```

**Empirical Boundary**: Within the tested path, DROS-controlled command ingress and Commander consumption were empirically observed. This demonstrates that the command successfully entered the autopilot execution subsystem through the mediated gateway. It does not establish execution completion or authority acknowledgment.

---

## 7. Source-Proven Path

Analysis of the PX4 Autopilot source code (`v1.14.3`) traces the theoretical internal processing path beyond ingestion:

```text
Commander
  │
  ▼
handle_command()
  │
  ▼
VEHICLE_CMD_COMPONENT_ARM_DISARM
  │
  ▼
ARMING_ACTION_ARM
  │
  ▼
arm()
  │
  ▼
preflight checks
  │
  ▼
TRANSITION_DENIED / TEMPORARILY_REJECTED
  │
  ▼
answer_command()
  │
  ▼
_vehicle_command_ack_pub.publish()
```

**Distinction**: This execution branch is **SOURCE-PROVEN** via static code analysis. It is **NOT RUNTIME-PROVEN** in the live test environment because the concluding ACK emission was not observed at runtime.

---

## 8. Runtime Gap (The ACK Gap)

During live execution across the continuous runs:
* **New `vehicle_command_ack`**: `NOT OBSERVED`
* **`COMMAND_ACK(400)` on Wire**: `NOT OBSERVED`

Forensic findings regarding the ACK gap:
1. The listener timing artifact encountered in RUN20/RUN20.1 was completely eliminated in RUN21 by attaching a persistent observer prior to stimulus injection.
2. In RUN21, Commander consumption was directly observed, but no subsequent `vehicle_command_ack` instance was published by the Commander.
3. While historical ACK frames from prior sessions existed in log buffers, zero new ACK frames were generated in response to the stimuli of RUN18–RUN21.
4. Historical ACKs cannot and must not be used to claim that current runs emitted an acknowledgment.

---

## 9. Fresh-Restart Experiment (Restart A/B)

To evaluate whether process continuity or accumulated state influenced the ACK gap, a fresh restart experiment was conducted:

* **State A Execution**:
  - Freshly spawned PX4 SITL process.
  - Freshly spawned PEP proxy process.
  - Exactly one ARM command stimulation injected.
  - **Result**: PEP Policy Decision Point (PDP) rejected the request due to `ARGUMENT_HASH_MISMATCH`.
  - The command was blocked at the PEP gateway; downstream Commander was never reached.
* **State B**:
  - Not executed.
* **Conclusion**: Fresh-state effect on the ACK gap is **NOT ESTABLISHED** because State A failed at the ingress PDP boundary prior to reaching PX4.

---

## 10. PDP Argument-Hash Anomaly

During the fresh-restart attempt, an unexpected non-deterministic behavior in argument hashing was discovered:

```text
PDP ARGUMENT-HASH DETERMINISM ANOMALY = OBSERVED

EXPECTED HASH PREFIX:
81880720...

COMPUTED HASH PREFIXES:
afc2771...
3661dd...
8e2335...
```

**Classification**:
* Status: `OBSERVED ANOMALY`
* Root Cause: `UNRESOLVED`
* Boundary Rule: This finding must NOT be classified as a "confirmed vulnerability", "payload mutation attack", or "security exploit". It represents an observed discrepancy in runtime argument hash computation across fresh startup cycles requiring isolated future investigation.

---

## 11. Separation of the Two Evidence Chains

To prevent false attribution, the evidence must be strictly split into two orthogonal chains:

### Chain A: Continuous Runtime Path (RUN18 – RUN22)
```text
PEP Auth (ALLOW)
  └──> PEP Forwarding (Wire Send)
        └──> PX4 Ingress (Wire Receive)
              └──> vehicle_command Published
                    └──> Commander Consumed
                          └──> New vehicle_command_ack: NOT OBSERVED
                          └──> Wire COMMAND_ACK: NOT OBSERVED
```

### Chain B: Fresh-Restart Ingress Path (State A)
```text
Fresh PEP / PX4
  └──> ARM Request
        └──> PEP PDP Evaluation
              └──> ARGUMENT_HASH_MISMATCH (Denied)
                    └──> Ingress Blocked
                          └──> Commander NOT REACHED
```

**Epistemic Rule**: Chain B is an independent ingress failure on fresh startup; it is **NOT** the root cause of Chain A's downstream ACK gap.

---

## 12. Evidence Reconciliation & Final Verdict

### S2-D Formal Outcome Matrix

```text
========================================================================
S2-D STATUS: CLOSED — NOT_PROVEN
========================================================================
Oracle C1 (PEP Binding & Ingress Control) : PASS
Oracle C2 (PEP Forwarding & Downstream)   : PASS
Oracle C3 (PX4 Command Execution ACK)    : NOT_PROVEN
------------------------------------------------------------------------
Composite Evaluation                      : NOT_PROVEN
Execution Authority Verification          : NOT_PROVEN
ACK Gap Status                            : OBSERVED / UNRESOLVED
Root Cause                                : UNRESOLVED
========================================================================
```

---

## 13. Limitations & Disclaimers

1. **No Whole-Vehicle Governance**: S2-D does not establish whole-vehicle governance across all autopilot interfaces.
2. **No Closed-Loop Execution Proof**: S2-D does not establish that PX4 executed the requested flight mode change to completion with closed-loop attribution.
3. **No Automatic Vulnerability Attribution**: The PDP argument-hash discrepancy remains an unresolved anomaly, not an exploit.
4. **Historical Immutability**: All original artifacts from RUN18–RUN22, Run #1, and Gate 1 remain frozen and unmodified.

---

## 14. Future Research Boundary

All live PX4 runtime experimentation is formally paused and concluded:
* **PX4 S2-D ACK Forensic**: `PAUSED`
* **PDP-ARGHASH-DET Investigation**: `NOT STARTED`
* **Further Live Execution**: `STRICTLY FORBIDDEN`
