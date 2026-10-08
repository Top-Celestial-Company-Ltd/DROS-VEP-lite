# PGM-VEP2-FRESH-24H-20261007-01 — HUMAN ACCEPTANCE

Date: 2026-10-08 13:16:50 +0800

## Decision

HUMAN_ACCEPTANCE = ACCEPTED

## Evidence State

EVIDENCE_GENERATED = YES
EVIDENCE_INTEGRITY_CHECKED = YES
EVIDENCE_HUMAN_VERIFIED = YES
CLAIM_SUPPORTED = PENDING
PUBLIC_PROMOTION = NOT_AUTHORIZED
RELEASE_AUTHORIZATION = NOT_GRANTED

## Accepted Evidence

Run ID:

`PGM-VEP2-FRESH-24H-20261007-01`

Execution node:

`Agent-server / 192.168.100.31`

Source commit:

`4c3e43c502657382e13b0e86d5c9f3807f32da01`

Raw observations:

268,120 records

Errors:

0

Timeouts:

0

Crashes:

0

Internal PDP:

- P50 = 18.99 us
- P95 = 27.24 us
- P99 = 47.78 us
- P99.9 = 57.03 us
- MAX = 97.36 us

Client E2E:

- P50 = 4.37658 ms
- P95 = 9.70269 ms
- P99 = 10.40944 ms
- P99.9 = 30.14521 ms
- MAX = 360.04845 ms

## Forensic Acceptance Basis

The following were independently verified:

1. 24-hour duration.
2. Exact run identity.
3. 268,120 raw records.
4. Continuous sequence IDs from 1 through 268,120.
5. JSON validity.
6. Required measurement fields.
7. Measurement-domain separation between internal PDP and client E2E.
8. Allow/deny counts recomputed from raw.
9. Percentiles independently recomputed from raw.
10. Derived results reconciled with raw evidence.
11. All 48 declared artifact hashes verified.
12. Hash manifest does not self-reference.
13. Frozen source repository remained clean.
14. Frozen source commit matched the experiment manifest.
15. External latency outliers were preserved.

## Governance Boundary

This acceptance verifies the evidence package.

It does NOT automatically establish or promote any public claim.

Historical benchmark values remain classified as historical unless separately reproduced.

Any claim promotion requires an explicit evidence-to-claim mapping and separate human authorization.

## Human Decision

The PGM 24-hour fresh evidence package is accepted as:

`VERIFIED_EVIDENCE`

The associated public performance claim remains:

`CLAIM_SUPPORTED = PENDING`

No publication, GitHub push, Zenodo release, or Canonical mutation is authorized by this record.

---

Human Acceptance Authority:

Jimmy Chen

Decision:

ACCEPTED
