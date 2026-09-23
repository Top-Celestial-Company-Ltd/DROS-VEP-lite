# DROS-Mobile Android Baseline Evidence Index

Status: **Phase 1–2 Android baseline evidence indexed and closed**

Scope: `Pixel_7` AVD / Android 34 / x86_64 / declared application-runtime boundary.

## Canonical evidence map

| Artifact | Lane | Evidence | Status |
|---|---|---|---|
| T4 | Security semantics | Unauthorized execution denied before effect | Closed / immutable |
| T5 | Security semantics | Authorized bounded execution | Closed / immutable |
| T7 | Security semantics | Revocation prevents subsequent effect | Closed / immutable |
| T9 | Decision latency | DENY raw measurement + tail characterization | Closed / immutable |
| T10 | Decision latency | ALLOW raw measurement | Closed / immutable |
| T14 | Concurrency prerequisite | 2 submitted = 2 received | Closed / immutable |
| T15 | C1 accounting | 2 = 2 = 2 = 2 pipeline records | Closed / immutable |
| T16 | C1 performance | C1=2 throughput and decision latency | Closed / immutable |
| T17 | C2 accounting | 4 = 4 = 4 = 4 pipeline records | Closed / immutable |
| T18 | C2 performance | C2=4 throughput and decision latency | Closed / immutable |
| T19 | C3 accounting | 8 = 8 = 8 = 8 pipeline records | Closed / immutable |
| T20 | C3 performance | C3=8 throughput and decision latency | Closed / immutable |

The machine-readable index, including closure hashes and provenance completeness, is [android_baseline_evidence_index.json](./android_baseline_evidence_index.json).

## Descriptive 2/4/8 series

| Concurrency | P50 | P95 | P99 | Host-observed throughput |
|---:|---:|---:|---:|---:|
| 2 / T16 | 715.7 μs | 1.8794 ms | 3.4942 ms | 15.7731 req/s |
| 4 / T18 | 896.1 μs | 5.5945 ms | 11.3106 ms | 14.0353 req/s |
| 8 / T20 | 859.1 μs | 6.4929 ms | 21.4807 ms | 16.5062 req/s |

Each performance run passed the accounting gate:

```text
100 submitted = 100 RECEIVED = 100 DISPATCHED = 100 RESULT
100 DENY; 0 execution; 0 effect
```

## Claim boundary

The series is a reproducible descriptive observation under the declared Android application-runtime measurement boundary. It is not an Android scalability law, saturation analysis, or causal explanation. T11/T12 remain failure provenance only because the earlier Activity ingress did not guarantee request/result pairing.

The index does not establish Android-wide, OS-level, Binder, SELinux, kernel, physical-device, energy, CPU, memory, or runtime-causal claims.
