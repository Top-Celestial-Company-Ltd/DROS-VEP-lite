# DROS / VEP 2.0
# Runtime Evidence Recovery — 2026-10-08

Status: VERIFIED_EVIDENCE
Publication state: HUMAN REVIEW REQUIRED
Public Claim Promotion: NOT AUTHORIZED
Release Authorization: NOT GRANTED

## Purpose

This evidence package records fresh runtime evidence generated under the
VEP 2.0 Evidence Recovery Program.

The package reconciles four runtime evidence families:

1. PGM 24-hour runtime workload
2. PDP microbenchmark
3. RCU policy swap
4. M5 runtime enforcement

The evidence was generated on the frozen source/runtime environment and
subsequently subjected to human verification and SHA-256 reconciliation.

Historical benchmark numbers are NOT silently replaced.

---

# 1. PGM — 24H Runtime Evidence

Run ID:

PGM-VEP2-FRESH-24H-20261007-01

Environment:

- Ubuntu 24.04.4
- Linux 6.8.0-142
- Intel Core i5-3450
- Python 3.12.3
- 24 hours
- 268,120 raw observations
- 0 errors
- 0 timeouts
- 0 crashes

Fresh measurements:

Internal PDP:

- P50: 18.99 µs
- P95: 27.24 µs
- P99: 47.78 µs
- P99.9: 57.03 µs
- Max: 97.36 µs

Client E2E:

- P50: 4,376.58 µs
- P95: 9,702.69 µs
- P99: 10,409.44 µs
- P99.9: 30,145.21 µs
- Max: 360,048.45 µs

All raw observations and outliers are preserved.

Evidence status:

VERIFIED_EVIDENCE

Boundary:

This evidence supports the reported latency distribution under the specified
24-hour workload, source, environment, and measurement boundary.

It does NOT establish universal performance, hardware-independent latency,
or production-wide guarantees.

---

# 2. PDP Microbenchmark

Samples:

100,000

Fresh measurements:

- Min: 615 ns
- P50: 730 ns
- P95: 947 ns
- P99: 1,223 ns
- P99.9: 1,354 ns
- Mean: 800 ns
- Max: 13,482 ns

Evidence status:

VERIFIED_EVIDENCE

Boundary:

Only the PDP policy evaluation boundary was measured.

Network, HTTP, socket, logging, disk I/O, startup, and unrelated work were
excluded.

This supports only the measured latency distribution under the specified
environment and measurement boundary.

---

# 3. RCU Policy Swap

Observed:

- 7,428 reader observations
- 5 policy swaps
- Torn updates: 0
- Average swap publication latency: 1.96 µs
- Final policy state matched expected hash

Evidence status:

VERIFIED_EVIDENCE

Boundary:

The evidence supports the tested RCU policy-swap mechanism under the specified
workload.

It does NOT establish universal lock-free correctness, arbitrary concurrency
correctness, kernel mediation, formal verification, or production security.

---

# 4. M5 Runtime Enforcement

Cases:

6 / 6 PASS

Verified behaviors:

- Authorized request → ALLOW → downstream execution
- Unauthorized principal → DENY → downstream blocked
- Unauthorized action → DENY → downstream blocked
- Missing identity binding → DENY → downstream blocked
- Unauthorized devops action → DENY → downstream blocked
- Authorized CISO finance action → ALLOW → downstream execution

Decision agreement:

100%

Downstream-effect agreement:

100%

Evidence status:

VERIFIED_EVIDENCE

Boundary:

The evidence supports the tested controlled runtime enforcement boundary.

It does NOT establish complete mediation across the operating system,
raw-syscall immunity, arbitrary application integration, universal
authorization correctness, or production security.

---

# 5. Historical Number Policy

Historical values remain classified as:

HISTORICAL_REPORTED_RESULT

Fresh values remain classified as:

VERIFIED_EVIDENCE

Fresh evidence does not silently overwrite historical measurements.

Any transition to a public claim requires separate human authorization.

---

# 6. Governance

EVIDENCE_GENERATED = YES

EVIDENCE_INTEGRITY_CHECKED = YES

EVIDENCE_HUMAN_VERIFIED = YES

CLAIM_SUPPORTED = PENDING

PUBLIC_PROMOTION = NOT_AUTHORIZED

RELEASE_AUTHORIZATION = NOT_GRANTED

COMMIT = NO

PUSH = NO

CANONICAL_MUTATION = NO

ZENODO = NO

---

# 7. Future Evidence Recovery Candidates

Completed:

- PGM 24H
- PDP microbenchmark
- RCU policy swap
- M5 runtime enforcement

Optional future robustness work:

- Cross-environment PDP / RCU / M5 validation
- Stronger execution-boundary / bypass-resistance validation

Deferred unless a specific public claim requires them:

- Historical 72H PGM
- Historical DROS vs ScopeGate / OPA comparison

PX4 S2-D remains:

NOT_PROVEN

and is not reopened by this evidence package.

---

# 8. Promotion Rule

This package is an evidence record.

It is NOT a public claim authorization.

No claim may be promoted merely because an experiment passed.

Human Evidence Promotion Authority remains required.
