<!-- dros_component: dros-vep-evidence-status -->
<!-- dros_depends: [REPRODUCIBILITY.md, docs/EVIDENCE_READING_GUIDE.md] -->
<!-- dros_description: Public, scope-bounded summary of current and historical evidence status -->
<!-- dros_status: PUBLIC SANITIZED SUMMARY / WORKING STATUS -->

# Public Evidence Status / 公開證據狀態

**As of / 截至：2026-09-27**<br>
**Status / 狀態：** `PUBLIC_SANITIZED_SUMMARY` · `SOURCE_ARTIFACTS_REMAIN_LOCAL`<br>
**Scope / 範圍：** This page summarizes status only. It does not modify or replace source evidence, manuscripts, claim registries, or historical results. 本頁僅摘要狀態，不修改或取代來源證據、論文、claim registry 或歷史結果。

## Current TMC work / TMC 當前工作

| Item | Current status | Boundary / 限制 |
|---|---|---|
| D1 paper identity | `COMPLETED — HUMAN SELECTED` | Candidate B (2026-09-24 reviewer-facing PDF) selected for the review. Exact source-package-to-upload binding remains unresolved. 已由 Human 選定 Candidate B 作為本次 review 對象；source package 與實際上傳 bytes 的精確綁定仍未解決。 |
| D2 T4/T5 correspondence | `COMPLETED — CORRESPONDENCE ONLY` | Current-paper correspondence was confirmed by Human. Historical T4/T5 remains `EVIDENCE_FOUND_BUT_CONFOUNDED`; claim supportability is not established. Human 確認 claim 對應關係；歷史 T4/T5 仍為 `EVIDENCE_FOUND_BUT_CONFOUNDED`，未建立 claim 支持性。 |
| D3 target-state semantics | `D3-A SELECTED DESCRIPTIVELY` | Defines the selected target-state meaning only; it is not runtime observation or claim support. 僅描述所選 target-state 語義，不是 runtime observation 或 claim support。 |
| D4 read-only preflight | `PREFLIGHT COMPLETED` | Static/source and bounded read-only metadata review only. It is not an isolation test. 僅完成靜態／來源及有限唯讀 metadata 檢視，不是 isolation test。 |
| D4 runtime validation | `NOT EXECUTED` | Runtime isolation remains `NOT VALIDATED`; the preflight is not execution authorization. Runtime isolation 仍為 `NOT VALIDATED`；preflight 不構成執行授權。 |
| New matched experiment | `NOT AUTHORIZED / NOT EXECUTED` | No run or new experiment was performed for this reconciliation. 本次 reconciliation 未執行任何新實驗或 run。 |
| Evidence promotion | `NONE` | No evidence or claim was promoted. 未升格任何 evidence 或 claim。 |

The local D3 and D4 source records were checked against the supplied SHA-256 values at reconciliation time: D3 `1C114BC6544FA3EF868258A07BDF65026BDFDCCA8FFD4464450C6088D101F29D`; D4 preflight `59AC14EE10307AA44C6DAE3B75E4F58634E489F9582094A58EEF1BE1FA47C36C`. These hashes identify local source bytes; the detailed D1–D4 records are intentionally not part of this public commit because they contain machine-specific paths and paper-workspace metadata. 本次核對時，D3/D4 本機來源紀錄與指定 SHA-256 相符。這些 digest 指向本機來源 bytes；D1–D4 詳細紀錄含機器路徑及論文工作區 metadata，因此本次不納入公開 commit。來源檔案保持原狀並留在本機。

## Historical and public-claim status / 歷史證據與公開主張狀態

The README wording update follows a bounded local review in `docs/reviews/VEP_PUBLIC_CLAIM_EVIDENCE_CONSISTENCY_AUDIT_2026-09-25.md`. That audit remains uncommitted and is held for separate review; this commit does not make its underlying search independently reproducible to a fresh clone. README wording is therefore scoped conservatively and no new evidence claim is made. README 文案限縮依據本機 bounded review；該 audit 尚未提交，留待另行審閱，因此新 clone 無法僅憑本 commit 重現其底層檢索。本次 README 措辭採保守範圍，未建立新的 evidence claim。

- Historical T4/T5 records are retained and remain `EVIDENCE_FOUND_BUT_CONFOUNDED`. They are not causal evidence and are not retroactively repaired. 歷史 T4/T5 紀錄予以保留，仍為 `EVIDENCE_FOUND_BUT_CONFOUNDED`；不是因果證據，也不回溯修補。
- README latency figures `26.1 μs` and `<500 ns` are historical reported values, not currently independently validated or promoted. Code anchors and report presence do not establish measured latency. README 中 `26.1 μs` 與 `<500 ns` 是歷史報告數值，目前未獨立驗證或升格；程式碼定位與報告存在不能證明量測延遲。
- The AS-001–AS-005 `DENY` summary is a historical synthetic-fixture result, not an overall security rate or a current deployment claim. AS-001–AS-005 的 `DENY` 摘要是歷史合成 fixture 結果，不是整體安全率或現行部署主張。
- Historical scripts, reports, and artifacts are not automatically reproducible, verified, or claim-supporting. 歷史腳本、報告及工件不會因存在而自動成為可重現、已驗證或支持 claim 的證據。

## Reading rules / 閱讀規則

`SOURCE_DESCRIBED` ≠ `STATICALLY_VERIFIABLE` ≠ `VERIFIED_EVIDENCE` ≠ `CLAIM_SUPPORTED`. `HISTORICAL`, `CONFOUNDED`, `NOT_VALIDATED`, `BLOCKED`, and `INDETERMINATE` remain distinct status labels. Source-described behavior is not runtime verification; an artifact's presence is not claim support. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and [Evidence Reading Guide](docs/EVIDENCE_READING_GUIDE.md).

`SOURCE_DESCRIBED` ≠ `STATICALLY_VERIFIABLE` ≠ `VERIFIED_EVIDENCE` ≠ `CLAIM_SUPPORTED`。`HISTORICAL`、`CONFOUNDED`、`NOT_VALIDATED`、`BLOCKED` 與 `INDETERMINATE` 各為不同狀態。來源描述不等於 runtime verification；工件存在不等於支持 claim。請參閱 [REPRODUCIBILITY.md](REPRODUCIBILITY.md) 與 [Evidence Reading Guide](docs/EVIDENCE_READING_GUIDE.md)。

**Paper / claim sources: unchanged. No experiment, runtime validation, evidence promotion, or push was performed by this documentation update.**<br>
**論文／claim 來源：未變更。本次文件更新未執行實驗、runtime validation、evidence promotion 或 push。**
