<!-- dros_component: dros-vep-public-reconciliation -->
<!-- dros_depends: [EVIDENCE_STATUS.md, reports/evidence/reconciliation/GIT_PUBLIC_RECONCILIATION_INVENTORY_2026-09-27.md] -->
<!-- dros_description: Read-only public-facing wording, path, and secret-pattern scan for the 2026-09-27 reconciliation -->
<!-- dros_status: BOUNDED STATIC SCAN / NOT A REPOSITORY-WIDE CERTIFICATION -->

# 公開倉庫 sanity scan / Public Repository Sanity Scan

## 繁體中文摘要

本次為 bounded static scan，不是整個 repo 的公開安全認證。選定公開文案已限縮歷史 benchmark、fixture、reproducibility 與 production wording。初始掃描在未審閱文本中找到 7 個 `E:/` 與 13 個 `C:\\` 絕對路徑檔案，均未納入 commit；常見 private-key header／`sk-` prefix pattern 未命中，但不能由此推論所有秘密皆不存在。96,506,651-byte OPA executable 及 E1-TMC build outputs 排除；其他未審閱內容一律 HOLD。

**Date:** 2026-09-27 (Asia/Taipei)<br>
**Scope:** repository-local text search and review of the public-facing files selected for this commit. No tests, runners, experiments, runtime probes, or external lookups were performed. This is a bounded scan, not a certification that every unreviewed file is safe to publish.

## Search and disposition

| Classification | Findings | Disposition |
|---|---|---|
| `SAFE` | The staged-candidate README pair, `REPRODUCIBILITY.md`, `EVIDENCE_STATUS.md`, and evidence reading guide contain no absolute workstation path or private-key marker after review. | Eligible for this documentation-only batch. |
| `SANITIZED` | README latency, fixture-rate, reproducibility, production, and workflow-availability wording was scoped to historical reports, synthetic fixtures, source descriptions, or unvalidated behavior. The reproducibility guide now uses repository-relative links and removes local machine paths and credential-variable examples. | Include the sanitized wording; source reports and experiment results remain unchanged. |
| `HISTORICAL` | `26.1 μs`, `<500 ns`, AS-001–AS-005 summaries, and T4/T5 are retained only with explicit historical/confounded status and are not promoted as current independently validated evidence. | Preserve; no result alteration or evidence promotion. |
| `HUMAN_REVIEW_REQUIRED` | Absolute path scan identified 7 text files containing `E:/` and 13 containing `C:\\` strings. These include the detailed TMC D1–D4 records, paper/review workspace indexes, historical benchmark/replay reports, and E1-TMC implementation reports. | Keep unstaged until each is sanitized or approved for public inclusion. Exact file lists were inventoried locally; TMC originals remain byte-for-byte unchanged. |
| `HUMAN_REVIEW_REQUIRED` | Keyword search for strong public claims (`100%`, `guaranteed`, `verified`, `validated`, `official final`, `production`, `only`, `world first`, `global first`) has additional matches outside the selected README sections, including untracked implementation, test, evidence, and research documents. Some are scoped test vocabulary or examples; the unreviewed set is not presumed safe. | Hold all such unreviewed files; this batch does not silently edit paper, claim registry, or other research documents. |
| `DO_NOT_COMMIT` | `tools/opa/opa.exe` is 96,506,651 bytes. E1-TMC build outputs include `.exe`, `.dll`, `.pdb`, and dependency files. | Excluded from this batch; provenance, licensing, size, and release inclusion were not reviewed. |

## Absolute-path files found

The following names are recorded to explain the hold; none is staged by this batch. Counts reflect the repository text scan before this report was created; the explanatory pattern literals in this report are not additional source files or local-path disclosures.

**`E:/` matches (7 files):**

```text
docs/DROS_5_PAPER_PROGRAM_SUBMISSION_MASTER_INDEX.md
docs/specifications/DROS_VEP_TEST_CATALOG_v0.1.0_ZH.md
reports/benchmarks/post_compromise/appendix_d_full_report.md
reports/evidence/drone/m1_1/s2_v2/S2_PUBLIC_REPLAY_AUDIT.md
reports/evidence/reconciliation/TMC_D1_D2_HUMAN_DECISION_RECORD_2026-09-27.md
reports/evidence/reconciliation/TMC_D3_TARGET_STATE_SEMANTICS_HUMAN_DECISION_2026-09-27.md
reports/evidence/reconciliation/TMC_D4_READ_ONLY_PREFLIGHT_2026-09-27.md
```

**`C:\\` matches (13 files):**

```text
docs/guides/VEP_HANDOFF_2026-09-21.md
docs/reviews/M1_PILOT_IDENTITY_SCOPE_MANIFEST_2026-09-25.md
reports/evidence/reconciliation/PAPER_CLAIM_S0_S1_EXECUTION_WORKSHEET_2026-09-26.md
reports/evidence/reconciliation/TMC_D4_READ_ONLY_PREFLIGHT_2026-09-27.md
reports/evidence/reconciliation/VEP_HISTORICAL_PROVENANCE_INCIDENT_REPORT_2026.md
implementations/e1_tmc_b1_o1/E1_TMC_B1_O1_ACL_DEPLOYMENT_REPAIR_EXECUTION_BLOCKER_PROPOSAL_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_B1_O1_ACL_DEPLOYMENT_PATH_REPAIR_PREPARATION_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_B1_O1_LANE_I_RUNTIME_AUTHORIZATION_PACKAGE_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_B1_O1_ISOLATION_VALIDATION_REPORT_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_BOOTSTRAP_SDDL_CONTROL_FLAG_RECONCILIATION_DECISION_PACKAGE_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_BOOTSTRAP_RUNTIME_EVIDENCE_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_BOOTSTRAP_PRIVILEGE_CREATE_INTEGRATION_VALIDATION_DESIGN_2026-09-27.md
implementations/e1_tmc_b1_o1/E1_TMC_BOOTSTRAP_PRIVILEGE_CREATE_INTEGRATION_RUNTIME_2026-09-27.md
```

No `AppData` reference was found by the bounded scan. No PEM private-key header or common `sk-`-prefixed credential pattern was found in scanned text files. This does not establish that all tokens, secrets, or sensitive content are absent; unreviewed files remain held.

## Explicit non-actions

- No absolute-path source file was edited or deleted; no private artifact was overwritten.
- No paper, reviewer-facing PDF, claim registry, or T4/T5 source artifact was changed.
- No experiment, benchmark, test suite, runner, runtime validation, or evidence promotion was performed.
- `tools/dros_code_weaver.py` was not found; topology was not manually rewritten.
- No remote operation or push was performed.
