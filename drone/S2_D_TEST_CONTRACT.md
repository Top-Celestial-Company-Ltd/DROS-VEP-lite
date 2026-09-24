# Milestone M1.1-S2-D Test Contract
## Reversible Host-Level Perimeter Containment & Control-Path Preservation

> **Epistemic Invariant**:
> $\text{Containment} \neq \text{Governance Transfer}$  
> $\text{Whole-Vehicle Governance} = \mathbf{PENDING\_GOVERNANCE\_TRANSFER\ (NOT\_PROVEN)}$
> 
> *“S2-D establishes only whether specifically identified S2-C bypasses can be reversibly contained under tested host-perimeter conditions, while preserving the designated governed control path. It does not establish governance transfer or whole-vehicle governance.”*

---

### 1. Core Proposition

> **S2-D evaluates whether the three active unmediated bypasses identified and frozen by S2-C can be reversibly contained at the defined host perimeter, while preserving the designated DROS-mediated control path and without modifying or restarting the PX4 flight-control process.**

---

### 2. Epistemic Scope & Bounded Terminology

To eliminate semantic drift and prevent claims from exceeding evidence boundaries, the following terminology constraints are mandatory:

1. **Reversibility Scope**:
   - **Prohibited**: *"100% reversible"*, *"completely reversible"*, *"universal reversibility"*.
   - **Mandatory**: *"Reversibility is demonstrated under the defined test procedure and observed execution conditions."*
   - **Rollback Proof**: *"The containment mechanism was successfully rolled back, and the previously observed bypass behavior was re-demonstrated under the same test conditions."*
2. **Containment Scope**:
   - **Prohibited**: *"rendering endpoints execution-incapable"*, *"closing all possible attacks"*.
   - **Mandatory**: *"rendering them incapable of inducing the previously observed state transition from the defined external probe surface."*
3. **Port 14580 Epistemic Boundary**:
   - Port 14580 is retained strictly as `INDETERMINATE_BOUNDARY`.
   - **No Perimeter Drop on 14580**: Host filtering rules MUST NOT drop packets destined for port 14580, as this would sever the designated DROS PEP delivery path (`UDP 14540 → PEP → Downstream Tap 14588 → PX4 14580`), inducing self-inflicted Denial of Service.
   - **Decoupled Responsibilities**: S2-D contains known bypasses; S2-E addresses boundary ownership and governance transfer.
4. **Subject Integrity Boundary**:
   - PX4 SITL C++ binary (`bin/px4`, SHA-256 `91fbf689...`) MUST NOT be recompiled, patched, or modified.
   - PX4 SITL runtime process MUST NOT be restarted, killed, or respawned during the execution of S2-D.

---

### 3. Three-Tier Evaluation Oracles

S2-D rejects any single simplistic metric (such as "0 downstream bytes") in favor of three concurrent oracles:

```text
               ┌────────────────────────────────────────────────────────┐
               │              S2-D Evaluation Oracles                   │
               └──────────────────────────┬─────────────────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
┌───────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────┐
│ Oracle A: Network     │   │ Oracle B: Execution       │   │ Oracle C: Control     │
│ Enforcement Evidence  │   │ State Integrity           │   │ Path Preservation     │
├───────────────────────┤   ├───────────────────────────┤   ├───────────────────────┤
│ • Rule hit counters   │   │ • Pre-state == Post-state │   │ • 14540 PEP path works│
│ • Packet drop verified│   │ • Target state Delta = 0  │   │ • PX4 PID unchanged   │
│ • Drop behavior logged│   │ • Mutation probe fails    │   │ • Binary hash matches │
└───────────────────────┘   └───────────────────────────┘   └───────────────────────┘
```

#### Oracle A: Network Enforcement Evidence
* Host packet filter rules (e.g. Linux `iptables` / `nftables`) targeting the designated bypass ports (`18570`, `13030`, `14280`) register non-zero packet drop counters upon probe injection.
* Network interface monitoring confirms drop behavior under external probe stimulation.

#### Oracle B: Execution Oracle (Target State Integrity)
* Injection of the exact S2-B raw MAVLink mutation payloads (`PARAM_SET`) against the contained ports results in **zero observed state transition** in PX4:
  $$\Delta \text{State}(\text{MIS\_TAKEOFF\_ALT}) = 0 \quad (\text{Pre} \equiv \text{Post})$$
  $$\Delta \text{State}(\text{TRIG\_INTERVAL}) = 0 \quad (\text{Pre} \equiv \text{Post})$$

#### Oracle C: Control Path Preservation (Negative Control)
* **Designated Governed Control Path Preserved**: The DROS-mediated execution path (`UDP 14540 → PEP → Downstream Tap 14588 → PX4 14580`) remains operational:
  - Authorized, cryptographically signed ARM request sent to `UDP 14540` is admitted by PEP and observed at Downstream Tap, reaching PX4.
  - Unauthorized request (forged signature / ungranted capability) sent to `UDP 14540` is blocked at PEP boundary (0 downstream packets).
* **Runtime Continuity**: PX4 flight-control process PID remains constant across all phases (no process crash or restart).

---

### 4. Four-Phase Execution Protocol

```text
PHASE 1: Frozen Baseline Confirmation
  ├── Assert S2-C freeze anchor validity (s2_c_freeze_anchor.json, commit c402bf...)
  ├── Confirm baseline partition: B=3, I=1, U=1, G=0, N=0
  └── Confirm PX4 process health (PID active, binary SHA-256 == 91fbf689...)
  ↓
PHASE 2: Containment Activation
  ├── Apply host perimeter packet filter rules (DROP input to UDP 18570, 13030, 14280)
  ├── Do NOT modify port 14580; do NOT touch PX4 binary; do NOT restart PX4
  └── Capture baseline rule counters (all initial counters recorded)
  ↓
PHASE 3: Symmetric Verification & Control Path Preservation
  ├── Inject S2-B mutation probes to 18570, 13030, 14280
  │     ├── Oracle A: Verify rule drop counters increment
  │     └── Oracle B: Readback PX4 parameters; verify Pre == Post (no mutation)
  └── Test designated PEP path (UDP 14540)
        ├── Oracle C: Authorized ARM admitted & executed
        └── Oracle C: Unauthorized ARM blocked at PEP boundary
  ↓
PHASE 4: Rollback & Re-demonstration
  ├── Remove host perimeter containment rules
  ├── Verify host firewall tables restored to pre-test baseline
  └── Re-inject S2-B mutation probes to 18570, 13030, 14280
        └── Verify state transitions re-occur under identical conditions (Pre != Post)
```

---

### 5. Target Surface Matrix

| Endpoint Key | Port | Protocol | S2-C Baseline | S2-D Target Treatment | Phase 3 Verification | Phase 4 Rollback Verification |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| `0.0.0.0:18570` | 18570 | UDP | `UNMEDIATED_ACTIVE_BYPASS` | Host Filter DROP | Rule Hit, State Delta = 0 | Rule Removed, State Delta $\neq$ 0 |
| `0.0.0.0:13030` | 13030 | UDP | `UNMEDIATED_ACTIVE_BYPASS` | Host Filter DROP | Rule Hit, State Delta = 0 | Rule Removed, State Delta $\neq$ 0 |
| `0.0.0.0:14280` | 14280 | UDP | `UNMEDIATED_ACTIVE_BYPASS` | Host Filter DROP | Rule Hit, State Delta = 0 | Rule Removed, State Delta $\neq$ 0 |
| `0.0.0.0:14580` | 14580 | UDP | `INDETERMINATE_BOUNDARY` | **Unfiltered (Preserved)** | PEP delivery downstream | Retained for S2-E Transfer |
| `0.0.0.0:14540` | 14540 | UDP | (S1 PEP Ingress) | **Unfiltered (Preserved)** | Authorized PASS / Unauth DENY | Continues operation |

---

### 6. Formal Verdict Schema

The test harness must output one of four mutually exclusive verdicts:

| Verdict | Meaning & Epistemic Gate |
| :--- | :--- |
| **`PASS`** | All mandatory Oracles (A, B, and C) across Phases 1–4 are strictly satisfied. Containment rendered bypasses incapable of inducing state mutations from the external probe surface, control path was preserved, and reversibility was empirically demonstrated upon rollback. |
| **`FAIL`** | Any mandatory oracle violated: bypass mutation succeeded during Phase 3, control path (14540) was disrupted, PX4 crashed/restarted, or rollback failed to restore bypass behavior. |
| **`INDETERMINATE`** | Instrumentation, reachability, or network observation was insufficient to conclusively prove packet drop or state preservation (e.g. socket timeout without rule counter increment). |
| **`ABORTED`** | Environmental fault, flight-control instability, or prerequisite check failure mandated immediate test halting. |

---

### 7. Governance Claim Ceilings (Negative Invariants)

The following negative constraints are permanent and non-negotiable:

1. **`S2-D does NOT establish Whole-Vehicle Governance.`**
2. **`S2-D does NOT establish Governance Transfer.`**
3. **`S2-D does NOT establish elimination of all execution bypasses.`**
4. **`S2-D establishes only whether specifically identified S2-C bypasses can be reversibly contained under the tested host-perimeter conditions.`**

**Mandatory Output Classification**:
* **Known Execution Ingress**: 4
* **S2-C Active Bypass Baseline**: 3 (`18570`, `13030`, `14280`)
* **S2-D Contained Ingress**: 3
* **Residual Unmanaged Active Bypasses**: 0 (during Phase 3 active containment)
* **Designated Governed Control Path**: 1 (`14540 → PEP → 14588 → 14580`)
* **Indeterminate Boundary**: 1 (`14580`)
* **S2-D Containment Status**: `CONTAINED`
* **Whole-Vehicle Governance Status**: $\mathbf{PENDING\_GOVERNANCE\_TRANSFER\ (NOT\_PROVEN)}$
