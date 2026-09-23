# 舊版 Mobile 能耗與浸泡測試主張稽核

**稽核日期：** 2026-09-23 | **範圍：** 舊版 Mobile SDK host harness、系統開銷報告與 24 小時 soak aggregate
**目的：** 區分歷史報告數字與目前可重現、可獨立核對的證據。

## 稽核結果

| 主張 | 核對材料 | 稽核狀態 | 允許的描述方式 |
|---|---|---|---|
| Mobile `P50=1.70 μs`、`P99=7.30 μs` | `test_mobile_attacks.py` 呼叫 `KotlinDROSClient`；該 adapter 再委派至 `SwiftDROSClient`，由 Python `ctypes` 載入 Windows DLL。計時使用 host `perf_counter_ns`，不是 Android JNI、iOS Swift 或裝置 runtime；未保存 raw latency samples。 | **僅為 host-side adapter 歷史報告值；未經真機驗證，也無法由 raw samples 重建。** | 至多稱為歷史 host-side C-ABI adapter timing，不得稱為手機裝置延遲。 |
| 電池 `<0.001 mAh / 10k calls` | 測試程式直接印出固定 estimate；未附電流、電壓、能量樣本、計算輸入、校準電量計、Batterystats trace 或 power-profile artifact。 | **不得宣稱為實測值。** | 僅能說舊 harness 曾輸出未驗證估算；商品與論文文案應移除數值。 |
| 每次調用能量 `<0.05 μJ` | 舊報告有此數字，但未提供推導、儀器、raw trace 或校準流程。 | **不得宣稱為實測值。** | 不提出量化能耗主張。 |
| Mobile energy claim 中的 `0 KB` network egress | 引用的 harness 沒有網路封包或流量 accounting instrumentation。 | **該 harness 未量測。** | 不得當成實測網路結果。 |
| 24 小時 soak「memory leak `0 Bytes`」 | `scripts/run_24h_soak_test.py` 存在，但沒有 heap/RSS/profile collection；JSON aggregate 沒有 memory 欄位或原始 memory profile。 | **僅為報告值；目前 artifacts 無法獨立核驗。** | 可保留為歷史報告敘述並加限制，不可標成 Verified。 |
| 24 小時報告「100% 攔截攻擊」 | aggregate 記錄總數 160,611、DENY 137,751、ALLOW 22,854、errors 6。`containment_rate_percent` = 137,751 / (137,751 + 22,854) = 85.77%；errors 不納入分母。它沒有獨立的 malicious-request 分母或逐筆分類。 | **無法由 aggregate 重建 100% malicious-blocking claim。** | 報告 aggregate 數量與分母；不得推論 100% 攔截率。 |

## 重現性與範圍說明

舊版 Mobile adapter 是 host process 透過模擬 API wrapper 呼叫 native library；不是實體裝置或 Android AVD 能耗實驗。現在的 TMC Android lane 是另一組 Pixel_7 / Android 34 / x86_64 application-runtime 研究，明確排除實體能耗量測，不能替舊版能耗估算背書。

24 小時 runner 存在，但會隨機選取 scenario、未記錄 random seed、latency samples 僅保存在記憶體，最後寫入固定路徑 `reports/soak_test_24h_report.json`。重跑會產生新的 stochastic run 並覆寫該摘要，不能精確重播原 run。JSON 是 aggregate record，不是 raw event stream；runner 也沒有 memory-profiling instrumentation。因此目前無法建立 exact replay、raw-to-summary reconstruction 或 `0 Bytes` memory claim。

## 未來恢復能耗主張的 closure 條件

恢復任何電池／能耗數字前，必須提供明確裝置與 workload、校準過的實體量測方法（或清楚標記的軟體估算器）、baseline/control、warm-up 與 sample protocol、raw traces、analysis code，以及 hash-closed evidence record。模型估算必須標為 modeled estimate，不可描述成實體量測。
