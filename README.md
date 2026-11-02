# Research Evidence — DROS-6P: A Deterministic Runtime Governance Architecture for Six Trust Boundaries in Enterprise AI Agents

This repository contains the curated, sanitized research evidence supporting the empirical evaluation presented in the IEEE ICA 2026 paper:

> **DROS-6P: A Deterministic Runtime Governance Architecture for Six Trust Boundaries in Enterprise AI Agents**  
> *IEEE International Conference on Agents (ICA 2026)*

The materials are provided strictly for academic examination, peer review, and independent result reanalysis of the reported empirical figures without requiring access to proprietary DROS core implementation code.

---

## Research Evidence and Intellectual Property Notice

This repository contains publicly available research evidence supporting the DROS-6P paper presented at IEEE ICA 2026.

The materials are provided for academic examination, verification, and independent reanalysis of reported research results.

**All rights reserved. This repository is not an open-source software distribution or an open-data release.**

Permission is granted to download and analyze the published research evidence for non-commercial academic research and independent result verification, with appropriate attribution.

Redistribution, modification and republication of the datasets, commercial exploitation, and incorporation into commercial products require separate written permission, except where otherwise permitted by applicable law.

The proprietary DROS implementation, source code, internal test harnesses, and deployment materials are not included.

Certain aspects of DROS are patent pending. No patent license or right to implement the proprietary DROS technology is granted by publication of these materials.

Copyright © 2026 Top-Celestial Company Ltd. (康宸園有限公司). All rights reserved.

This research evidence repository is maintained by Top-Celestial Company Ltd.

The DROS implementation remains proprietary. Permission for non-commercial academic examination and independent result reanalysis is governed by the Research Evidence and Intellectual Property Notice. No open-source software license or patent implementation license is granted.

---

## Repository Structure

```text
DROS-6P-Research-Evidence/
├── README.md                      # This document (scope, reanalysis guidelines, IP notice)
├── CLAIM_EVIDENCE_INDEX.csv       # Claim-by-claim mapping from paper to evidence datasets
├── METHODS_AND_LIMITATIONS.md     # Measurement methods, quantile definitions, hardware profiles
├── CORRECTIONS_AND_DISCLOSURES.md # Documented discrepancies, limitations, and negative observations
├── SHA256SUMS                     # Integrity checksum manifest for all repository files
└── data/                          # Sanitized research datasets for independent reanalysis
    ├── receiver_audit_reconciliation_900.csv  # 900-request Receiver audit reconciliation (M01-M04)
    ├── audit_tampering_trials_8.csv           # 8 injected audit tampering trials (M05)
    ├── receiver_crash_trials_5.csv            # 5 kill-recovery trials / 416 acknowledged records (M06)
    ├── audit_ring_saturation.csv              # Volatile audit ring saturation summary (M07)
    ├── fixed_bitmap_context_pairs.csv         # 16-row fixed bitmap policy context pairs (M09)
    ├── rcu_dynamic_policy_8000.csv            # 8,000 RCU policy reload evaluation records (M10)
    ├── reload_latency_samples_2000.csv        # 2,000 full policy reload latency samples (M11)
    ├── atomic_publication_samples_50000.csv   # 50,000 atomic pointer publication samples (M12)
    ├── m17_authenticated_path_63.csv          # 63 authenticated path evaluation requests (M17-A/B)
    ├── m17_contextual_cases_27.csv            # 27 contextual decision cases (M17-C)
    ├── m17_control_fixtures_1200.csv          # 1,200 repeated control fixture outcomes (M17-D)
    └── t07_latency_summary.csv                # Table IV Runtime Decision Cost latency summary (M18)
```

---

## Level-A Independent Result Reanalysis Framework

Across the 20 main claims of the paper (M01–M20), empirical evidence is structured into three explicit categories:
- **PUBLICLY_REANALYZABLE (10 Claims / 50.0%):** M01, M02, M03, M04, M05, M06, M09, M10, M11, M12. Complete row-level or trial-level observations are provided; exact numeric outcomes are independently reproducible.
- **PARTIALLY_PUBLICLY_REANALYZABLE (3 Claims / 15.0%):** M07 (3-row ring saturation summary), M17 (sub-evidence 63/27/1200 numerically verified; categorical and wording caveats disclosed), M18 (Table IV 9-row summary quantiles).
- **NOT_PUBLICLY_REANALYZABLE (7 Claims / 35.0%):** M08 (raw 22+8 execution records held private; 16 vs 22 note discrepancy disclosed), M13/M14 (2,880 rounds Linux soak log held private), M15 (build log), M16 (ring abort zero file), M19 (C-ABI OS bypass negative observation), M20 (in-memory correlation).

### Reanalysis Verification Instructions:

1. **Table III Controlled Evidence:**
   - **M01 (400 Committed Audit Records):** In `data/receiver_audit_reconciliation_900.csv`, filter `observed_effect == 'COMMITTED'`. Exactly 400 rows are returned with contiguous sequence numbers 1 to 400.
   - **M02 (900 Harness Request Composition):** Group `data/receiver_audit_reconciliation_900.csv` by scenario prefix. The 6 scenarios sum to exactly 900 rows ($400 + 100 \times 5$).
   - **M03 (80/80 Injected WAL Failures):** Filter `data/receiver_audit_reconciliation_900.csv` for scenario `F_injected_wal_failure`. Exactly 80 HTTP 500 records with state reservation retained are verified.
   - **M04 (50/50 Filesystem Error Injections):** Filter `data/receiver_audit_reconciliation_900.csv` for scenarios `E1` and `E2`. Exactly 50 HTTP 503 and 50 HTTP 500 records are verified.
   - **M05 (5/8 Tamper Detection):** In `data/audit_tampering_trials_8.csv`, group by classification. Exactly 5 trials are flagged as `TAMPER_DETECTION_OBSERVED` and 3 trials as `TAMPER_NOT_DETECTED`.
   - **M06 (416 Acknowledged Records Post-Crash):** In `data/receiver_crash_trials_5.csv`, summing `acked_200` across trials 1–5 ($114 + 92 + 70 + 55 + 85$) yields exactly 416 acknowledged records with 0 missing or torn records.
   - **M07 (Audit Ring Saturation Summary):** In `data/audit_ring_saturation.csv`, 3 summary rows verify capacity 4,096, attempted 6,000, and 1,904 dropped. Raw event push stream is held private.
   - **M09 (16 Fixed Bitmap Context Pairs):** In `data/fixed_bitmap_context_pairs.csv`, 16 rows evaluate 8 authorized/unauthorized context pairs under identical bitmasks.
   - **M10 (7,902 Post-Reload Denials):** In `data/rcu_dynamic_policy_8000.csv`, filtering `req_class == 'CLASS_C_POST_RELOAD'` verifies exactly 7,902 requests evaluated as `DENY` with 0 linearizability violations; 84 pre-reload requests as `ALLOW`; and 14 overlapping requests (11 `ALLOW`, 3 `DENY`). Note that `worker_id` values (0–7) represent anonymized worker thread indices.
   - **M17 (Authenticated Path Sub-Evidence):**
     - *M17-A/B:* In `data/m17_authenticated_path_63.csv`, 63 evaluation requests yield 12 `ALLOW` and 51 `DENY`, with 60/60 expected matched decisions and 3 observation-only ALLOWs.
     - *M17-C:* In `data/m17_contextual_cases_27.csv`, exactly 27 rows match expected outcomes (22 DCT decision cases + 5 posture checks).
     - *M17-D:* In `data/m17_control_fixtures_1200.csv`, exactly 30 distinct fixtures ($A00\dots A09, P00\dots P04, D00\dots D04, U00\dots U04, X00\dots X04$) repeated across 40 iterations yield 600 `ALLOW` and 600 `DENY` with 0 false classifications.

2. **Table IV Performance and Decision Latency:**
   - **M11 (Policy Reload Latency):** In `data/reload_latency_samples_2000.csv`, computing the rounded order-statistic index $\text{round}(p \times 999)$ over sorted samples yields Config A $p_{50} = 384.60\ \mu\text{s}, p_{99} = 4012.40\ \mu\text{s}$ and Config B $p_{50} = 478.90\ \mu\text{s}, p_{99} = 5075.60\ \mu\text{s}$.
   - **M12 (Atomic Pointer Publication Latency):** In `data/atomic_publication_samples_50000.csv`, computing median latencies across reader concurrency levels ($0, 1, 2, 4, 8$) confirms median publication latencies within $800 \dots 1,900\ \text{ns}$.
   - **M18 (Runtime Decision Cost Summary):** In `data/t07_latency_summary.csv`, summary quantiles for $N=270,500$ benchmark invocations confirm $p_{50} = 900\ \text{ns}, p_{99} = 1,900\ \text{ns}$ at concurrency 1, and $p_{50} = 1,600\ \text{ns}, p_{99} = 2,600 \dots 4,400\ \text{ns}$ under concurrency 5–50. Note that underlying raw microbenchmark traces are held private.

3. **Documented Disclosures and Limitations:**
   - Refer to `CORRECTIONS_AND_DISCLOSURES.md` and `METHODS_AND_LIMITATIONS.md` for documented textual discrepancies (M08 recovery note count vs. raw record count), categorical classification nuances (M17-C and M17-D), and five fundamental architectural negative observations (M03, M05, M07/M16, M17-B, M19).
