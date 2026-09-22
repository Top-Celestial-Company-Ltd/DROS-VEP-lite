# VEP Bilingual Delivery Manifest

**Date:** 2026-09-21  
**Policy:** English files are canonical for raw evidence and full command detail; Chinese files are claim-aligned companion reports. Neither companion enlarges the evidence scope.

| English canonical | Chinese companion | Coverage |
|---|---|---|
| `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md` | `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5_ZH.md` | M5.1 tracks, metrics, hypotheses, limitations, evidence boundary |
| `reports/benchmarks/post_compromise/appendix_d_full_report.md` | `reports/benchmarks/post_compromise/appendix_d_full_report_ZH.md` | Appendix D experiment index, validator suites, raw-artifact boundary |
| `reports/PREFLIGHT_REPORT.md` | `reports/PREFLIGHT_REPORT_ZH.md` | M6 pre-flight status, Ubuntu build, C ABI inventory, oracle feasibility, stop condition |
| `reports/benchmarks/post_compromise/cli_execution_boundary/EXEC_BOUNDARY_15_CLOSURE_REPORT_EN.md` | `reports/benchmarks/post_compromise/cli_execution_boundary/EXEC_BOUNDARY_15_CLOSURE_REPORT_ZH.md` | Phase 2 EXEC-BOUNDARY-15 closure, candidate matrix, substrate evidence, claim boundary |

## Evidence rule

The `EXP-*` directories, JSON manifests, JSONL evidence, and source/test harnesses remain the authoritative machine-readable evidence. Reports must be read with their recorded environment, experiment ID, measurement boundary, and claim limitations. A `PASS` test result does not by itself establish a universal security property.
