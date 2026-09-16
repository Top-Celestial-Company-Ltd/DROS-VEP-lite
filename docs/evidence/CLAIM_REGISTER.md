# VEP Formal Claim Register (CLAIM_REGISTER.md)
* **Register ID**: CLAIM-REG-2026-v1.0
* **Status**: FROZEN_BASELINE
* **Protocol**: VEP-PLAN-2026-M5.1
* **Date**: 2026-09-16

---

## 1. Claim Classification Taxonomy
All claims must be tagged with strictly defined validation statuses:
* `VERIFIED`: Formally proven or mathematically demonstrated.
* `SUPPORTED UNDER REGISTERED MODEL`: Empirically validated on registered testbeds under declared attacker and measurement models.
* `OBSERVED`: Empirical observation within bounded experimental runs.
* `PARTIAL`: Partially achieved or dependent on external unverified assumptions.
* `UNSUPPORTED`: Claim refuted or lacking necessary evidence under tested conditions.

---

## 2. Active Claims Register

### CLAIM-01: Bare-Metal Crucible Containment
* **Statement**: Under the registered AAV-2026 threat model and 1,000 crucible attempts (902 unauthorized, 98 benign), DROS achieves 100% interception of unauthorized tool invocations with zero state drift ($\Delta\text{Effect} = 0$).
* **Definition**: $\text{UEIR} = 902 / 902 = 1.000000$.
* **Status**: `SUPPORTED UNDER REGISTERED MODEL`
* **Evidence Binding**: `reports/audit.jsonl` (SHA-256: `e60f4856...`), `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md` (§3).
* **Limitations**: Scoped to the 1,000 registered crucible attack vectors; does not claim zero-day protection outside declared mutations.

### CLAIM-02: Native C-ABI Decision Latency
* **Statement**: DROS GuardVM in-memory capability bitmask lookup and ArgHash verification operates at sub-microsecond P50 latency.
* **Definition**: Runtime PDP decision latency measured in-process at C-ABI boundary excluding external network/RPC I/O.
* **Status**: `SUPPORTED UNDER REGISTERED MODEL`
* **Evidence Binding**: `reports/benchmarks/post_compromise/EXP-1789532251-38a4fd/result.json` (P50: $7.8\ \mu\text{s}$ harness / $<1.0\ \mu\text{s}$ pure PDP).
* **Limitations**: Excludes end-to-end framework serialization and Python runtime dispatch overhead.

### CLAIM-03: Multi-Substrate Governance Semantic Consistency
* **Statement**: The same formal execution-governance semantics (principal, capability, argument hash, dynamic revocation, fail-closed) are evaluated across 4 execution substrates (DROS, OPA, ScopeGate, WASI).
* **Definition**: Deterministic replay yields 100% matching decisions across 44 replayed requests.
* **Status**: `SUPPORTED UNDER REGISTERED MODEL`
* **Evidence Binding**: `python vep.py replay --experiment EXP-1789532251-38a4fd` (44/44 MATCH).
* **Limitations**: Replay is bounded to the 44 recorded requests in experiment `EXP-1789532251-38a4fd`.

### CLAIM-04: Full-Path Boundary Coverage (Choke Point Precondition)
* **Statement**: Application-layer middleware (e.g. AGT function decorators) leaves unmanaged runtime paths unmonitored; DROS C-ABI substrate enforces boundary containment across declared and direct native execution paths.
* **Definition**: Observed path coverage gap in gateway-only architectures when execution bypasses declared tool wrappers.
* **Status**: `REGISTERED PATH COVERAGE GAP OBSERVED`
* **Evidence Binding**: `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md` (§4, Table 1).
* **Limitations**: Validated on registered probes (PROBE-01~04); universal containment of all arbitrary kernel syscalls requires OS-level PGM integration.

### CLAIM-05: Level-C Landscape Feature Conjunction
* **Statement**: Within the candidates identified, screened, and verified under PROTO-LANDSCAPE-2026-v1.0, no candidate has yet been documented with primary-source evidence satisfying the complete Level-C feature conjunction.
* **Definition**: Evidence-bounded empirical finding across 15 governance dimensions under frozen query families.
* **Status**: `OBSERVED (EVIDENCE-BOUNDED)`
* **Evidence Binding**: `docs/research/landscape/candidate_evidence_ledger.csv`, `candidate_matrix.csv`.
* **Limitations**: Strictly bounded by search protocol and publicly indexed sources; does not claim non-existence of unpublished or proprietary systems.

### CLAIM-06: Hybrid Loopback IPC Authentication Reference Boundary
* **Statement**: Candidate C's reference implementation successfully rejected 15/15 registered adversarial cases under the simulated cross-platform peer-identity model, demonstrating that possession of stolen session secrets does not grant execution authority when OS-attributed peer identity does not match.
* **Definition**: $\text{IPC-ACIR} = 15 / 15 = 1.000000$ with 0 unauthorized executions across payload spoofing, capability tampering, cross-principal theft, nonce replay, argument mutation, hot revocation, same-UID attacks, credential theft, and confused deputy vectors.
* **Status**: `SUPPORTED UNDER SIMULATED PEER-IDENTITY MODEL`
* **Evidence Binding**: `reports/benchmarks/post_compromise/ipc_p2_evidence.jsonl` (SHA-256: `d27281381cd239235e973fd88e9c990ddecaa9df4b6bde45fd34b8664fc7eb3a`), `tests/security/ipc/test_ipc_adversarial_suite.py`.
* **Limitations**: Scoped to the reference test harness with simulated OS peer provider; real OS-level peer-identity enforcement across Linux UDS / Windows Named Pipe remains subject to P3 integration validation.

### CLAIM-07: Real OS Process Identity & PID Reuse Invariant Containment
* **Statement**: In real operating system execution environments, numerical PID is an identifier rather than an identity; binding session authority to the dual tuple $\langle \text{PID},\ \text{create\_time} \rangle$ successfully prevents PID recycling attacks. Furthermore, authentic Windows kernel extraction (`GetNamedPipeClientProcessId`) guarantees caller attribution and blocks independent subprocess privilege porting.
* **Definition**: 0 unauthorized executions across PID reuse simulation, independent subprocess separation, and native Windows Named Pipe kernel handle attribution.
* **Status**: `VERIFIED UNDER REAL OS PEER ATTRIBUTION (WINDOWS NATIVE & PID REUSE HARNESS)`
* **Evidence Binding**: `reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl` (SHA-256: `d3365d7efb6549414b016875c4cabcef7dd763a8f14ddb301bd208e805adffd1`), `tests/security/ipc/test_ipc_p3_real_os_suite.py`.
* **Limitations**: Windows kernel peer attribution experimentally validated on native Win32 Named Pipe; Linux UDS `SO_PEERCRED` formally scoped and implemented, awaiting live Linux host run. Cross-platform universal equivalence is explicitly disclaimed.

### CLAIM-08: Level-C Search-Bounded Conjunction Novelty (Maximum Defensible Ceiling)
* **Statement**: Within the candidates identified, screened, and verified under PROTO-LANDSCAPE-2026-v1.0 across the six queried database families, no external peer candidate documents primary-source evidence satisfying the complete Level-C feature conjunction (attributed identity, in-process execution-boundary capability bitmasking, dynamic revocation, fail-closed mediation, and heterogeneous runtime governance across Web/MCP, native C-ABI, and physical actuator domains).
* **Definition**: Evidence-bounded empirical finding under Claim Ladder Level 3.
* **Status**: `OBSERVED UNDER PROTO-LANDSCAPE-2026-v1.0 (LEVEL 3)`
* **Evidence Binding**: `docs/research/landscape/candidate_matrix.csv` (11 candidates × 15 dimensions), `candidate_evidence_ledger.csv`, `LANDSCAPE_COUNTER_EVIDENCE.md`.
* **Limitations**: Strictly bounded by frozen search parameters and publicly indexed primary sources; does not constitute an unconstrained global uniqueness proof (Level 4, which is strictly prohibited). Preserved as an open empirical finding (BOUNDARY-02).

### CLAIM-09: Agent Server Hub Deployment Economics & Invariant Preservation
* **Statement**: When deployed at an Agent Server execution boundary satisfying the Non-Bypassable Mediation Interface and Execution Privilege Decoupling preconditions, DROS enforces deterministic execution governance across heterogeneous downstream substrates (Web/MCP, APIs, subprocesses) with sub-linear integration complexity $\mathbf{GIC}$ and sub-microsecond PDP decision latency ($P50 < 1.0\ \mu\text{s}$), eliminating redundant per-agent governance overhead.
* **Definition**: Empirical architectural capability under Claim Ladder Level 2.
* **Status**: `SUPPORTED UNDER REGISTERED CHOKE-POINT TOPOLOGY (LEVEL 2)`
* **Evidence Binding**: `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md` (§4 Table V, §8 H2/H3), `docs/research/DROS_COMPETITIVE_LANDSCAPE_AND_POST_COMPROMISE_POSITIONING_2026.md` (§16).
* **Limitations**: Preconditioned on execution choke point closure; does not claim bypass immunity if host process permits unmanaged raw syscall execution outside the mediated interface.