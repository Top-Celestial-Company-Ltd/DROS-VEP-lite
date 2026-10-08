# 📋 PGM-VEP2 Fresh 24-Hour Evidence Run: Human Summary

**Run Identifier:** `PGM-VEP2-FRESH-24H-20261007-01`  
**Execution Node:** `Agent-server` (`Intel Core i5-3450 @ 3.10GHz`, `Ubuntu 24.04 LTS`)  
**Duration:** `24.00 Hours` (`86,400.14 Seconds`)  
**Evidence Status:** `EVIDENCE_GENERATED = YES` (Pending Human Review)

---

### Observed Evaluation Results

During the 24-hour non-stop execution window, 268,120 total requests were generated and recorded under seed `20261007` across four predefined workload profiles (W-A steady, W-B mixed authorization, W-C bounded burst, W-D payload variation).

| Evaluation Metric | Observed Value | Scope / Definition |
| :--- | :--- | :--- |
| **Total Dispatched Requests** | 268,120 | Continuous 24h stream |
| **Observed Throughput** | 3.10 req/s | Sequential loop with predefined burst profiles |
| **ALLOW Decisions** | 45,140 (16.84%) | Authorized requests forwarded to target |
| **DENY Decisions** | 222,980 (83.16%) | Policy-blocked violations at PEP boundary |
| **Recorded Errors / Timeouts** | 0 / 0 | 100% operational completion rate |
| **Internal PDP Latency (P50)** | **18.99 μs** | In-memory bitmap evaluation + Ed25519 signature |
| **Internal PDP Latency (P90)** | **25.70 μs** | 90th percentile evaluation decision |
| **Internal PDP Latency (P99)** | **47.78 μs** | 99th percentile evaluation decision |
| **Internal PDP Latency (P99.9)** | **57.03 μs** | 99.9th percentile evaluation decision |
| **Internal PDP Latency (Max)** | **97.36 μs** | Single worst-case internal decision across 222,980 checks |
| **Internal PDP P99/P50 Ratio** | **2.52x** | Bounded tail ratio across 24h |
| **Client Socket E2E Latency (P50)** | **4,376.58 μs (4.38 ms)** | HTTP socket, TCP, Flask framework round-trip |
| **Client Socket E2E Latency (P99)** | **10,409.44 μs (10.41 ms)** | 99th percentile client HTTP round-trip |

---

### Non-Assertion Statements

* **Historical Baseline:** Archived historical soak values (P50 = 26.21 μs, P99 = 242.69 μs) are noted as `HISTORICAL_SPEC = NOT_REPRODUCIBLE` due to missing raw evidence and ambiguous boundaries. No claim of percentage speedup or slowdown is asserted.
* **Scope Boundary:** These measurements reflect empirical observations on an Intel i5-3450 host under the specific predefined workload profiles. They do not constitute an assertion of production performance across unexamined workloads.
