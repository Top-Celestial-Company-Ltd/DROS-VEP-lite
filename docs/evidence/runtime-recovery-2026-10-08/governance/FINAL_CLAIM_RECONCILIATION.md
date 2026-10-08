# DROS / VEP 2.0 — FINAL CLAIM RECONCILIATION

Date: 2026-10-08

## Evidence Families

### RCU Policy Swap
Status: VERIFIED_EVIDENCE
Protocol result: PASS
Samples: 7,428 reads
Swaps: 5
Torn updates: 0
Average swap publication latency: 1.96 us
Final policy hash: reconciled

Supported boundary:
Under the tested workload and implementation, the tested RCU policy-swap mechanism produced no observed torn/partial policy state and reached the expected final policy state.

Not supported:
Universal lock-free correctness, arbitrary workloads, kernel mediation, production security, formal verification.

### M5 Runtime Enforcement
Status: VERIFIED_EVIDENCE
Protocol result: PASS
Cases: 6/6
Decision agreement: 100%
Downstream-effect agreement: 100%

Supported boundary:
Under the tested controlled enforcement boundary, authorized actions were permitted and unauthorized actions were denied, with downstream execution matching the expected enforcement result.

Not supported:
Complete mediation, raw-syscall immunity, arbitrary integrations, universal authorization correctness, production security.

### PDP Microbenchmark
Status: VERIFIED_EVIDENCE
Protocol result: PASS
Samples: 100,000
P50: 730 ns
P95: 947 ns
P99: 1,223 ns
P99.9: 1,354 ns
Mean: 800 ns
Max: 13,482 ns

Supported boundary:
Under the specified environment and measurement boundary, the tested PDP exhibited the reported latency distribution.

Not supported:
Hardware-independent latency, universal performance guarantees, end-to-end latency claims.

## Historical Number Policy

Historical benchmark values MUST NOT be silently replaced.

Historical values remain:
HISTORICAL_REPORTED_RESULT

Fresh measurements remain:
VERIFIED_EVIDENCE

Any public claim update requires separate human authorization.

## Claim Decision

Each historical claim shall be classified only as:

SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED

No automatic transition to CLAIM_SUPPORTED is permitted.

No public promotion is authorized by this artifact.

No Canonical mutation is authorized.

No Git commit is authorized.

No Git push is authorized.

No Zenodo update is authorized.

No release authorization is granted.

## Final Governance State

EVIDENCE_GENERATED=YES
EVIDENCE_INTEGRITY_CHECKED=YES
EVIDENCE_HUMAN_VERIFIED=YES
CLAIM_SUPPORTED=PENDING
PUBLIC_PROMOTION=NOT_AUTHORIZED
RELEASE_AUTHORIZATION=NOT_GRANTED

## Final Principle

The fresh evidence supersedes neither history nor governance by itself.

It provides a new verified evidence basis against which historical claims may be reconciled.

Human approval remains the Evidence Promotion Authority.
