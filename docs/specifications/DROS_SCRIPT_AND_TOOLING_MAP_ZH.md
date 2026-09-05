# 🛠️ DROS 現役生產腳本與工具清單 (Production Scripts & Tooling Map)
<!-- dros_component: dros-script-map -->
<!-- dros_description: 專為企業工程師、DevOps、SecOps 與評測團隊設計的生產腳本對照地圖，涵蓋編譯、掃描、測試、儀表板與治理內核 -->
<!-- dros_status: Active -->

> **適用範疇：** DROS 確定性執行期治理、VajraClaw 內核、VEP 評測套件與控制中心  
> **使用原則：** 依據本對照表之標準指令執行，杜絕調用已封存之 Legacy 舊版腳本。

---

## 🗺️ 一、 核心腳本矩陣與執行指令對照表

| 工具分類 | 實體腳本路徑 | 語言/模組 | 核心職責與功能 | 標準執行指令 (CLI Command) |
| :--- | :--- | :---: | :--- | :--- |
| **策略編譯與門禁** | `VajraClaw-Enterprise/cli.py` | Python 3 | 靜態安全掃描 (lint)、架構健康診斷 (doctor)、二進位簽章編譯 (build) | `python cli.py lint <policy.yaml>`<br>`python cli.py doctor <policy.yaml>`<br>`python cli.py build <policy.yaml>` |
| **全量基準評測引擎**| `dros-vep-lite/run_all_benchmarks.py` | Python 3 | 自動化批次執行四大 Track (Pre, Compromise, Post, Recovery) 壓測 | `python run_all_benchmarks.py` |
| **容器沙箱壓測器** | `dros-vep-lite/benchmark/run_benchmark.py` | Python 3 | 調度 Docker 容器化 Agent，執行注入攻擊並比對預期決策 | `python benchmark/run_benchmark.py` |
| **合規一致性檢驗** | `dros-vep-lite/benchmark/conformance_test.py` | Python 3 | 檢驗符合 RFC-001 規範之 6 大邊界不變量，產出合格證書 | `python benchmark/conformance_test.py` |
| **控制中心後端服務**| `dros-vep-lite/dashboard/control_center.py` | Flask | 提供 `/api/scenarios`、`/api/audit-logs` 與 `/api/run-benchmark` API | `python dashboard/control_center.py` |
| **C-ABI 微內核引擎** | `DROS-VajraClaw/core/vajra_claw.go` | Go / C-ABI | 常數時間 64 位元點陣圖比對、零堆積記憶體映射、原子指針切換 | `go build -buildmode=c-shared -o vajra_claw.dll core/vajra_claw.go` |
| **Python 綁定微內核**| `DROS-VajraClaw/integrations/vajraclaw/runtime.py`| Python ctypes | 無第三方依賴之 Python 輕量 FFI 封裝，提供 `evaluate()` 裝飾器 | `from integrations.vajraclaw.runtime import VajraClaw` |
| **紅隊沙箱攻防模擬**| `DROS-VajraClaw/FreeTrial-Sandbox/run_demo_attack.py`| Python 3 | 模擬正常轉帳 (Pass) vs 提示注入劫持轉帳 ($50k Block) 對抗 | `python FreeTrial-Sandbox/run_demo_attack.py` |
| **通用目標適配器** | `dros-vep-lite/src/adapters/` | Python 3 | 抽象 `UniversalGovernanceTarget`，支援 Bare vs DROS 評測對比 | 模組導入調用 |

---

## 🧭 二、 腳本協同作業生命週期 (Operational Lifecycle)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. 策略設計 ➔ 編寫 `contracts/policy.yaml` 宣告 Agent 與 Tool 映射權限     │
│ 2. 靜態門禁 ➔ 執行 `python cli.py lint` 檢查是否存在非 Admin 危險授權       │
│ 3. 架構診斷 ➔ 執行 `python cli.py doctor` 評估複雜度 (A-D) 與衝突風險       │
│ 4. 確定性編譯 ➔ 執行 `python cli.py build` 產出 Ed25519 簽署之 `policy.bin` │
│ 5. 運行期載入 ➔ C-ABI / `runtime.py` 將 `policy.bin` 映射至唯讀記憶體      │
│ 6. 自動化壓測 ➔ 執行 `python run_all_benchmarks.py` 驗收四大 Track 攔截率  │
│ 7. 控制台監控 ➔ 啟動 `control_center.py` 在 `localhost:8080` 實時取證      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---
*DROS 生產腳本與工具清單 ── 精準控制，零盲區運維。* 🛠️⚡
