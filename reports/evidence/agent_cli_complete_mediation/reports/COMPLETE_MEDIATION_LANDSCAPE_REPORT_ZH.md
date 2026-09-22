# AI Agent CLI 完整中介研究報告（第一輪）

研究 protocol：`PROTO-AGENT-CLI-COMPLETE-MEDIATION-2026-v1.0`

日期：2026-09-22

## 結論

在本輪檢視的公開一手資料中，Codex CLI、Claude Code、Gemini CLI、Cursor 與 OpenHands 均可找到不同程度的 sandbox、approval、tool policy、container、VM 或 kernel substrate 控制；但目前沒有足夠公開證據，能在一般化 Agent CLI topology 上建立 `CM-1` 至 `CM-7` 的完整中介證據。

正式研究 verdict：

```text
INSUFFICIENT_PUBLIC_EVIDENCE
```

這不代表任何指定產品「不安全」，也不代表沒有實作 enforcement；它只表示「所有可達 execution path 均經過同一個可驗證授權邊界」尚未由公開證據建立。

## 對 DROS MCP 防禦的影響

MCP 層應降低不必要的 execution topology，而不是宣稱取代 host-wide CLI enforcement：

- arbitrary shell capability 預設 `DENY`；
- semantic tool 使用 typed schema，先驗證結構化參數，再建構 argv；
- MCP handler 僅作 PEP，不得自行核發 `ALLOW`；
- 正向授權必須進入 canonical DROS Execution Authority；
- principal credential、executable digest、TTL、revocation 與 audit 必須分別驗證；
- registered MCP execution path 的成功，不等於 host-wide CLI governance。

## VEP 新增證據

- `MCP-EXEC-AUTHORITY-01`：registered MCP path contract 24/24 通過；涵蓋 arbitrary shell deny、typed argument validation、principal credential rejection、executable digest mismatch、canonical authority seam、expiry fail-closed。
- `EXEC-BOUNDARY-15-BPF-LSM-LIVE-ROUND2`：`agentserver` 實機確認 BPF-LSM attach、pre-exec deny 與 cleanup 後 baseline recovery。
- BPF-LSM、AppArmor、Landlock 的 substrate evidence 不升格為 host-wide choke point 或 DROS universal authority binding。

## 尚未完成

- 真實 vLEI 或其他密碼學 principal credential verifier；
- fd-based `execveat` 與 immutable executable binding；
- host-wide alternate topology closure；
- DROS universal CLI governance。

詳細來源與矩陣：

- `../sources/sources.json`
- `../matrix/AGENT_CLI_EXECUTION_TOPOLOGY_MATRIX.md`
- `../research/public_source_scan_round1.md`
