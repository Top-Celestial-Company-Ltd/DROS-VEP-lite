# S2 Public Evidence Package Replay & Fresh Clone Verification Audit

**Audit Date (UTC):** 2026-09-24T22:42:00Z  
**Audit Date (Taipei):** 2026-09-25T06:42:00+08:00  
**Evaluator:** Antigravity Autonomous Lead Architect  
**Evaluation Standard:** DROS Epistemic Governance & Clean Checkout Reproducibility  
**Target Sub-Repo:** `dros-vep-lite` (Clean Clone)  
**Clone Target Path:** `build_tmp/clean_clone_verify/dros-vep-lite`  
**Clone Commit:** `415ef0751a8f94473e5b6d2e9754a8232113b6b2` (`main`)  
**Commit Message:** `fix(drone): record byte-exact CRLF exit_code blob (18748286e5) matching canonical anchor`  

---

## 1. Epistemic Classification & Boundary Definition

| Boundary Dimension | Internal Root Repository (`dros-core` / `volume1/GitRepos/dros-core`) | Public Standalone Distribution (`dros-vep-lite`) |
| :--- | :--- | :--- |
| **Epistemic Classification** | **Canonical Source Replayable / Historical Evidence Replayable** | **Public Evidence Package Replayable** |
| **Object Database** | Contains full commit history, trees, and blobs (e.g. historical commit `c402bf05...`). | Isolated commit tree rooted at standalone initial export; does **NOT** share `.git/objects` with `dros-core`. |
| **Replay Scope** | Historical provenance verification, Git object inspection, full-tree snapshotting. | Independent downstream replay of cryptographic verification, test oracles, and mathematical reconciliation derivation. |
| **Physical Hardware / SITL** | Historical physical PX4 SITL flight experiment run in earlier milestones. | **Zero Live Execution required.** Re-verifies frozen empirical artifacts, hashes, and partitions. |

---

## 2. Clean Clone Verification Protocol Results

### 2.1 Isolation Verification
- **Remote Origin:** Points only to `E:/vscode/AI知識庫/dros-vep-lite` (no remote reference to `dros-core`).
- **Internal Commit Lookup:** `git cat-file -e c402bf05024613501083441c2f26316b47e88d78` returns **Exit Code 1** (commit is absent from git object database, confirming strict isolation).
- **Working Tree Cleanliness:** `git status` reports `nothing to commit, working tree clean`.

### 2.2 CRLF & Blob Preservation Verification
All 17 mirrored canonical artifacts maintain exact SHA-256 and Git blob hashes across Windows checkout:
- `.gitattributes` enforces `/reports/evidence/drone/** -text`.
- `s2_v2_c_reconciliation.exit_code`:
  - Bytes: `0\r\n` (CRLF)
  - Git Blob SHA-1: `18748286e5b8b4de5db905f87cdfed1a7d48fe60`
  - SHA-256: `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354`

### 2.3 Automated Pytest Suite Execution
Executed in clean clone:
```bash
python -m pytest build_tmp/clean_clone_verify/dros-vep-lite/tests/drone/s2_v2/test_s2_d_gate1.py build_tmp/clean_clone_verify/dros-vep-lite/tests/drone/s2_v2/test_s2_v2_c_reconciliation.py -v
```
**Result:** **12 passed in 3.38s (100% PASS)**
- `test_g1_01_s2_c_anchor_verification`: **PASSED**
- `test_g1_04_snapshot_serialization_and_invariants`: **PASSED**
- `test_g1_07_probe_construction`: **PASSED**
- `test_g1_08_firewall_default_dry_run_and_prohibitions`: **PASSED**
- `test_g1_12_normalizer_and_oracles`: **PASSED**
- `test_g1_gate1_result_schema_and_preflight`: **PASSED**
- `test_p1_s2_b_canonical_provenance`: **PASSED**
- `test_p2_s2_b_surface_reproducibility`: **PASSED**
- `test_p3_s1_topology_integrity`: **PASSED**
- `test_p4_s1_governance_evidence_grounding`: **PASSED**
- `test_p5_path_level_reconciliation_partition_and_soundness`: **PASSED**
- `test_p6_whole_vehicle_governance_fail_closed`: **PASSED**

### 2.4 Reconciliation Derivation Execution
Executed in clean clone:
```bash
python build_tmp/clean_clone_verify/dros-vep-lite/scripts/s2_v2/run_s2_v2_c.py
```
**Result:** **Exit Code 0**
- Successfully derived mathematical partition:
  $$S = G(0) \uplus B(3) \uplus I(1) \uplus U(1) \uplus N(0)$$
- Whole-Vehicle Governance Claim:
  $$\text{Whole-Vehicle Governance} = \mathbf{NOT\_PROVEN}$$
- Clean checkout restored: `git checkout -- .` restored tree to clean state.

---

## 3. Status Summary of S2-D Containment

- **S2-C Historical Baseline:** **FROZEN & IMMUTABLE** (never modified).
- **Public VEP Package:** **STANDALONE VERIFIED & INDEPENDENTLY REPLAYABLE**.
- **Live S2-D Execution Status:** **`NOT_RUN` (Awaiting explicit human instruction)**.
