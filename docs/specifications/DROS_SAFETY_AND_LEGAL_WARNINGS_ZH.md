# ⚖️ DROS 企業級法律免責聲明、安全警語與物理邊界完整揭露
### (Enterprise Safety Warnings, Boundary Disclaimers & Legal Notice)
<!-- dros_component: dros-safety-warnings -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0_ZH.md, DROS_ENTERPRISE_FAQ_AND_AI_ASSIST_GUIDE_ZH.md] -->
<!-- dros_description: 嚴格對標國際上市公司與頂級企業資安軟體標準之完整法律免責條款、高風險警語、防禦極限邊界與合規聲明 -->
<!-- dros_status: Active -->

> **重要公告：** 本文件為 DROS 商業產品（包括 VajraClaw、DROS-Guard、DROS Enterprise Suite）正式交付物之核心法律與安全組成部分。企業客戶在採購、安裝或部署本系統前，**必須完整審閱並同意本文件所述之全部條款、警語與邊界約束**。

---

## 🚫 一、 DROS 物理防禦邊界與「防禦極限之外」之完整揭露 (Boundary Disclosure)

作為一套基於作業系統與 FFI 執行邊界的**確定性運行期治理基座 (Deterministic Runtime Enforcement Substrate)**，DROS 具備極度精確的能力範疇。
為維護誠信與杜絕認知偏差，特此**完整揭露以下 4 大防禦極限與非保護範疇**：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DROS 物理防禦邊界與責任劃分清單                       │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ 1. 純文字語意輸出與對話幻覺   │ ❌ 不在 DROS 攔截範疇 (Out of Scope)        │
│    (Pure Text Prompt Hijack)  │ 原因：DROS 治理「行為與動作」，不審查自然語言│
│                               │ 輸出。需搭配前端 LLM Guardrails 進行防護。  │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. 合規權限內的邏輯錯誤破壞   │ ❌ 不在 DROS 攔截範疇 (Out of Scope)        │
│    (Authorized Logic Errors)  │ 原因：若策略明確允許寫入 `db.table`，AI 覆蓋│
│                               │ 合法資料視為合規操作。需依賴 Level 3 異動率 │
│                               │ 熔斷或 CoW 交易快照回滾機制。               │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. 密鑰洩漏與偽造私鑰簽章     │ ❌ 不在 DROS 攔截範疇 (Out of Scope)        │
│    (Private Key Compromise)   │ 原因：DROS 微內核驗證數位簽章是否與公鑰吻合。│
│                               │ 若私鑰外洩，必須依賴嚴格的 HSM 與冷儲存保護。│
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. 宿主作業系統 Root 級入侵   │ ❌ 不在 DROS 攔截範疇 (Out of Scope)        │
│    (OS-Level Compromise)      │ 原因：若攻擊者取得 Root/Kernel 權限篡改內存，│
│                               │ 屬於宿主 OS 安全範疇，非應用層治理所能涵蓋。│
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## ⚠️ 二、 高風險操作與企業資安警語 (Security Cautions & Warnings)

### 🚨 警語 1：嚴禁非 Admin 角色配置萬用權限 (Wildcard `*` Warning)
> [!CAUTION]
> 在編寫 `policy.yaml` 策略時，**絕對禁止**對任何非管理員 Agent 分配 `action: allow, tool: '*'` 或 `tool: 'admin.*'`。
> 寬鬆的萬用權限將使 DROS 帶內門閘形同虛設。在發布前**必須強制執行 `python cli.py lint` 進行靜態門禁驗證**。

### 🚨 警語 2：外掛預設 Fail-Safe 原則 (Fail-Safe Default Notice)
> [!WARNING]
> 第三方客戶端外掛（如 DSH Plugin）之 `strictFailClosed` 參數預設值為 `false` (Fail-Open / Fail-Safe)，以保護宿主應用程式不因外部網關短暫離線而崩潰。
> 若企業要求**極限零信任防護**，需在正式生產環境顯式啟用 `strictFailClosed: true`。

### 🚨 警語 3：階梯處置 Hard Kill 之資料一致性警示
> [!WARNING]
> 當系統觸發 Tier 3 (Hard Kill) 發送 `SIGKILL` 物理終止行程時，該 Agent 正在執行的非事務性連線將被立即切斷。企業系統應具備事務回滾 (Rollback) 或斷點續傳機制。

---

## 🏛️ 三、 智慧財產權、專利保護與三大層級授權宣告 (Standard 3-Tier IP & License)

所有購買、下載或實施 DROS 之客戶，必須遵守以下三大層級法律邊界：

1. **🔒 核心執行期微內核 (Core Runtime Substrate) ➔ 專利保護 (Patent Pending)**：
   * **專利與智慧財產權聲明：** DROS 確定性執行期治理與微秒級帶內防禦技術已申請美國臨時專利保護（**U.S. Provisional Patent Application No. 64/111,973，Patent Pending**）。所有商業部署、再發行與生產實施權益由康宸園有限公司 (Top Celestial Company Ltd.) 專有保留。
2. **🎁 個人與社群外掛套件 (Community Client / Plugin) ➔ 個人非商業免費授權 (Free for Individuals)**：
   * 賦能個人開發者獲得微秒級帶內硬熔斷保護，但源代碼專有保留，嚴禁第三方進行未經授權之商業轉售或 SaaS 化服務。
3. **🧪 評測沙盒與重現套件 (Benchmark Harness) ➔ 評測工具開源 (Apache-2.0 License)**：
   * 僅開放評測測試腳本與 RFC-001 驗證情境供學術重現與反證評鑑；明確聲明「評測代碼開源 $\neq$ 底層專利技術開源」。

---

## ⚖️ 四、 國際法律標準合規與有限擔保聲明 (Limited Warranty & Liability)

1. **歐盟 AI 法案與美國 NIST 對齊**：
   * DROS 審計鏈與執行邊界設計符合 **EU AI Act (Article 12 / 50)** 及 **NIST SP 800-207 (Zero Trust Architecture)** 之技術規範要求。
2. **免責與有限擔保 (AS-IS Disclaimer)**：
   * 在適用法律允許之最大範圍內，本軟體按「現狀 (AS-IS)」提供。Top Celestial 不對因客戶自身策略配置不當、私鑰遺失或未授權修改所致之業務中斷、資料損失承擔間接或附隨性損害賠償責任。

---
*DROS 企業級法律免責、安全警語與邊界完整揭露 ── 合規透明，國際信賴。* ⚖️🛡️💎
