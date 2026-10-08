# VEP 2.0 — RUNTIME EVIDENCE RECOVERY BUNDLE: FORENSIC REPORT

**Generated:** 2026-10-08 13:38:30 +0800  
**Human Execution Authority:** Jimmy Chen  
**Execution Host:** `ai_user@192.168.100.31` (Target Server: `agentserver`)  
**OS/Substrate:** `Linux agentserver 6.8.0-142-generic #142-Ubuntu SMP PREEMPT_DYNAMIC x86_64`  
**CPU:** `Intel(R) Core(TM) i5-3450 CPU @ 3.10GHz`  
**Runtime:** `Python 3.12.3` (Native Python, `COMPILED_BINARY = NOT_APPLICABLE`)  

---

## 1. Execution Status Summary

| Experiment ID | Experiment Name | Protocol Target | Raw Samples | Primary Metric | Protocol Verdict |
|---|---|---|:---:|---|:---:|
| **01-RCU** | RCU Policy Swap | Deterministic policy hot-swap without torn reads | 7,428 reader reads / 5 consecutive swaps | Mean Swap Latency: **1.96 µs**<br>Torn Updates: **0** | **PASS** |
| **02-M5** | M5 Runtime Enforcement | Real boundary enforcement (ALLOW/DENY + Downstream effect) | 6 boundary probes | Downstream Match: **100% (6/6)**<br>Decision Match: **100% (6/6)** | **PASS** |
| **03-PDP** | PDP Microbenchmark | Pure O(1) bitmap PDP evaluation (No network/IO) | 100,000 raw requests | P50: **0.730 µs** (730 ns)<br>P99: **1.223 µs** (1,223 ns)<br>Max: **13.482 µs** | **PASS** |

---

## 2. Frozen Source Identity & SHA-256 Hashes

* **Source Commit Identity:** `4c3e43c502657382e13b0e86d5c9f3807f32da01`
* **Frozen Source Files:**
  * `dros_guard.py` SHA256: `a8c3018d482431a435eb53859ec85a5606ab1c1a95a8d1e487878a03e69463f3`
  * `mock_services.py` SHA256: `24438fc1e75fb5b3877104808c79ec5b49dfb0bb9adf302c8b4fd9c39a55eb14`
* **VEP Review HEAD:** `0b80533634d5be630ae15ef913609b4b64f192f2`

---

## 3. Detailed Results by Protocol

### 3.1 Protocol 01-RCU: Policy Swap Verification
* **Policy A SHA256:** `f045cc23b59468c11b5575a7c2c088c7518178da1a0ddc1ab9e60e62ea4e84a3` (Inventory ALLOW, Finance DENY)
* **Policy B SHA256:** `f034e17f1efe0c5d9e40324d6892227c8a517202cd43f67b2bc0546263d2e6e8` (Inventory DENY, Finance ALLOW)
* **Concurrence & Threading:** 4 background reader threads continuously probing policy state during swap operations.
* **Torn Updates Observed:** `0` (Zero instances of inconsistent or partially-written policy states observed across 7,428 queries).
* **Swap Events Observed:**
  * SWAP-1 (A → B): Prep = 3.14 µs, Swap = 2.25 µs
  * SWAP-2 (B → A): Prep = 3.99 µs, Swap = 2.12 µs
  * SWAP-3 (A → B): Prep = 3.06 µs, Swap = 1.81 µs
  * SWAP-4 (B → A): Prep = 2.69 µs, Swap = 1.40 µs
  * SWAP-5 (A → B): Prep = 3.63 µs, Swap = 2.21 µs
  * **Mean Publication Latency:** **1.96 µs** (1,956.4 ns)
* **Final Policy Hash Match:** `True` (Target matches Policy B SHA256 exactly).
* **Verdict:** **PASS**

### 3.2 Protocol 02-M5: Runtime Enforcement Verification
* **Objective:** Verify physical enforcement rather than mere reporting (`DENY` + downstream action did not execute; `ALLOW` + downstream action executed).
* **Target Ports:** Mock ERP (`18081`), DROS Guard PEP/PDP (`18082`).
* **Test Matrix Verification:**
  1. `M5-001` (Authorized Principal & Action): `Observed = ALLOW (200)`, Downstream Executed = `True` → **PASS**
  2. `M5-002` (Unauthorized Principal / Rogue Role): `Observed = DENY (403)`, Downstream Executed = `False` → **PASS**
  3. `M5-003` (Authorized Principal on Prohibited Action): `Observed = DENY (403)`, Downstream Executed = `False` → **PASS**
  4. `M5-004` (Missing/Invalid Identity Binding): `Observed = DENY (403)`, Downstream Executed = `False` → **PASS**
  5. `M5-005` (Prohibited DevOps Endpoint for Support): `Observed = DENY (403)`, Downstream Executed = `False` → **PASS**
  6. `M5-006` (CISO Authorized for Finance): `Observed = ALLOW (200)`, Downstream Executed = `True` → **PASS**
* **Verdict:** **PASS** (100% enforcement consistency across all 6 test cases).

### 3.3 Protocol 03-PDP: Pure Microbenchmark
* **Measurement Boundary:** Strictly inside `evaluate_pdp_pure` (`request enters PDP → policy evaluation → decision returned`), excluding network sockets, HTTP serialization, logging, and disk I/O.
* **Warmup:** 5,000 iterations.
* **Total Sample Count:** 100,000 raw observations across 5 distinct classes.
* **Percentile Distribution (All Classes Combined):**
  * **Min:** 0.615 µs (615 ns)
  * **P50:** **0.730 µs** (730 ns)
  * **P95:** 0.947 µs (947 ns)
  * **P99:** **1.223 µs** (1,223 ns)
  * **P99.9:** 1.354 µs (1,354 ns)
  * **Mean:** 0.800 µs (799.7 ns)
  * **Max:** 13.482 µs (13,482 ns) — *Outliers fully preserved without deletion or winsorization.*
* **Breakdown by Class:**
  * `PDP-001` (ALLOW): N=20,000, P50 = 0.712 µs, P99 = 0.974 µs
  * `PDP-002` (DENY): N=20,000, P50 = 0.909 µs, P99 = 1.262 µs
  * `PDP-003` (MIXED ALLOW/DENY): N=20,000, P50 = 0.854 µs, P99 = 1.264 µs
  * `PDP-004` (REPEATED IDENTICAL): N=20,000, P50 = 0.711 µs, P99 = 0.976 µs
  * `PDP-005` (VARYING HASH/PATHS): N=20,000, P50 = 0.821 µs, P99 = 1.013 µs
* **Verdict:** **PASS**

---

## 4. Raw Evidence & Manifest Integrity (SHA-256)

All artifacts are persisted under:
`E:\vscode\AI知識庫\DROS-VEP\Work\Evidence-Recovery\2026-10-08\RUNTIME-RECOVERY-BUNDLE\`

```text
09f3e7f8d1e864a08808848525331ec3f3f179a1416edffb8887f798439a0c1b  ./03-PDP/PDP_MICROBENCHMARK_REPORT.json
1c17c8dce9d932190d4ac75c42b5b0da391aa65583fcb5d7206a45bfa4fd8ee2  ./03-PDP/run_pdp.py
24438fc1e75fb5b3877104808c79ec5b49dfb0bb9adf302c8b4fd9c39a55eb14  ./source_frozen/mock_services.py
5fe30f597695e782e5dde3c16ab37b7f76cabccea6798f641ce11b4b9efb3e93  ./01-RCU/raw_rcu_events.jsonl
66e6a965d05f7c657a8866946fcb718ebe011f817d1ce26333eb38dfc679b494  ./02-M5/M5_ENFORCEMENT_REPORT.json
685206f761fb8d25ac3871a64a9775a74ffd8ef36885dfaf4cee2d1d624101f1  ./01-RCU/RCU_POLICY_SWAP_REPORT.json
a2d12f4905834f440dac6b851d7ffd54b07fe7b98c1c76bb2e8998c11a6dd007  ./02-M5/run_m5.py
a8c3018d482431a435eb53859ec85a5606ab1c1a95a8d1e487878a03e69463f3  ./source_frozen/dros_guard.py
acd1cdf0b06f83d3e733a90e6984474a0a01a160b781326a1df85bf3a2d759be  ./03-PDP/raw_observations.jsonl
d99da54dbb76798a8e046f2646cbaaffd111a78f6406f4a8f7db16e252f62160  ./02-M5/raw_enforcement_events.jsonl
f634e99f3520f237caeb033d7e4e31e9c49ff6a3268ef67ac345dce80ef69ca5  ./01-RCU/run_rcu.py
```

---

## 5. Environment Mutations and Deviations

* **Environment Mutation:** None on permanent system configuration.
  * Local test harness ports `18081` and `18082` were dynamically bound for M5 verification and terminated immediately upon completion.
  * No system packages, kernel parameters, CPU schedulers, or background daemons were modified.
* **Deviations from Protocol:** None. All tests ran strictly against frozen source commit `4c3e43c502657382e13b0e86d5c9f3807f32da01`.

---

## 6. Proposed Evidence Governance State

* **01-RCU:** `VERIFIED_EVIDENCE` (Pass criteria met, zero torn updates)
* **02-M5:** `VERIFIED_EVIDENCE` (Pass criteria met, 100% downstream enforcement concordance)
* **03-PDP:** `VERIFIED_EVIDENCE` (Pass criteria met, 100,000 raw samples reconciled)
* **Overall Bundle State:** `VERIFIED_EVIDENCE`
* **Claim Promotion:** `CLAIM_SUPPORTED = PENDING` (Remains pending separate Human Claim Authority review)
* **Public Promotion:** `NOT_AUTHORIZED`
* **Release Status:** `NOT_AUTHORIZED`

---

## 7. Canonical Integrity & Repository State

* **Canonical Mutation:** `NONE` (Canonical untouched)
* **Git Status:** All artifacts generated and synced reside exclusively under `Work/Evidence-Recovery/2026-10-08/`.
* **Git Commit / Push:** `NOT PERFORMED` (Strictly adhered to governance rule).
* **Governance Constraints:** NO COMMIT / NO PUSH / NO CANONICAL MUTATION / NO ZENODO.

