# MCP Execution Authority Contract — Round 1

狀態：`CONTRACT_GREEN_NOT_LIVE_EXECUTION_EVIDENCE`

`tests/security/cli`：24 passed。

本輪已驗證：

- arbitrary shell capability 預設 DENY；
- semantic tool 必須先通過 typed schema；
- principal credential 無效時，在 authority 前 DENY；
- executable digest 不一致時，在 authority 前 DENY；
- 實際檔案內容變更造成 digest mismatch 時，在 authority 前 DENY；
- semantic MCP request 可進入現有 `ExecutionAuthority` seam；
- expired semantic capability 經 canonical authority fail-closed；
- positive authorization 仍只能由注入的 authority seam 回傳。

本輪尚未驗證：

- 真實 vLEI 或其他密碼學 credential verifier；
- 真實 executable content hashing；
- fd-based `execveat` 執行；
- Linux kernel enforcement；
- host-wide topology closure。

因此本輪不得升格為 `DROS_INTEGRATION_CONFIRMED` 或 `COMPLETE_MEDIATION_ESTABLISHED`。
