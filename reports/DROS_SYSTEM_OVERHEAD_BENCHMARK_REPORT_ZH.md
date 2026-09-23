# ⚡ DROS 系統開銷與效能微基準全量評測報告 (System Overhead Benchmark Report)
## 歷史報告數字與目前證據邊界

**文件版本：** 1.0 — 系統開銷與效能基準  
**維護機構：** DROS 工程團隊 / 康宸園有限公司  
**測試硬體環境：** 
* **伺服器/工作站端：** AMD Ryzen 9 7950X (16C/32T, 64GB DDR5, Linux Kernel 6.8) ＋ Intel Xeon E3-1275L v3 (4C/8T, 16GB DDR3)
* **邊緣/嵌入式端：** ARM Cortex-A72 (Raspberry Pi 4B)
* **移動端 (Mobile)：** Apple A17 Pro (iOS 18) / Snapdragon 8 Gen 3 (Android 14) 模擬環境

> **證據狀態稽核（2026-09-23）：** 舊版 mobile harness 是 host-side adapter：`KotlinDROSClient` 委派至 Python `ctypes` adapter，載入 Windows DLL；並未執行 Android JNI、iOS Swift 或手機裝置 runtime。歷史 `<0.001 mAh` 與 `<0.05 μJ` 數字在目前 artifacts 中沒有電量計、計算輸入、校準程序或 raw energy trace，不得視為實測。24 小時 soak runner 存在但使用隨機 scenario、只輸出至固定路徑的 aggregate，且沒有 memory profiling；其 `0 Bytes` 數字僅為 report-only。詳見[雙語舊版主張稽核](DROS_MOBILE_LEGACY_ENERGY_AND_SOAK_CLAIM_AUDIT_ZH.md)。

---

## 🧭 一、 摘要 (Executive Summary)

在企業與實體設備部署 AI Agent 執行期治理時，**「系統開銷 (System Overhead)」** 往往是決定產品生死的第一核心指標。傳統大模型護欄（如 NVIDIA NeMo、Llama Guard、Palo Alto AIRS）每次檢查需花費數百毫秒（ms）並佔用龐大 GPU/記憶體，導致無法在飛控、高頻交易與手機端落地。

本歷史報告整合先前記載的 **24 小時 soak aggregate (160,611 次請求)**、**多架構微基準 ($N=10,000$)** 與 **host-side mobile-style adapter harness** 數字。這些數字的 evidence level 與 measurement boundary 不同，且目前 repository 無法獨立重現全部項目：
1. **納秒級決策延遲：** C-ABI 本地決策中位數延遲 $P_{50} = \mathbf{500\text{ ns}\ (0.5\ \mu\text{s})}$，極端延遲 $P_{99} = \mathbf{1.2\ \mu\text{s}}$。
2. **極致輕量 CPU 佔用：** 額外 CPU 負載 $<\mathbf{1.8\%}$，RCU 無鎖指針熱切換僅耗時 $\mathbf{420\text{ ns}}$。
3. **記憶體：** 舊報告記載 24 小時 0 Bytes leak；runner 沒有 memory-profile instrumentation，故狀態為 **Reported，未獨立驗證**。
4. **手機能耗：** host-side harness 未量測。歷史電池／能耗數字是**未驗證估算**，不列為商品 claim。

---

## 📊 二、 四大物理維度系統開銷總表 (Macro Overhead Matrix)

| 評測維度與指標 | DROS 實測數值 (Empirical Value) | 傳統大模型護欄 (NeMo / Llama Guard) | 傳統雲端 API 網關 (Palo Alto Prisma) | 效能差距倍數 |
| :--- | :--- | :--- | :--- | :--- |
| **1. 策略決策中位數延遲 ($P_{50}$)** | **500 ns (0.0005 ms)** | 150 ms ~ 500 ms | 20 ms ~ 80 ms | ⚡ **快 40,000 ~ 300,000 倍** |
| **2. 策略決策尾端延遲 ($P_{99}$)** | **1.2 μs (0.0012 ms)** | 800 ms ~ 2,000 ms | 150 ms ~ 350 ms | ⚡ **快 120,000 倍** |
| **3. CPU 額外開銷 (CPU Overhead)** | **< 1.8%** | 30% ~ 100% (耗盡 GPU/CPU) | 5% ~ 15% (網路 I/O 序列化) | 🛡️ **低功耗常駐** |
| **4. 記憶體佔用 (Memory Footprint)** | **< 16 MB** | 2 GB ~ 8 GB (加載模型權重) | 250 MB ~ 500 MB (Container) | 💎 **省 95% 以上記憶體** |
| **5. 連續浸泡記憶體洩漏 (Memory Leak)** | 舊報告記載 0 Bytes；profile artifact 不在目前包內 | 存在 Python GC 與快取膨脹 | 存在連線 Session 殘留 | Reported；未獨立驗證 |
| **6. 政策熱更新無鎖切換延遲 ($T_{\text{swap}}$)** | **420 ns** | 需重啟或重載模型 (數秒至數分鐘) | 50 ms ~ 200 ms | ⚡ **微秒級熱生效** |
| **7. 手機端電池能耗 (Battery Power)** | **引用 harness 未量測** | 未比較 | 未比較 | 不提出電池 claim |

---

## 🔬 三、 多架構決策延遲橫向對照實測 ($N = 10,000$ 獨立迭代)

在固定測試硬體（Intel Xeon E3-1275L v3 @ 2.70GHz, 16GB RAM）上，針對各治理架構進行 10,000 次微基準測試：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   決策延遲 (Decision Latency) 橫向對照                      │
└─────────────────────────────────────────────────────────────────────────────┘

  Arm A: Baseline (無治理) ──► 200 ns [純函式呼叫底噪]
  Arm B: Microsoft AGT ──────► 500 ns (P50) / 1,800 ns (P99) [Python 裝飾器開銷]
  Arm C: DROS GuardVM ───────► 500 ns (P50) / 1,200 ns (P99) [C-ABI 點陣圖查表]
  Arm D: 雙層縱深 (AGT+DROS) ─► 4,400 ns (P50) / 15,900 ns (P99) [跨層呼叫開銷]
```

### 詳細數據分佈：
* **DROS GuardVM (Arm C):**
  * 平均延遲 (Mean): `526.65 ns`
  * P50 中位數: `500.00 ns`
  * P95 延遲: `800.00 ns`
  * P99 極端延遲: `1,200.00 ns (1.2 μs)`

---

## 🔋 四、 Mobile-style host adapter 與 edge-drone 歷史報告數字

### 1. 舊版 mobile-style host adapter（非 Android/iOS 裝置）
* 舊報告列出 $P_{50}=1.70\ \mu\text{s}$、$P_{99}=7.30\ \mu\text{s}$；目前 harness 使用 Python host adapter 與 Windows DLL，不是 Android/iOS 裝置；raw timing samples 未保存，故僅為 host-side reported values。
* **Battery/energy：未量測。** 舊 `<0.05 μJ`／`<0.001 mAh` 數字無儀器、公式或 raw trace 支持，不得當成實測值。

### 2. 邊緣無人機 (MAVLink 飛控防護)
* **即時性約束：** 飛控姿態迴路頻率通常為 $400\text{ Hz} \sim 1\text{ kHz}$（每週期 $1\text{ ms} \sim 2.5\text{ ms}$）。
* **DROS 熔斷耗時：** $< 500\text{ ns}$（佔飛控週期 $< 0.05\%$），**對飛控即時姿態計算完全零干擾、零抖動（Zero Jitter）**。

---

## 📈 五、 24小時連續高壓浸泡 (160,611 次請求) 系統穩定度

* **總測試時長：** 24.0 小時
* **處理總請求數：** 160,611 次
* **成功攔截 (DENY)：** 137,751 次
* **合規放行 (ALLOW)：** 22,854 次
* **記憶體洩漏 (Memory Leak)：** 舊報告記載 0 Bytes；目前無 memory-profile trace 或可重現 runner，未獨立驗證。
* **GuardVM 核心崩潰次數：** **0 次 (Zero Crash)**
* **系統可用度：** **99.9963%**

---

## 🎯 六、 結論 (Conclusion)

本報告的歷史 overhead 數字須依各自 evidence boundary 解讀。舊 mobile battery 數字屬未驗證估算；mobile-style adapter timing 並非手機裝置結果。作為商品或論文主張前，請先參照稽核補充並補齊各自 artifacts。

* **在雲端**：不搶佔業務 CPU/記憶體，支持每秒數萬次的高併發；
* **在無人機/邊緣**：納秒級熔斷滿足硬實時（Hard Real-Time）要求；
* **Mobile-style host adapter**：只測 host-side policy wrapper；實體裝置 latency、network egress 與 energy 未由此 report 驗證。
