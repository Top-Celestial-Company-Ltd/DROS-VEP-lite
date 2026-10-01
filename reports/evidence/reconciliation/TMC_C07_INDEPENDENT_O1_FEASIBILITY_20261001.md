# TMC-C07 Independent O1 Observer Feasibility Reconciliation — 2026-10-01

**Document ID:** `TMC_C07_INDEPENDENT_O1_FEASIBILITY_20261001`  
**Date:** 2026-10-01  
**Governance Protocol:** READ-ONLY / RECORD-ONLY  
**Subject:** Feasibility Reconciliation of an Independent Downstream Target Observer ($O_1$) for `TMC-C07`  
**Parent Records:**  
- `reports/evidence/reconciliation/TMC_C07_INDEPENDENT_TARGET_OBSERVER_RECONCILIATION_20260930.md`  
- `reports/evidence/reconciliation/TMC-C07_O1_FEASIBILITY_ASSESSMENT_20261001.md`  
- `reports/evidence/reconciliation/CLAIM_CLOSURE_GATE_20261001.md`  

---

## 1. Current TMC-C07 Status

Under the definitive claim closure gate (`CLAIM_CLOSURE_GATE_20261001.md`):
- **Canonical Claim ID:** `TMC-C07`
- **Manuscript Source:** IEEE TMC §3.3 Table VI
- **Existing Artifact Source:** App-owned `effects.jsonl` (`tmc_android_base_03_avd/20260922T5/`, `base_05_avd/20260922T7/`)
- **Safe Permissible Scope:** Bounded descriptive statement of "application-reported fixture execution markers"; independent downstream target oracle claim is explicitly retracted.
- **Closure Disposition:** **`Category D (NARROWED_NO_EXPERIMENT)`**
- **C07 Operational Status:** `EXPERIMENT_REQUIRED / O1_FEASIBILITY_BLOCKED`

---

## 2. Existing Observer Architecture & Limitations

### 2.1 The Existing `effects.jsonl` Harness
In the historical Android Phase 1 evaluation (AVD Pixel 7, Android 34):
- The test harness submits a command through ADB to the SUT application (`com.example.tmc`).
- When authorized, the application-internal callback invokes `DemoFixture::recordEffect()`, which writes a JSON string line directly into `/data/data/com.example.tmc/files/effects.jsonl`.
- The test harness executes `adb exec-out run-as com.example.tmc cat files/effects.jsonl` to inspect this marker.

### 2.2 Inherent Epistemic Limitations of `effects.jsonl`
1. **SUT Self-Reporting:** The file is entirely authored within the memory boundary and process context of the System Under Test.
2. **No Target-Side Isolation:** The marker indicates only that the application reached an internal logging branch; it provides zero direct evidence of an authoritative downstream target state modification.
3. **Inability to Detect Bypasses or Failures:** If execution bypasses the boundary and triggers an unmediated side effect, `effects.jsonl` will still record `false` or remain absent. Conversely, if an internal exception occurs downstream after logging, `effects.jsonl` records `true` even if the target effect never committed.
4. **Epistemic Invariant:**
   $$\text{TARGET\_MARKER} \neq \text{INDEPENDENT\_TARGET\_OBSERVATION}$$
   $$\text{SUT SELF-REPORT} \neq O_1$$

---

## 3. Candidate $O_1$ Inventory & Independence Assessment

An exhaustive audit of all observation mechanisms in the repository reveals three candidate tracks:

| Candidate Mechanism | Process / Identity Separation | Directly Observes Downstream Target? | Independent of `effects.jsonl`? | Target-Side Evidence Available? | Verified Identity / Lineage Binding? | Runtime Authorization Status | Audit Assessment |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate 1: App Sandbox `effects.jsonl`** | **NO** (In-process SUT) | **NO** (Private file) | **NO** (Identical) | **NO** | YES (Historical runs) | N/A (Existing) | **DISQUALIFIED** (SUT Self-Report) |
| **Candidate 2: Host ADB `run-as` Retrieval** | **PARTIAL** (Host script) | **NO** (Reads app sandbox) | **NO** (Depends 100% on app file) | **NO** | YES (Historical runs) | N/A (Existing) | **DISQUALIFIED** (Secondary Transport of SUT Self-Report) |
| **Candidate 3: Windows $B_1/O_1$ Prototype** (`implementations/e1_tmc_b1_o1/`) | **YES** (Separate Named Pipe process) | **YES in design** (Named Pipe target counter) | **YES in design** | **NO** (Zero operational traces) | **NO** (R6 missing correlation; R7 halted at preflight) | **NONE** (`RUNTIME_ISOLATION_STATUS = HOLD`) | **BLOCKED / NOT OPERATIONAL** (Design only; calibration unverified) |

---

## 4. Rigorous Candidate Evaluation

### 4.1 Candidate 1 & 2: App Sandbox / Host-side ADB
- **Evaluation:** Both mechanisms are bound to the internal behavior of the SUT. Under the strict requirements of Vajra Epistemic Rules and VEP governance, SUT self-reporting cannot validate its own containment or downstream efficacy.
- **Result:** Formally disqualified as $O_1$ candidates.

### 4.2 Candidate 3: $B_1/O_1$ Prototype (`implementations/e1_tmc_b1_o1/`)
- **Evaluation:**
  - *Implemented vs Executed:* Implementation files and test structures exist, but **`IMPLEMENTED != EXECUTED`**.
  - *Target-side evidence:* In runtime preflight tests (R6, R7), the PEP process was unobserved, the $B_1$ dispatch was unobserved, and causal correlation between client action and $B_1$ target state was not established.
  - *Identity / Binding:* The target identity crosswalk and named-pipe security descriptors remain incomplete.
  - *Authorization:* Runtime authorization was explicitly denied/frozen (`R7_FORENSIC_STATUS = COMPLETE_WITH_GAPS`, `RUNTIME_ISOLATION_STATUS = HOLD`).
- **Result:** Not operational. It remains a conceptual design and is not an eligible $O_1$ observer for active verification.

---

## 5. Feasibility Reconciliation Result

```text
================================================================================
TMC-C07 INDEPENDENT O1 OBSERVER FEASIBILITY DETERMINATION
================================================================================
O1_FEASIBILITY           = BLOCKED
OBSERVER_STATUS          = NON_INDEPENDENT_OBSERVER
AVAILABLE_O1_CANDIDATE   = NONE_QUALIFIED
CURRENT_C07_DISPOSITION  = CATEGORY_D (NARROWED_NO_EXPERIMENT)
================================================================================
```

### Minimum Essential Gaps Required for Future Unblocking:
1. **Isolated Downstream Target Service:** An external, stateful service with a hardened process/security boundary independent of the SUT.
2. **Dedicated Out-of-Band Observation Channel:** An $O_1$ reader query interface capable of polling target-side state without passing through the PEP or the SUT.
3. **Tamper-Resistant Target State Ledger:** Direct target-side evidence recording pre-state, post-state, timestamp, and transaction digest.
4. **Formal Isolation Challenge:** Empirical proof that disconnecting or falsifying SUT logging does not corrupt or alter the $O_1$ observation.
5. **Human EPA Runtime Authorization:** Explicit Human EPA sign-off approving a newly specified E7 intake contract prior to any preflight or execution.

---

## 6. Strict Epistemic & Governance Boundaries

- **`O1_FEASIBILITY = BLOCKED`**
- **`NO EXPERIMENT AUTHORIZED`**
- **`NO RUNTIME EXECUTION`**
- **`NO CLAIM PROMOTION`**
- **`NO SCOPE EXPANSION`**
- **`NO SYNTHETIC EVIDENCE GENERATION`**
- **`NO CONVERSION OF SUT SELF-REPORT TO O1`**
- **`SUBMITTED_PAPER_MODIFICATION = NONE`**
- **`PRODUCTION_CODE_MODIFICATION = NONE`**
- **`CANONICAL_MODIFICATION = NONE`**
- **`CLAIM_CLOSURE_GATE_MODIFICATION = NONE`**
- **`CLAIM_01_DISPOSITION_MODIFICATION = NONE`**
