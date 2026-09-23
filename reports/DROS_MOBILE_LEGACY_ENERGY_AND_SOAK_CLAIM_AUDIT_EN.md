# Audit of Legacy Mobile Energy and Soak-Test Claims

**Audit date:** 2026-09-23 | **Scope:** Legacy mobile SDK host harness, system-overhead report, and 24-hour soak aggregate
**Purpose:** Separate historical reported values from evidence that can currently be reproduced and independently checked.

## Findings

| Claim | Evidence inspected | Audit status | Permitted description |
|---|---|---|---|
| Mobile `P50=1.70 μs`, `P99=7.30 μs` | `test_mobile_attacks.py` calls `KotlinDROSClient`; that adapter delegates to `SwiftDROSClient`, which loads a Windows DLL through Python `ctypes`. The harness records host `perf_counter_ns`; it does not run Android JNI, iOS Swift, or a device runtime. Raw latency samples are not archived. | **Reported host-side adapter timing; not device-verified or raw-reconstructable.** | At most, describe as historical host-side C-ABI adapter timing, not mobile-device latency. |
| Battery `<0.001 mAh / 10k calls` | The test prints this fixed estimate; no current, voltage, energy sample, calculation inputs, calibrated meter, Batterystats trace, or power-profile artifact is included. | **Do not claim as a measurement.** | The legacy harness emitted an unvalidated estimate; omit the numeric value from product and paper claims. |
| Energy `<0.05 μJ / invocation` | Appears in the legacy report without a derivation, instrument, raw trace, or calibration procedure. | **Do not claim as a measurement.** | No quantitative energy claim. |
| `0 KB` network egress in the mobile energy claim | The cited harness does not include network packet/accounting instrumentation. | **Not measured by this harness.** | Do not present as a measured network result. |
| `0 Bytes` memory leak during a 24-hour soak | `scripts/run_24h_soak_test.py` exists, but it does not collect heap/RSS/profile data. The JSON aggregate contains no memory fields or raw memory profile. | **Reported; not independently verifiable from the current artifact set.** | Preserve only as a historical report statement with this limitation; do not call Verified. |
| `100%` attack interception in the 24-hour report | The aggregate records 160,611 total, 137,751 denied, 22,854 allowed, and 6 errors; its `containment_rate_percent` is 85.77. It does not provide a separate malicious-request denominator or per-request classifications. | **The 100% malicious-blocking claim is not reconstructable from the aggregate.** | Report the aggregate counts and denominator; do not infer a 100% rate. |

## Reproduction and scope notes

The legacy mobile adapter exercises the native library from a host process through an emulated API wrapper. It is not a physical-device or Android AVD energy test. The current TMC Android lane is a separate Pixel_7 / Android 34 / x86_64 application-runtime study and explicitly excludes physical energy measurement; it does not validate these legacy energy estimates.

The 24-hour runner exists, but selects scenarios randomly without a recorded seed, keeps latency samples only in memory, and writes a summary to the fixed path `reports/soak_test_24h_report.json`. Re-running it would create a new stochastic run and overwrite that summary; it would not exactly replay the archived run. The JSON is an aggregate record, not a raw event stream, and the runner has no memory-profiling instrumentation. Therefore exact replay, raw-to-summary reconstruction, and the `0 Bytes` memory claim are not established.

## Closure criteria for any future energy claim

Before restoring a numeric battery/energy statement, add a declared device and workload, calibrated physical measurement method (or clearly named software estimator), baseline/control procedure, warm-up and sample protocol, raw traces, analysis code, and a hash-closed evidence record. A modeled estimate must remain labeled as modeled and must not be described as physical measurement.
