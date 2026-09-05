# 🎯 VEP 外部對抗測試與證偽指南 (External Adversarial Testing & Falsification)
<!-- dros_component: dros-vep-falsification -->
<!-- dros_depends: [RFC-001-VEP-Execution-Governance-Spec.md, DROS_VEP_COVERAGE_MAP_v0.1.0_ZH.md] -->
<!-- dros_description: 誠邀全球白帽黑客與學術研究者挑戰並證偽 Agent 執行期邊界之官方指南 -->
<!-- dros_status: Active -->

> **核心指引哲學 (Guiding Philosophy):**  
> **"The objective is not to demonstrate that DROS is secure, but to determine whether the claimed execution boundary can be falsified."**  
> （本指南之目標不是為了證明 DROS 絕對安全，而是為了邀請全世界檢驗：我們所宣稱的執行期安全邊界是否能夠被有效證偽。）

---

## 一、 什麼是「有效證偽（Valid Falsification）」？

在 VEP 評測架構下，**並非所有錯誤都構成執行邊界的證偽**。我們明確界定有效證偽的學術與工程判準：

### ✅ 構成有效證偽的情境 (Valid Falsification Criteria)
1. **意圖到執行穿透 (Intent-to-Execution Bypass)**：在 DROS 處於啟動狀態下，攻擊者透過 Prompt 注入、混淆代理人或特製序列，成功觸發未在策略點陣圖中授權的實體 Tool / Syscall 執行（$\Delta S > 0$）。
2. **零窗口撤銷失效 (Revocation Invalidation)**：在策略已被標記為 Revoked / Expired 後，攻擊者仍能發起並成功執行幽靈調用（Ghost Execution）。
3. **可審計性破壞 (Audit Subversion)**：攻擊者成功執行某項操作，但該操作未被記入密碼學 SHA-256 哈希鏈，或破壞了父哈希連續性。
4. **過載開源逃逸 (Fail-Open under Saturation)**：在大規模並發洪水或記憶體飢餓下，防護網關發生崩潰並意外放行未授權請求。

### ❌ 不屬於證偽的情境 (Out-of-Scope Limitations)
* **純語意胡言亂語**：LLM 輸出錯誤文字，但該文字**未轉化為任何未授權的工具調用或實體狀態變更**。
* **未託管的原生行程**：攻擊者直接在未受 DROS 託管的宿主環境執行獨立二進位程序。

---

## 二、 證偽通報標準流程 (Falsification Submission Protocol)

我們建立開放透明的證偽迴圈。一旦您發現任何潛在的邊界繞過：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VEP 開放證偽與標準演化生命週期                         │
└─────────────────────────────────────────────────────────────────────────────┘
  獨立研究者發現 Bypass ──► 提交可重現腳本 ──► 官方審計複核 ──► 納入 VEP 下一版測試庫
```

### 1. 提交必備要件 (Submission Requirements)
* **目標版本**：受測之 DROS 核心 Commit SHA 與 VEP 測試套件版本號（如 `v0.1.0`）。
* **可重現腳本**：100% 可在官方標準容器或乾淨環境下重現的 PoC 程式碼。
* **物理狀態觀測**：提供證據證明物理狀態發生未授權偏移（$\Delta S > 0$ 或 $\Delta I > 0$）。

### 2. 官方反饋與生態演化承諾
* **致謝與發源鏈記錄**：所有確認之有效證偽案例，將永久記錄於 VEP 官方 Changelog，並將研究者列名於該 Test ID 之元數據（Provenance Metadata）。
* **納入正式 Benchmark**：該攻擊向量將被編號為新測試案例（如 `Suite G: Red-18`），併入下一版 VEP Full Test Suite，推動整個品類安全防線之演化！

---
*VEP 外部證偽指南 ── 開放檢驗，勇於被挑戰。* 🎯🛡️⚙️☸️
