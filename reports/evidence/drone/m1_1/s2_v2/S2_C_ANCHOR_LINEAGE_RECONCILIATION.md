# Milestone M1.1-S2-C Anchor Lineage & Cross-Repository Reconciliation Report

- **Document ID**: DROS-REP-M11-S2C-LINEAGE-RECON-2026
- **Date**: 2026-09-25T06:00:00+08:00
- **Scope**: Reconcile S2-D Gate 1 Prerequisite `G1-01_s2_c_anchor_verification` with Codex Gate 2 Finding (`BLOCKED_FROM_THIS_CHECKOUT`)
- **Status Classification**:
  - **In Main Repository (`dros-core` / `dros-drone-real`)**: **`REPLAYABLE`**
  - **In Public Submodule / Standalone Repo (`dros-vep-lite`)**: **`NOT_REPLAYABLE_FROM_CHECKOUT`**
- **Live S2-D Execution**: **STRICTLY BLOCKED (NOT_RUN)**

---

## 1. Executive Summary: The Root of the Divergence

A fundamental epistemic question was raised:
> *Why did AGY's Gate 1 report declare `G1-01_s2_c_anchor_verification: PASS` for frozen anchor `c402bf...`, while Codex's Gate 2 Audit independently concluded that S2-B/C v2 is `BLOCKED_FROM_THIS_CHECKOUT`?*

### The Resolution
The divergence is purely a **repository boundary and checkout divergence**, not a fabrication of evidence or test failure:

1. **In the Root Git Repository (`E:\vscode\AI知識庫`, Git Root: `volume1/GitRepos/dros-core`)**:
   - The commit `c402bf05024613501083441c2f26316b47e88d78` **actually exists, resolves, and contains the exact tree** `845ba96ef2f660492572acb016f911697b7162a1`.
   - The frozen anchor `s2_c_freeze_anchor.json` is physically present.
   - All tracked artifact blob SHA-1 and file SHA-256 hashes match **100% identically**.
   - `test_s2_v2_c_reconciliation.py` passes **6/6 (2.32s)** and `run_s2_v2_c.py` executes cleanly (**Exit Code 0**).
   - Hence, within `dros-drone-real`, the status is undeniably **`REPLAYABLE`**.

2. **In the Public Standalone Checkout (`dros-vep-lite`, Git Remote: `DROS-VEP-lite.git`)**:
   - `dros-vep-lite` is a separate Git repository with an independent commit history.
   - The commit `c402bf...` and the commit `b7ab26...` were committed only to the main `dros-core` repository and were **never pushed or committed to `dros-vep-lite`**.
   - Furthermore, the raw JSON outputs (`s2_v2_c_reconciliation.json`), the anchor (`s2_c_freeze_anchor.json`), the runner (`run_s2_v2_c.py`), and the test suite (`test_s2_v2_c_reconciliation.py`) were never copied or committed into `dros-vep-lite/reports/evidence/drone/m1_1/s2_v2/`.
   - Hence, from the perspective of an auditor inspecting *only* `dros-vep-lite`, Codex's finding was **100% accurate: `BLOCKED_FROM_THIS_CHECKOUT`**.

---

## 2. Ten-Point Lineage Verification Matrix

| Checkpoint | Target Property | Verification Result in Main Repo (`dros-drone-real`) | Verification Result in `dros-vep-lite` | Epistemic Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **1** | Git commit object existence | `cat-file -t c402bf...` returns `commit` (code 0) | `cat-file -t c402bf...` returns fatal error (code 128) | **CONFIRMED DISCREPANCY** |
| **2** | Exact tree existence | Tree `845ba96ef2...` resolves and lists exact paths | Unresolvable in object database | **CONFIRMED DISCREPANCY** |
| **3** | `s2_c_freeze_anchor.json` presence & SHA-256 | File exists; SHA-256: `96d4198bc19c11b43c6372e42124311173d9a427ef605f0bb596805c2e92c0b2` | File does not exist | **CONFIRMED DISCREPANCY** |
| **4** | Anchor blob SHA-1 match | All 3 blobs match exact Git object hashes (`556192...`, `27ea2f...`, `187482...`) | N/A (Anchor absent) | **MATCH IN ROOT REPO** |
| **5** | S2-C Report consistency | `S2_C_EVIDENCE_INDEX.md` and report match partition \(S = G(0) \uplus B(3) \uplus I(1) \uplus U(1) \uplus N(0)\) | Text reports exist, but underlying raw JSONs are absent | **PARTIAL IN VEP-LITE** |
| **6** | Endpoint surface SHA-256 | `1e78d2b2eef1c4ca25d42e2d703a5f93abbbcd549a9ac7e6148467ac9999cd44` matches S2-B anchor digest | Absent in vep-lite | **MATCH IN ROOT REPO** |
| **7** | Claim matrix consistency | `M1_1_CLAIM_MATRIX.md` maps \(G(0), B(3), I(1), U(1)\) and \(\text{WVG} = \text{NOT\_PROVEN}\) | Present, matches claim structure | **MATCH** |
| **8** | Test reproducibility | `pytest test_s2_v2_c_reconciliation.py`: **6/6 PASS** (2.32s) | Test file does not exist | **BLOCKED IN VEP-LITE** |
| **9** | Runner reproducibility | `python scripts/s2_v2/run_s2_v2_c.py`: **Exit Code 0** | Runner does not exist | **BLOCKED IN VEP-LITE** |
| **10**| No string-only substitution | Hash verification enforced via Python `canonical_git_snapshot.py` | N/A | **STRICT CRYPTO BINDING** |

---

## 3. Definitive Classification of Evidence

To prevent confusion across researchers, academic reviewers, and audit agents, we classify the stages under the formal status schema:

| Artifact / Stage | In Main Repo (`dros-drone-real`) | In Public Checkout (`dros-vep-lite`) | Resolution Required |
| :--- | :---: | :---: | :--- |
| **S2-A v2** | `REPLAYABLE` | `NOT_REPLAYABLE_FROM_CHECKOUT` | Mirror raw JSON & runner to `dros-vep-lite` |
| **S2-B v2** | `REPLAYABLE` | `NOT_REPLAYABLE_FROM_CHECKOUT` | Mirror raw JSON, summary, & anchor to `dros-vep-lite` |
| **S2-C v2** | `REPLAYABLE` | `NOT_REPLAYABLE_FROM_CHECKOUT` | Mirror raw JSON, summary, & anchor to `dros-vep-lite` |
| **S2-D Gate 0** | `REPLAYABLE` | `REPLAYABLE` | Already mirrored and committed |
| **S2-D Gate 1** | `REPLAYABLE` | `REPLAYABLE` | Already mirrored and committed |
| **S2-D Live** | `NOT_RUN` | `NOT_RUN` | **Strictly blocked pending human authorization** |

---

## 4. Exact Inventory of Files Missing in `dros-vep-lite`

To make `dros-vep-lite` standalone and replayable without access to the internal `dros-core` repository, the following artifacts must be synced and committed to `dros-vep-lite`:

1. `reports/evidence/drone/m1_1/s2_v2/s2_c_freeze_anchor.json`
2. `reports/evidence/drone/m1_1/s2_v2/s2_b_freeze_anchor.json`
3. `reports/evidence/drone/m1_1/s2_v2/s2_v2_c_reconciliation.json`
4. `reports/evidence/drone/m1_1/s2_v2/s2_v2_c_reconciliation_summary.json`
5. `reports/evidence/drone/m1_1/s2_v2/s2_v2_c_reconciliation.exit_code`
6. `reports/evidence/drone/m1_1/s2_v2/s2_v2_b_authority.json`
7. `reports/evidence/drone/m1_1/s2_v2/s2_v2_b_authority_summary.json`
8. `reports/evidence/drone/m1_1/s2_v2/s2_v2_b_authority.exit_code`
9. `reports/evidence/drone/m1_1/s2_v2/s2_v2_a_discovery.json`
10. `reports/evidence/drone/m1_1/s2_v2/s2_v2_a_discovery.exit_code`
11. `scripts/s2_v2/run_s2_v2_c.py`
12. `scripts/s2_v2/run_s2_v2_b.py`
13. `tests/drone/s2_v2/test_s2_v2_c_reconciliation.py`
14. `tests/drone/s2_v2/test_s2_v2_b_execution_authority.py`

---

## 5. Conclusion & Action Order

- AGY was operating within `E:\vscode\AI知識庫` where `c402bf...` is fully accessible and verifiable.
- Codex was operating with focus on `dros-vep-lite`, which is missing the S2-B/C package.
- **Both findings are logically consistent once repository boundaries are acknowledged.**
- **Before Live S2-D is ever considered**, the historical S2-B/C evidence package should be mirrored and committed into `dros-vep-lite` so that public reviewers do not encounter `BLOCKED_FROM_THIS_CHECKOUT`.
