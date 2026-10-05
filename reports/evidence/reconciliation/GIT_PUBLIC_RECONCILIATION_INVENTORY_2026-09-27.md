<!-- dros_component: dros-vep-public-reconciliation -->
<!-- dros_depends: [EVIDENCE_STATUS.md, reports/evidence/reconciliation/PUBLIC_REPOSITORY_SANITY_SCAN_2026-09-27.md] -->
<!-- dros_description: Read-only inventory and disposition for the 2026-09-27 local-to-public Git reconciliation -->
<!-- dros_status: BATCH INVENTORY / NO HISTORICAL ARTIFACT DELETION -->

# 本機 → 公開 Git reconciliation 盤點 / Local → Public Git Reconciliation Inventory

## 繁體中文摘要

本批僅納入雙語 README 公開文案限縮、證據狀態摘要、閱讀指南、可重現性規則與本盤點／sanity scan。初始盤點有 8 個既有 tracked modifications、302 個既有 untracked files；除本批 3 個文件變更外，其餘 8 個 tracked modifications 與全部未審閱 untracked work 均保留並排除。D1–D4 詳細來源紀錄 hash 已核對，但因本機絕對路徑及論文工作區 metadata 留在本機，不直接公開；狀態摘要不冒充原始 artifact。未刪除、未改寫歷史結果，未執行實驗、runtime、promotion 或 push。

**Date:** 2026-09-27 (Asia/Taipei)<br>
**Repository:** `dros-vep-lite`<br>
**Initial branch / HEAD:** `main` / `908d17f106`<br>
**Remote:** `origin` points to the existing public GitHub repository; remote configuration was not changed.<br>
**Policy:** local documentation/commit only; no push, experiment, runtime validation, paper edit, or evidence promotion.

## Git state at inventory

At the initial read-only snapshot, the worktree had 8 pre-existing modified tracked files and 302 pre-existing untracked files. After this reconciliation's three intended tracked-file edits, the tracked diff contained 11 files (3 in-scope documentation files and 8 unrelated pre-existing files). This report and other new reconciliation documents are this task's untracked additions and are not part of the pre-existing count.

| Category | Files / scope | Action |
|---|---|---|
| Current research/evidence | `EVIDENCE_STATUS.md`, `docs/EVIDENCE_READING_GUIDE.md`, updated `REPRODUCIBILITY.md`, bilingual README wording, this inventory, and the companion sanity scan | `INCLUDE` — public-safe status/guidance only; no raw evidence or result altered |
| Current implementation | 137 untracked files under `implementations/`, including E1-TMC source, deployment materials, manifests, and build outputs | `HOLD` — preserve; source/build/package review and public-scope selection remain separate |
| Historical evidence | 86 untracked files under `reports/`, including Drone artifacts, TMC records, raw bundles, and reconciliation records | `PRESERVE`; selected TMC originals `HOLD` for public sanitization/review; no deletion or alteration |
| Legacy scripts | 10 untracked files under `scripts/`, including `scripts/legacy/` runners | `PRESERVE + HUMAN REVIEW` — no runner executed; no script logic changed or included in this batch |
| Other research / tests / profiles | 40 untracked `docs/`, 13 `tests/`, 8 `tools/`, 2 `profiles/`, 1 `substrates/`, and 5 root-level files | `HOLD` — pre-existing user work; not reviewed or staged by this batch |
| Local-only/private | D1/D2/D3/D4 detailed records and other files with absolute workstation paths or private paper-workspace metadata | `EXCLUDE` originals from public commit; retain unchanged locally. `EVIDENCE_STATUS.md` is a sanitized status summary, not a replacement source artifact |
| Generated / large binary | `tools/opa/opa.exe` (96,506,651 bytes); E1-TMC `.exe`, `.dll`, `.pdb`, and dependency outputs | `DO_NOT_COMMIT` in this batch — no size/provenance/release review was authorized |
| Sensitive / secret-like | Public-facing candidate docs scanned for absolute local paths and private-key markers; repository-wide code/docs produced keyword matches requiring contextual review | Candidate docs `SAFE` after sanitization; unreviewed matches remain `HOLD`, not presumed secrets or presumed safe |
| Needs human review | 8 pre-existing tracked edits listed below; all other pre-existing untracked work not selected above | `HOLD` — untouched and unstaged |
| Deleted files | None observed in the initial `git status --short` snapshot | No delete/restore operation performed |

### Pre-existing tracked changes held out of this commit

```text
docs/whitepapers/DROS_AgenticWeb_Defense_Whitepaper_EN.md
drone/adapters/mavlink/mavlink_adapter.py
drone/pep_proxy.py
reports/benchmarks/post_compromise/latest.json
scripts/s2_v2/s2_d/models.py
scripts/s2_v2/s2_d/rollback_verifier.py
scripts/s2_v2/s2_d/snapshot.py
vep.py
```

### Recent TMC records preserved locally

The following source files were present and not overwritten. D3 and D4 matched the supplied SHA-256 values; the D1/D2 record and its three named local source records also matched their recorded hashes. The detailed source files remain unstaged because they contain absolute workspace paths, local paper-workspace references, and review-only detail.

```text
reports/evidence/reconciliation/TMC_D1_D2_HUMAN_DECISION_RECORD_2026-09-27.md
reports/evidence/reconciliation/TMC_D3_TARGET_STATE_SEMANTICS_HUMAN_DECISION_2026-09-27.md
reports/evidence/reconciliation/TMC_D4_READ_ONLY_PREFLIGHT_2026-09-27.md
```

Their public status is summarized in `EVIDENCE_STATUS.md`; no sanitized copy is represented as the original hashed artifact.

## Batch disposition

**INCLUDED:** bilingual README scope/status corrections; reproducibility criteria; public evidence status; evidence reading guide; inventory; sanity scan.<br>
**EXCLUDED:** all unrelated pre-existing code, benchmark/evidence outputs, paper/whitepaper sources, deployment materials, and binaries.<br>
**HELD_FOR_REVIEW:** the eight unrelated tracked modifications, the 302 initial untracked files outside the explicitly included documentation, the detailed TMC records, and the local public-claim audit.<br>
**SANITIZED:** public status summary and public-facing paths/claim wording only. Source artifacts remain unchanged.<br>
**No historical result was deleted, rewritten, or promoted.**

`tools/dros_code_weaver.py` was not found in the workspace search, so no topology regeneration was attempted and no manual substitute was made.
