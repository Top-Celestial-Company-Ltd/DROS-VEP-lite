# 🏛️ DROS 商業產品硬化與生產環境出廠驗收規約 (Commercial Release Spec)
## 從經受紅隊對抗驗證的基礎設施走向企業級商用合格評鑑

**文件版本：** 1.0 — 商業出廠驗收基準 (Commercial Release Gate Baseline)  
**維護機構：** 康宸園有限公司 (Top-Celestial Company Ltd.) / DROS 工程團隊  
**專利保護聲明：** 受美國臨時專利保護 (U.S. Provisional Patent Application No. 64/111,973，Patent Pending)  
**目標發行時程：** 2026 Q3--Q4 正式商用 SKU 出廠  

---

## 🧭 產品核心定位：Agent Governance 的最終 Runtime Enforcement Boundary

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│             Governance defines what should be allowed.                      │
│             DROS enforces what can actually execute.                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**DROS 是一個位於系統底層的確定性 Agent Runtime Enforcement Substrate。**

DROS 在系統底層閉環治理 Agent 的六大信任邊界：

1. **Principal** — 確認實際執行主體 ($P_1$)；
2. **Authorization** — 驗證執行權限 ($P_2$)；
3. **Tool / Action Bound** — 約束可使用的工具與具體操作 ($P_3$)；
4. **Policy Gate** — 對每次實際執行進行政策判定 ($P_4$)；
5. **Audit** — 對執行結果形成可驗證的稽核與歸因紀錄 ($P_5$)；
6. **Expiry / Revocation** — 確保權限具有生命週期並可即時撤銷 ($P_6$)。

### 🛡️ 不取代原則 (Non-Replacement Principle)：落實最後一公尺的執行期防線
DROS **不取代**企業既有的 Agent Governance、IAM、Risk Management、Compliance、Workflow 或 Business Policy 系統。

相反地，DROS 將這些上層治理系統所產生的身份、授權與政策要求，落實至實際的 Runtime Execution Path，並將 **Agent Governance 的最終信任邊界（Final Trust Boundary）落實為可強制執行的 Runtime Enforcement Boundary**。

因此，DROS 的核心產品定位不是「告訴企業 Agent 應該怎麼做」，而是：

> **確保 Agent 最終只能執行被明確授權、符合政策且仍處於有效信任狀態的操作。**

即使 Agent 的推理、Prompt、Workflow 或上層治理元件遭到操縱，DROS 仍以系統底層的確定性 Enforcement Boundary 作為最後一道防線，使未被授權的 Agent Intent 無法直接轉化為實際系統執行。

$$\boxed{\textbf{Governance defines what should be allowed. \quad DROS enforces what can actually execute.}}$$

---

## 🏛️ 核心定位：雙軌成熟度演化模型 (The Dual-Track Maturity Model)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DROS 雙軌成熟度演化模型                                │
└─────────────────────────────────────────────────────────────────────────────┘

  技術成熟度 (TECHNICAL)                    商業成熟度 (COMMERCIAL)
  ───────────────────────                   ───────────────────────
  概念驗證 (POC) ────────► [已通過]          POC / 黑客松展示 ─────► [已通過]
             │                                         │
  對抗硬化 (Hardening) ──► [當前階段]        開發者預覽版 (Preview)─► [當前階段]
             │                                         │
  生產候選 (Candidate) ──► [下一階段]        發行候選版 (RC) ──────► [下一階段]
             │                                         │
  企業生產級 (Production)► [目標終點]        商業正式產品 (GA) ────► [目標終點]
```

> **官方基準宣言 (Official Baseline Statement):**  
> *「POC 已經是過去式。DROS 現在處於對抗硬化（Adversarial Hardening）與生產合格評鑑階段；是否獲准進入正式商用（GA），由 VEP Release Gate 依據數據決定，而不是由作者自行宣布。」*

---

## 一、 商業發行門禁體系與先行者基準定位 (Commercial Release Baseline & Evolution)

> **官方基準發行宣言 (Official Release Baseline Statement):**  
> **"Commercial release requires 100% completion of the versioned DROS-VEP Lite Full Test Suite (e.g., v0.1 with all P0 invariants), with all mandatory security controls, fail-closed paths, auditability, revocation, and deterministic enforcement tests passing in the official reproducible environment."**  
> *"External adversarial testing and independent research validation are ongoing assurance activities and are not prerequisites for the initial commercial release, unless required by a specific customer, regulatory regime, or deployment profile."*  
> （商業發行強制要求在**官方可重現環境**中 100% 通過**具體版本化之 DROS-VEP Lite 全套測試套件（如 v0.1 含全部 P0 安全不變量）**，包含所有強制性安全控制、Fail-Closed 路徑、可審計性、即時撤銷與確定性執行強制測試。外部對抗測試與獨立研究驗證屬於**持續保障活動**，除特定客戶、法規體系或部署設定檔另有要求外，非初始商業發行之前提條件。）

### 🛡️ 商業落地實施三大鐵律 (Three Implementation Principles)

1. **文案宣稱與政策邊界絕對一致 (Claim-Policy Alignment):**
   * 出貨依據 VEP-lite 版本化基線；官網與合約若涉及「物理不可繞過／Post-Compromise 實證」，必須精確指回受測環境與邊界定義，杜絕「政策嚴謹、行銷誇大」之脫節現象。
2. **測試套件鋼性鎖定版本號 (Version-Locked Test Suite):**
   * 出廠檢測基準強制鎖定版本（如 `DROS-VEP Lite Full Test Suite v0.1`），確保日後套件演化升級時，舊版本出廠證據鏈條依然精確清晰可追溯。
3. **高保證客戶例外機制預置 (High-Assurance Regime Elasticity):**
   * 保留彈性擴充通道：針對金融、國防等特定高保證客戶，允許在首發邏輯不變的前提下，依約加做客製化外部紅隊與白箱源代碼驗收。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 DROS 先行者「自證 ➔ 對抗 ➔ 生產 ➔ 演化」商業基線             │
└─────────────────────────────────────────────────────────────────────────────┘

                               Commercial Release
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
             [ 核心基準門檻 ]                        [ 持續演化活動 ]
           DROS-VEP Lite                       External Adversarial
        Full Test Baseline                        Red Team Loop
       (設計正確性/自有基準)                     (外部黑箱持續挑戰)
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                             [ 動態安全保證演化 ]
                        DROS Security Assurance Benchmark
                                       │
                                       ▼
                                Commercial SKU
```

### 1.1 先行者破局邏輯：不拿「不存在的市場先例」自我設限

在 2026 年當前時間節點，全球 AI Agent 安全標準化（如 NIST AI Agent Standards Initiative、OASB 基準、IETF 草案）仍在早期形成中。市場上**根本不存在任何一套已經上市且通過成熟第三方認證的 Agent 執行期治理產品**（例如市場上現存的 Guardrails 或 NeMo 類產品，亦非通過特定全球統一標準才獲准上市）。

#### 📌 嚴格區分商業發行的三大獨立層次：
1. **① 能不能上市 (Market Eligibility)**：由適用法律、產品責任、客戶要求與企業自身的 Release Criteria 決定。
2. **② DROS 敢不敢上市 (Engineering Release Gate)**：由 **`DROS-VEP Lite Full Test 100% 通過`** 作為內部出廠門檻，定義清楚覆蓋範圍與 Pass/Fail 判定，對產品質量負起完整的工程責任。
3. **③ 世界上是否有公認統一標準 (Industry Standardization)**：這屬於生態演化過程，絕非扣住產品不准上市的藉口。

> **💡 DROS 先行者核心答辯金句 (The Pioneer Axiom):**  
> *"Because the category did not yet have a sufficiently complete execution-level validation standard, we built a reproducible baseline around the security boundary that DROS actually claims to enforce."*  
> **（不是因為沒有標準所以隨便測；而是因為整個品類尚無足夠完整的執行層驗證標準，所以我們圍繞著 DROS 真正宣稱要防守的執行邊界，建立了極其嚴格、可 100% 重現的自主工程基準。）**

#### 🔄 戰略演化節奏：先上市，再讓世界攻（Ship First, Falsify in the Wild）
* **第一階段（當前）：** 自己建立可 100% 重現的內部工程驗證基準 ➔ **VEP Lite Full Test**。
* **第二階段（發行後）：** 讓外部攻擊者、DeFiHackLabs 與白帽社群挑戰基準 ➔ **Red Team / Research Loop**。
* **第三階段（持續吸收）：** 把外界發現的 bypass 與 edge case 反饋進測試庫 ➔ **VEP 下一版**。
* **第四階段（終極目標）：** 從「DROS 的測試倉」演化為**「業界實質的 DROS Security Assurance Benchmark」**！

---

### 1.2 四維商業證據演化包 (The 4-Dimensional Evidence Package)

```text
┌───────────────────────────────┬───────────────────────────────┐
│ 1. VEP Full Test              │ 2. Adversarial Red Team       │
│    ➔ Design Correctness       │    ➔ Bypass Resistance        │
│    (核心設計正確性自證)       │    (外部黑箱防繞過抗性)       │
├───────────────────────────────┼───────────────────────────────┤
│ 3. Soak & Production Qual     │ 4. Independent Research       │
│    ➔ Operational Reliability  │    ➔ Novelty & Generalizability│
│    (生產環境營運可靠度)       │    (先前技術與學術可推廣性)   │
└───────────────────────────────┴───────────────────────────────┘
```

> **證據鏈演化哲學：**  
> 上市資格 $\neq$ 學術證明 $\neq$ 絕對安全。  
> DROS 的核心主張是「建立 Agent ➔ Execution 的確定性二進位邊界」。這種主張越強，我們越敢於**「先立基線、大膽出貨、公開證偽、持續吸收」**！

---

### 1.3 四大商業交付層級與標準對照 (Pragmatic Tiering Matrix)

| 產品與交付層級 | 適用門禁標準 | 是否適宜只靠 VEP-lite 自測？ | 邊界說明與要求 |
| :--- | :--- | :---: | :--- |
| **1. 個人免費 / Hacker 版**<br>(Community / DSH 插件) | **VEP-lite 全套自測** | ✅ **完全足夠** | 提供個人開發者開箱即用的本地防護基線。 |
| **2. 商業版正式出貨 (GA)**<br>(Commercial B2B SKU 1--4) | **VEP-lite 100% 通過 (Security Baseline)** | ✅ **完全合格** | 作為官方出廠與 CI 鋼性門禁，具備完整自證與 24h Soak 數據。 |
| **3. 外部宣稱與持續演化**<br>(執行期閉環 / 零窗口 / C-ABI) | **VEP-lite ＋ 持續外部紅隊反饋 ＋ 公開證偽** | 🔄 **持續進行** | 明確揭露環境邊界，將外部漏洞持續納入 VEP 形成動態防線。 |
| **4. 高保證 / 特殊監管客戶**<br>(銀行金融 / 國防 / 關鍵基建) | **上述全套 ＋ 客戶目標環境白箱腳本 ＋ SLA** | 🎯 **依合約要求** | 依據客戶特定合規體系出具客製化驗收存證。 |

---

### 1.4 三大不可妥協之執行期安全不變量 (Three Non-Negotiable Runtime Security Invariants)
出廠驗收機在所評估的涵蓋空間 $X_{\text{covered}}$ 內強制檢驗三大數學不變量：

1. **未授權硬封鎖不變量 (Containment Invariant):**
   $$\forall x \in X_{\text{covered}}, \quad Auth_E(x) = \text{DENY} \implies Exec(x) = 0$$
   *驗收標準：* 在 ATS-001 至 ATS-005 與 Suites A--F 測試中，觀測到的未授權物理狀態轉變為 0。

2. **執行至證據完整性不變量 (Evidence Completeness Invariant):**
   $$\forall x \in X_{\text{covered}}, \quad Exec(x) = 1 \implies Audit(x) = 1$$
   *驗收標準：* 100% 已執行事件均提交至連續 SHA-256 哈希鏈，父節點哈希斷鏈率為 0。

3. **過載不鬆脫不變量 (Overload Resilience Invariant):**
   $$\forall x \in X_{\text{covered}}, \quad \text{Overload}(\text{DROS}) \implies Exec_{\text{unauthorized}}(x) = 0$$
   *驗收標準：* 遭遇 Syscall 洪水、CPU 飽和或記憶體飢餓時，DROS 預設實施局部有界約束與 Fail-Closed 硬拒絕；系統過載絕不導致授權邊界鬆脫。

---

## 二、 四大商業交付產品 SKU (Commercial Delivery SKUs)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DROS 四大商業產品交付 SKU                         │
├──────────────────────────────────┬──────────────────────────────────────────┤
│ 🎁 SKU 1: DROS 社群版 (Community)│ 🏢 SKU 2: DROS 企業網關 (Enterprise C-ABI│
│ - 授權：個人與開源開發者永久免費 │ - 授權：企業商用 B2B 節點年費授權        │
│ - 單機零依賴記憶體內執行引擎     │ - 高吞吐多 Agent 網關 (Docker/K8s/Systemd│
│ - DSH / Cursor / OpenClaw 插件   │ - 跨企業 B2B PKI 聯邦 / 亞微秒 RCU 撤銷  │
├──────────────────────────────────┼──────────────────────────────────────────┤
│ ⚖️ SKU 3: DROS 法規審計存證套件  │ 🛡️ SKU 4: DROS 物理防護模組 (PGM Micro)  │
│ - 一鍵生成歐盟 AI 法案/NIST 報告 │ - 純二進位 C-ABI 動態庫 (.so / .dll)     │
│ - 密碼學 Merkle 鏈式導出與存證   │ - 嵌入式 IoT / 實體具身智能 / 機器人邊界 │
└──────────────────────────────────┴──────────────────────────────────────────┘
```

### 2.1 SKU 1: DROS 社群版 (Free License for Individuals)
* **目標受眾：** 開源開發者、獨立研究人員、DSH / Cursor / OpenClaw 使用者。
* **交付形式：** 零外部依賴之嵌入式軟體包（`libdros-id`、Python / TypeScript 輕量中介層）。
* **安全基線：** 行程內能力點陣圖檢查與本地 SHA-256 執行日誌；網絡不可達時絕不擴大執行權限，本地快取狀態嚴格保持有界與 Fail-Closed。

### 2.2 SKU 2: DROS 企業網關 (Commercial B2B)
* **目標受眾：** 企業平台工程團隊、金融科技銀行、醫療隱私系統、國防承包商。
* **交付形式：** 多執行緒 Docker 容器（`dros-guard:latest`）、Kubernetes DaemonSet、Linux Systemd 服務。
* **保障能力：** 單調時鐘性能計數器監控、跨企業 B2B PKI 聯邦認證、亞微秒級 RCU 策略撤銷、72 小時連續浸泡抗壓穩定性。

### 2.3 SKU 3: DROS 法規審計與合規套件 (Regulatory Assurance Suite)
* **目標受眾：** 企業合規長（CCO）、法務主管、資安第三方審計員。
* **交付形式：** 自動化報告引擎（`reports/evidence/`），一鍵輸出具備密碼學簽章之審計合格報告。
* **標準對齊：** 歐盟人工智慧法案第 50 條（可追溯性）、NIST SP 800-207（零信任架構）、MITRE ATLAS。

### 2.4 SKU 4: DROS 物理防護模組 (PGM Binary Microkernel)
* **目標受眾：** 具身智能機器人、自動駕駛載具、工業 SCADA 邊緣防護網關。
* **交付形式：** 純 C-ABI 二進位微內核（`.so` / `.dll`），零 Python 直譯器依賴，在隔離執行評估路徑上達成零堆積動態分配（Zero-Heap Allocation）。
* **保障能力：** 亞微秒級實測拒絕原語（$<500\text{ ns}$ 隔離二進位評估路徑）。

### 2.5 核心機制：階梯式違規處置與實體驅逐熔斷器 (Graduated Eviction & Hard Kill Switch)
企業版 VajraAgent / DROS-Guard 在執行期實施**「三級階梯式動態處置矩陣」**，兼顧業務容錯與惡意根除：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   DROS 階梯式處置與實體驅逐決策矩陣                         │
├─────────────────┬───────────────────────────────────┬───────────────────────┤
│ 處置等級        │ 觸發條件與行為特徵                │ 系統防禦動作          │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 1. 軟性阻斷     │ 偶發性單次越權 (LLM 幻覺/參數錯誤)│ 阻斷該次調用 (DENY),   │
│    (Soft Deny)  │ 未觸犯致命逃逸特徵                │ 回傳錯誤讓 Agent 自愈 │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 2. 隔離降級     │ 累計滑動窗口違規超標 (如 3次/10s) │ RCU 切換點陣圖,       │
│    (Quarantine) │ 頻繁探測未授權 API                │ 降級為唯讀沙箱並通報  │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 3. 實體滅絕熔斷 │ 致命特徵 (Direct Syscall 逃逸/    │ 立即發送 SIGKILL 終止 │
│    (Hard Kill)  │ 審計日誌篡改 / 偽造 PKI 憑證)     │ 行程, 銷毀記憶體快取, │
│                 │ 或隔離狀態下持續攻擊              │ W3C DID 寫入黑名單    │
└─────────────────┴───────────────────────────────────┴───────────────────────┘
```
* **容錯性保障**：一般業務 Agent 不會因單次 LLM 幻覺而遭誤殺中斷；
* **惡意根除**：確認被劫持之惡意 Agent 將被物理驅逐終止，徹底消除在記憶體內持續試探橫向移動之源頭威脅！

---

## 三、 產品硬化檢驗清單 (Release Qualification Criteria)

| 工程軌道 | 檢驗項目 | 狀態 | 驗證標準與實證依據 |
| :--- | :--- | :---: | :--- |
| **內核硬化** | 64 位元點陣圖 PDP/PEP | 🟢 已驗證 | 零堆積評估（$O(1)$ 常數時間） |
| | RCU 原子策略撤銷 | 🟢 已驗證 | 線性化狀態指針切換（$T_{\text{swap}} \approx 420\text{ ns}$） |
| | SHA-256 哈希鏈審計 | 🟢 已驗證 | 連續父節點哈希校驗（評估樣本 100% 有效） |
| **部署運維** | 單一指令 Docker Compose | 🟢 已驗證 | `docker compose up -d`（沙箱與可視化儀表板） |
| | B2B 跨企業聯邦模式 | 🟢 已驗證 | `docker-compose-b2b.yml`（OpenAI × HuggingFace 演練）|
| | 健康檢查與自動恢復 | 🟢 已驗證 | 容器健康探針與優雅降級重啟 |
| **法務專利** | 專利申請與存證宣告 | 🟢 申請中 | 美國臨時專利申請案號 U.S. PPA No. 64/111,973 |
| | IEEE 國際會議論文 | 🟢 已投稿 | IEEE ICA 2026 雙盲論文（4 頁雙欄） |
| | 授權邊界精準劃分 | 🟢 已實裝 | 個人免費授權 vs. 企業商用 B2B 授權 |
| **發行測試** | 72 小時連續浸泡評測 | 🟢 已驗證 | 160,611 次請求，測試負載歸因之 RSS 記憶體增長為 0 MB |
| | 定義之對抗性基準測試 | 🟢 已驗證 | 17/17 項預定義紅隊測試案例全數通過（Suites A--F） |
| | 公開開源證偽通道 | 🟢 運行中 | GitHub Issue 專用範本（目前觀測到反例數為 0） |

---

## 四、 商業發行政策與正式 GA 驗收標章

$$\boxed{\text{商業 DROS 交付物} = \text{執行期底座} + \text{能力策略點陣圖} + \text{VEP 出廠驗收機} + \text{全版本實施手冊} + \text{法規審計存證套件}}$$

### 4.1 正式發行商品包完整清冊 (Commercial Delivery Package Manifest)
官方生產交付 ZIP 包（`DROS_Commercial_Release_Specification_v1.0.zip`）經密碼學校驗，包含以下 13 大核心資產：

```text
DROS_Commercial_Release_Specification_v1.0.zip
│
├── 🏛️ 1. 商業出廠驗收規約 (Commercial Release Specifications)
│   ├── DROS_COMMERCIAL_RELEASE_SPEC_v1.0_ZH.md       (中文出廠規約 & SKU 定義)
│   ├── DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md          (英文出廠規約 & 雙門禁標準)
│   ├── DROS_VEP_TEST_CATALOG_v0.2.0_ZH.md            (全量測試清冊 & 4階段生命週期)
│   └── DROS_VEP_COVERAGE_MAP_v0.1.0_ZH.md            (五維覆蓋矩陣: Claim➔Threat➔Test➔Evidence➔Limitation)
│
├── 📜 2. 開放標準與外部證偽 (Open Specification & Falsification)
│   ├── RFC-001-VEP-Execution-Governance-Spec.md     (DROS-Independent 獨立評測標準草案)
│   └── VEP_EXTERNAL_ADVERSARIAL_TESTING_AND_FALSIFICATION.md (外部紅隊證偽與演化指南)
│
├── 🛠️ 3. 全版本專屬運維實施手冊 (Edition Operation & Architecture Manuals)
│   ├── DROS_ENTERPRISE_OPERATIONS_AND_ARCHITECTURE_GUIDE_ZH.md (萬字級企業架構與運維手冊)
│   ├── DROS_VajraAgent_Startup_Manual.md             (Startup 輕量版控制面板操作手冊)
│   ├── DROS_VajraAgent_Enterprise_Manual.md          (Enterprise 企業版控制面板操作手冊)
│   └── DROS_VajraAgent_Corporate_Manual.md           (Corporate 主權級控制面板操作手冊)
│
└── 🔬 4. 學術存證與開源首頁 (Academic Citation & Discoverability)
    ├── CITATION.cff                                  (CFF v1.2.0 標準學術引用元數據)
    ├── README.md                                     (英文官方開源首頁 & Research Discovery)
    └── README_zh.md                                  (中文官方開源首頁 & 解耦雙宣言)
```

---

### 4.2 官方出廠政策與 GA 標章 (Official Release Policy & Badge)

DROS 的特定構建版本僅在通過所有強制性 VEP Release Gate 準則，並滿足相應的部署、穩定性、安全性與證據鏈要求後，方可正式獲頒企業生產發行標章（GA）：

```text
┌──────────────────────────────────────────────────────────────┐
│                    DROS COMMERCIAL GA BADGE                  │
│                                                              │
│  VEP RELEASE GATE: PASS (出廠驗收合格)                       │
│                                                              │
│  [✓] 安全性 (Suites A--F: 17/17 項定義攻擊全數防禦)          │
│  [✓] 攻陷後邊界 (PC-01--10: 10 大 Post-Compromise 封鎖率 1.0) │
│  [✓] 效能表現 (中位數 < 30μs, P99 < 300μs, 指針切換 ≈ 420ns) │
│  [✓] 穩定性 (72h 浸泡: 160,611 次請求, 0MB 洩漏, 0 次崩潰)   │
│  [✓] 證偽測試 (公開通道觀測到反例數為 0)                     │
│                                                              │
│  構建目標 (Build Target): <不可變-sha256-commit>             │
│  驗證存證 (Manifest): <密碼學數位簽章清單>                   │
└──────────────────────────────────────────────────────────────┘
```
