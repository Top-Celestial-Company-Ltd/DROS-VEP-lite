# 🔬 PGM-VEP2 Fresh 24-Hour Evidence Forensic Report

**Experiment ID:** `PGM-VEP2-FRESH-24H-20261007-01`  
**Execution Node:** `Agent-server` (`node31` / `192.168.100.31`)  
**Timestamp Interval:** `2026-10-07T03:22:56Z` — `2026-10-08T03:22:56Z` (UTC)  
**Elapsed Duration:** `86,400.14 Seconds (24.00 Hours)`  
**Status:** `COMPLETED_AWAITING_HUMAN_REVIEW`

---

## 1. Governance & Execution Compliance

This experiment was conducted strictly under VEP 2.0 Hard Governance Rules as an automated execution run with full provenance.
* **Source/Enforcement Mutation:** None. All source files remained strictly frozen.
* **Workload Mutation:** None. Executed with declared PRNG seed `20261007` across profiles W-A, W-B, W-C, W-D without mid-run parameter changes.
* **Outlier / Error Treatment:** Zero outlier truncation or winsorization. All 268,120 raw observations preserved.
* **Promotion Status:** `NOT AUTHORIZED` (Pending Human Review).

---

## 2. Historical Baseline Separation (Auditable Context)

The archived historical soak benchmark recorded aggregate values:
* `Historical P50`: 26.21 μs
* `Historical P99`: 242.69 μs
* `Historical Requests`: 160,611

**Status:** `HISTORICAL_SPEC = NOT_REPRODUCIBLE`  
* The historical run did not preserve raw event traces, git commit SHAs, or random seeds, and exhibited measurement boundary ambiguity between client HTTP round-trips and internal PDP evaluations.
* **No comparative improvement/regression percentage is calculated against the historical report.**

---

## 3. Environment & Hardware Fingerprint

* **Host:** `agentserver`
* **CPU Model:** Intel(R) Core(TM) i5-3450 CPU @ 3.10GHz (4 Cores / 4 Threads)
* **Kernel & OS:** Linux 6.8.0-142-generic #142-Ubuntu SMP PREEMPT_DYNAMIC / Ubuntu 24.04.4 LTS
* **Memory & Storage:** 15 GiB RAM (13 GiB Free) / Root LVM 108.7 GiB (50 GiB Available after 24h)
* **CPU Frequency Policy:** `schedutil` governor / Active scaling ~3.28 GHz - 3.39 GHz
* **Clocksource:** `tsc` / NTP Synchronized
* **Background Isolation:** `nas-sync.service`, `synology-active-backup-business-linux-service.service`, and `dsh.service` confirmed inactive throughout run.

---

## 4. Source & Runtime Identity

* **Source Repository:** `DROS-VEP-lite` (`origin/main`)
* **Source Git Commit:** `4c3e43c502657382e13b0e86d5c9f3807f32da01` (Clean)
* **Runtime Substrate:** `NATIVE_PYTHON` (`Python 3.12.3`, `/usr/bin/python3`)
* **Compiled Binary:** `NOT_APPLICABLE`
* **Guard PEP Source SHA-256:** `a8c3018d482431a435eb53859ec85a5606ab1c1a95a8d1e487878a03e69463f3`
* **Runner Source SHA-256:** `3510e45d35a22bc13fa414498a8e836971ca0fe4ea90f1a78887e2ea05bc7788`
* **Workload Generator SHA-256:** `bceabc2c705e3b0e2bad9dedbdbc7ef948e4417bcc9225f0fd3e53e740029854`

---

## 5. Workload Execution Breakdown

* **Duration:** 86,400.14 seconds
* **Total Requests Dispatched:** 268,120
* **Average Throughput:** 3.10 req/sec
* **Outcomes:** 45,140 ALLOW (16.84%) / 222,980 DENY (83.16%)
* **System Exceptions / Timeouts / Socket Errors:** **0 / 0 / 0** (100% Operational Availability)

### Profile Breakdown

| Workload Profile | Profile Description | Total Requests | RPS | ALLOW | DENY | Errors |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **W-A** | Steady Controlled (0.5s interval) | 66,908 | 0.77 | 11,289 | 55,619 | 0 |
| **W-B** | Mixed Authorization (Policy paths) | 50,161 | 0.58 | 8,362 | 41,799 | 0 |
| **W-C** | Burst / Tail (5-req bursts) | 126,080 | 1.46 | 21,260 | 104,820 | 0 |
| **W-D** | Payload Variation (Small/Med/Large) | 24,971 | 0.29 | 4,229 | 20,742 | 0 |
| **ALL** | **Full 24-Hour Combined Stream** | **268,120** | **3.10** | **45,140** | **222,980** | **0** |

---

## 6. Latency Distribution & Boundary Segregation

Percentile Calculation Method: Linear interpolation between closest ranks (NIST/SciPy compliant).

### 6.1 Metric A — Client-Side End-to-End HTTP Round-Trip (`client_e2e_latency_ns`)
Includes client socket, TCP, Flask HTTP stack, PEP evaluation, and ERP mock.

| Workload | Min (μs) | P50 (μs) | P90 (μs) | P95 (μs) | P99 (μs) | P99.9 (μs) | Max (μs) | Mean (μs) | StdDev (μs) | P99/P50 | P99.9/P50 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ALL** | 2,515.45 | 4,376.58 | 9,444.39 | 9,702.69 | 10,409.44 | 30,145.21 | 360,048.45 | 5,327.86 | 2,674.06 | **2.38x** | **6.89x** |
| **W-A** | 2,722.71 | 4,424.45 | 9,637.61 | 9,822.56 | 10,890.65 | 33,522.37 | 99,692.01 | 5,484.35 | 2,742.13 | 2.46x | 7.58x |
| **W-B** | 2,583.07 | 4,422.06 | 9,625.68 | 9,813.70 | 10,844.00 | 32,746.48 | 360,048.45 | 5,478.52 | 3,510.37 | 2.45x | 7.41x |
| **W-C** | 2,515.45 | 4,280.68 | 9,134.57 | 9,376.17 | 9,871.06 | 22,533.87 | 88,924.82 | 5,153.68 | 2,190.53 | 2.31x | 5.26x |
| **W-D** | 2,793.95 | 4,423.84 | 9,641.54 | 9,822.66 | 10,784.11 | 33,256.53 | 89,372.56 | 5,485.35 | 2,712.97 | 2.44x | 7.52x |

### 6.2 Metric B — Internal DROS Guard PDP Decision (`internal_pdp_latency_ns`)
Includes RFC-010 Bitmap/Hashtable lookup, role verification, and Ed25519 cryptographic token signing.

| Workload | Min (μs) | P50 (μs) | P90 (μs) | P95 (μs) | P99 (μs) | P99.9 (μs) | Max (μs) | Mean (μs) | StdDev (μs) | P99/P50 | P99.9/P50 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ALL** | 11.26 | **18.99** | 25.70 | 27.24 | **47.78** | **57.03** | 97.36 | 21.72 | 5.57 | **2.52x** | **3.00x** |
| **W-A** | 11.44 | 20.10 | 26.07 | 31.22 | 49.16 | 60.19 | 68.68 | 22.71 | 6.12 | 2.45x | 2.99x |
| **W-B** | 11.30 | 20.01 | 26.02 | 30.68 | 48.93 | 57.79 | 97.36 | 22.65 | 6.03 | 2.45x | 2.89x |
| **W-C** | 11.26 | 18.50 | 25.27 | 25.86 | 45.04 | 53.58 | 83.50 | 20.64 | 4.72 | 2.43x | 2.90x |
| **W-D** | 11.36 | 20.06 | 26.05 | 30.82 | 49.19 | 59.00 | 67.62 | 22.66 | 6.04 | 2.45x | 2.94x |

---

## 7. Forensic Anomalies & Tail Behavior Analysis

1. **Internal PDP Stability:**
   Across 222,980 evaluated policy decisions, the internal PDP median was **18.99 μs**, P99 was **47.78 μs**, and P99.9 was **57.03 μs**. The ratio $P99/P50$ remained bounded at **2.52x**, demonstrating no internal decision long-tail degradation over 24 continuous hours.
2. **Client-Side Outlier Observation:**
   A single maximum socket latency of **360.05 ms** was recorded in profile W-B (seq #46,012). Concurrently, the internal PDP latency for that request remained at **21.84 μs**, identifying this event as an external Flask/TCP socket buffer delay rather than a PDP evaluation stall. In accordance with rule 9/13, this outlier is preserved in raw records without filtering.
3. **Pre-Run Environmental Mutation:**
   As logged in the pre-start audit, `PRE_RUN_ENVIRONMENT_MUTATION = YES` was recorded due to clearing previous calibration instances before starting the frozen workload.

---

## 8. Evidence Artifacts & Verification Paths

* **Raw Observations:** `/home/ai_user/vep-fresh-24h/experiment/raw/observations.jsonl` (109 MB, 268,120 rows)
* **System Telemetry:** `/home/ai_user/vep-fresh-24h/experiment/raw/system_metrics.jsonl` (1,438 entries)
* **Errors Log:** `/home/ai_user/vep-fresh-24h/experiment/raw/errors.jsonl` (0 entries)
* **Machine Report:** `/home/ai_user/vep-fresh-24h/experiment/reports/results.json`
* **Evidence Manifest:** `/home/ai_user/vep-fresh-24h/experiment/hashes/sha256_manifest.txt`
