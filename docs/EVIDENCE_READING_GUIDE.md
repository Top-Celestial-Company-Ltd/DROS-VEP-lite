<!-- dros_component: dros-vep-evidence-guide -->
<!-- dros_depends: [../EVIDENCE_STATUS.md, ../REPRODUCIBILITY.md] -->
<!-- dros_description: Public guide for inspecting evidence lineage and verification boundaries -->
<!-- dros_status: PUBLIC GUIDE -->

# Evidence Reading Guide / 證據閱讀指南

Use this sequence when assessing any repository result. 評估倉庫中的結果時，依序檢查：

1. Start with [EVIDENCE_STATUS.md](../EVIDENCE_STATUS.md) and identify whether the item is current, historical, confounded, blocked, or not validated. 先讀狀態頁，確認項目屬現行、歷史、confounded、blocked 或 not validated。
2. Read the experiment or reconciliation record and its stated claim, scope, and limits. 閱讀 experiment/reconciliation 紀錄及其 claim、scope、limit。
3. Bind the exact source revision and build/target identity. 綁定精確 source revision 與 build/target identity。
4. Identify the runner and execution path; a script's presence is not proof it ran. 確認 runner 與 execution path；腳本存在不證明曾執行。
5. Inspect raw artifacts and their provenance. 檢查 raw artifacts 與 provenance。
6. Recompute/check hashes against the named manifest and exact bytes. 依指定 manifest 核對精確 bytes 的 hashes。
7. Inspect the oracle and observation boundary, including independence where required. 檢查 oracle、觀測邊界及必要時的獨立性。
8. Confirm verification status and whether the evidence supports the exact claim and scope. 確認 verification status，以及 evidence 是否支持精確 claim 與 scope。

Do not infer claim support from repository presence, a model summary, an aggregate, a passing test alone, a matching hash alone, or source-described behavior. 不得僅由倉庫檔案存在、模型摘要、aggregate、單獨的 test pass、單獨的 hash 相符或來源描述推定 claim supported。

For minimum reproducibility fields and execution boundaries, see [REPRODUCIBILITY.md](../REPRODUCIBILITY.md). 可重現性的最低欄位與執行邊界請見 [REPRODUCIBILITY.md](../REPRODUCIBILITY.md)。
