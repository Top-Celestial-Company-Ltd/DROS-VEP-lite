# Documented Provenance Disclosures, Corrections, and Negative Findings

This document catalogs the specific experimental caveats, wording discrepancies, provenance limitations, and candid negative observations documented in the IEEE ICA 2026 paper (*DROS-6P*) and confirmed across independent audit acceptances.

---

## 1. Disclosed Textual and Provenance Discrepancies

### 1.1 Claim M08: Discrepancy Between Recovery Notes (16) and Raw Records (22)
- **Paper Context:** Section III, Line 88.
- **Documented Fact:** The raw output logs for the S2 P3/P4 context evaluation contain **22 Rust case records** and **8 Go case records**. However, early engineering recovery notes indicated **16 Rust records**.
- **Resolution:** As formally disclosed in the paper manuscript (Line 88):
  > *"The original process logs of the S2 harness are unavailable, and a discrepancy between the recovery notes (16 Rust records) and the output (22) is unresolved."*
- **Audit Status:** Codex R3 independently classified M08 as `CONFLICTED` regarding execution provenance, while verifying the physical existence of the 22+8 records in the private output logs. The raw 22+8 execution records are held private and are not included in the public package. The public `fixed_bitmap_context_pairs.csv` dataset contains 16 rows representing the 8 policy context pairs of Claim M09 and does not represent M08 output records.

### 1.2 Claim M17-C: Classification of 27 Decision Cases
- **Paper Context:** Section III, Line 86 and Table III Line 99.
- **Documented Fact:** The paper text refers to *"27 canonicalization cases on the contextual-policy path produced no mismatches"*.
- **Data Reality:** As verified by Codex M17 Delta Acceptance, the 27 matching records in `data/m17_contextual_cases_27.csv` comprise:
  - **22 DCT policy evaluation cases** (testing prefix, tenant boundaries, dynamic values, and URI canonicalization).
  - **5 posture check unit validations** (`T02-P4a` through `T02-P4e`).
- **Disclosure:** The 27 cases are not 27 pure URI canonicalization tests. Two further static checks in the suite (`T02-P3` and `T02-P4`) were unconfigured in test builds and evaluated statically.

### 1.3 Claim M17-D: Benign Control Fixtures Wording and Categorical Mapping
- **Paper Context:** Section III, Line 86.
- **Documented Fact:** The paper text describes *"A benign control of 30 fixed inputs repeated 40 times produced 600 expected ALLOW decisions and no false denial"*.
- **Data Reality:** The underlying 30 fixture inputs in `data/m17_control_fixtures_1200.csv` generate 1,200 total outcomes:
  - Exactly **600 expected ALLOW outcomes** (15 distinct benign inputs $\times 40$ repetitions: A00–A09, P00–P04).
  - Exactly **600 expected DENY outcomes** (15 distinct policy-denial inputs $\times 40$ repetitions: D00–D04, U00–U04, X00–X04).
- **Disclosure:** The 30 inputs are not all benign fixtures; 15 are benign fixtures producing 600 ALLOWs, and 15 are control rejection fixtures producing 600 DENYs with zero false classifications.
- **Categorical Mapping Bound:** While the paper conceptually mentions "600 context-pair controls" and "600 prompt-mutation controls", the underlying test harness (`T03_compat.jsonl`) categorizes records strictly by fixture identifier (`A00`–`X04`) and iteration (`0`–`39`). There are no explicit categorical columns distinguishing context-pair from prompt-mutation in the raw logs. Therefore, the numerical outcome (600 ALLOW / 600 DENY / 0 errors) is 100% verified from data, but the context-pair vs. prompt-mutation partition is not verified as a standalone dataset feature.

---

## 2. Documented Negative Observations and Failure Findings

In accordance with academic integrity and anti-fraud protocols, the DROS-6P prototype evaluation explicitly documents five foundational architectural limitations:

### 2.1 Negative Observation 1: Semantic Argument Validation Gap (Claim M17-B)
- **Observation:** A correctly signed request carrying semantically abusive arguments (such as a negative transfer amount or an unlinked account ID) was evaluated as `ALLOW`.
- **Root Cause:** DROS-6P implements cryptographic hash binding between the authorization token and request arguments, but does not perform application-level semantic constraint validation.

### 2.2 Negative Observation 2: C-ABI Mediation vs. OS Physical Isolation (Claim M19)
- **Observation:** On an unconfined Windows host without kernel sandbox enforcement, a malicious or compromised worker process directly executed `std::fs::write` to an unmanaged file and established a raw TCP loopback socket, bypassing DROS mediation entirely.
- **Architectural Bound:** The C-ABI is a software-call authorization checkpoint, not an operating system sandbox. Physical containment requires complementary OS isolation primitives (such as Linux `seccomp-bpf` or hypervisor boundaries).

### 2.3 Negative Observation 3: Volatile In-Memory Audit Ring Saturation (Claim M07 & M16)
- **Observation:** Under high-concurrency burst conditions (6,000 pushes into a ring buffer sized for 4,096), the core ring buffer dropped **1,904 audit records**. Furthermore, after an abrupt process abort (`SIGKILL`), zero audit files remained on disk.
- **Architectural Bound:** The volatile in-memory ring buffer provides transient per-decision traceability only; durable event recovery requires asynchronous durable queues and caller backpressure.

### 2.4 Negative Observation 4: Non-Atomic Effect and WAL Failure (Claim M03)
- **Observation:** In 80 out of 80 injected WAL-completion failure trials, the downstream external effect occurred before the WAL failure occurred, resulting in `HTTP 500` while retaining the state reservation.
- **Architectural Bound:** The prototype effect-to-WAL pipeline lacks distributed transaction coordination (such as two-phase commit or saga rollback).

### 2.5 Negative Observation 5: Selective Tamper Detection in Unkeyed Audit Chains (Claim M05)
- **Observation:** The audit validation tool detected 5 out of 8 injected tampering cases (such as modified fields without CRC updates or deleted middle records), but accepted 3 cases (field modifications with recomputed CRCs, tail truncation of 10 records, and full chain recomputation).
- **Architectural Bound:** The unkeyed hash chain lacks HMAC signatures or external trusted timestamp anchors, leaving it vulnerable to coordinated offline chain reconstruction.
