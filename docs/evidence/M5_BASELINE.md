# VEP M5 Evidence Baseline (M5_BASELINE.md)
* **Baseline ID**: BASELINE-VEP-2026-M5.1
* **Frozen Date**: 2026-09-16
* **Status**: FROZEN / IMMUTABLE
* **Git Commit**: `e02c4fcbd8e862afba72878122111f137ae20b18`
* **Governing Body**: DROS Virtual Enterprise Platform (VEP) Benchmark Lab

---

## 1. Scope & Objective
This document fixes the immutable experimental baseline for VEP M5 / M5.1 prior to initiating the Post-M5 Evidence Closure Roadmap. It guarantees complete provenance reconciliation across:
$$\text{Experiment ID} \longrightarrow \text{Raw Evidence} \longrightarrow \text{Artifact Manifest} \longrightarrow \text{Report Section}$$

---

## 2. Core Experiment Identifiers & Status
* **Canonical Multi-Substrate Post-Compromise Experiment**: `EXP-1789532251-38a4fd`
  - **Status**: FROZEN (44 requests across 4 substrates: DROS, OPA, ScopeGate, WASI)
  - **Location**: `reports/benchmarks/post_compromise/EXP-1789532251-38a4fd/result.json`
  - **Result Hash**: `851779ed905f80c284b4c775259d43f85e2bd53e660e16b2c1819cbf264e6c01`
  - **Pointer**: Registered in `reports/benchmarks/post_compromise/latest.json`
* **Predecessor 33-Run Iteration**: `EXP-1789530057-779a1d`
  - **Status**: ARCHIVED PREDECESSOR (33 requests without OPA substrate arm)
  - **Location**: `reports/benchmarks/post_compromise/EXP-1789530057-779a1d/result.json`
  - **Result Hash**: `0cb3b05fc09d7590bc53d4d17742e390dbdb62f6533f5c9a35a538c8a28c255e`
  - **Reconciliation Rule**: All formal reporting in `VEP-REPORT-2026-M5.1` binds exclusively to `EXP-1789532251-38a4fd`. `EXP-1789530057-779a1d` is preserved for historical audit only.

---

## 3. Cryptographic Fingerprints (SHA-256)
* **Attack Corpus (`benchmarks/bare_metal_crucible/run_crucible.py`)**:
  `11eff25be768756d2c7739da6cee20381e5654b247b48337173f5ece92b0241b`
* **Evaluator & CLI Substrate (`vep.py`)**:
  `96d5bdbcf953a98ad3070184df068405d2ada09715a7a698e50fbaa93bd2cce0`
* **Benchmark Runner (`src/vep/benchmark/runner.py`)**:
  `f2201f5cfbe7ae750cedd023057636b6837db55aba5343a2f8a05c936e7b4123`
* **Audit Execution Log (`reports/audit.jsonl`)**:
  `e60f48568667a727c33b2c2d5d5730d4b40126f35fe7c73af3bbe6a617b119fe`
* **Benchmark Summary (`reports/benchmark_summary.json`)**:
  `934ffc94cf7e2b4ccdeca2d6ceafc5a84e9a91d7f37d1da9415cfd442fdc775a`
* **Conformance Report (`reports/conformance_report.json`)**:
  `634dc344c2bdd5d43f551211064d3f941c52c3ece6f7c5c7686cd3a9debcbf88`
* **Hardened M5.1 Report (`reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md`)**:
  `ffab12b6eca64a243ab0564994cee0eb399342bed686c1bfd7ef28f71c001660`
* **Evidence Manifest (`reports/evidence_manifest.json`)**:
  `c9f7157494cbf5f1a8249266fec3483929b810f3468d2b1156d8cfb5c4111a2e`

---

## 4. Invariant Verification Status
* **100% Deterministic Replay**: Verified via `python vep.py replay --experiment EXP-1789532251-38a4fd` (44/44 MATCH).
* **Multi-Substrate Pytest Suite**: Verified via `pytest tests/test_multi_substrate_framework.py` (3 passed, 100% green).