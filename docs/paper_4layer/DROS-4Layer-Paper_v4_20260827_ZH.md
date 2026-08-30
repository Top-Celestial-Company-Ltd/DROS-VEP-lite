# 🛡️ DROS: 針對自主 AI 工作負載中「Agent至執行歸因治理」的四層執行期作業基板與確定性執行強制機制 (v4.0)

## 漸進式對抗驗證、元驗證與開放式證偽 (Progressive Adversarial Validation, Meta-Verification, and Open Falsification)

**文件版本：** 4.0 研究論文 / 同行評審手稿  
**日期：** 2026 年 8 月 27 日  
**作者：** 陳俊成 (Chun-Cheng / Jimmy Chen) (`jimmychen@dr-os.io`)  
**所屬機構：** 康宸園有限公司 (Top-Celestial Company Ltd.), 台灣台北  
**專利聲明：** DROS 執行治理與安全技術已申請美國臨時專利保護（U.S. Patent Application No. 64/111,973，Patent Pending）。  
**開源存證靶場與可重現性資產：** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**永久學術文獻引用 (DOI)：** [Zenodo Record DOI: 10.5281/zenodo.21755653](https://doi.org/10.5281/zenodo.21755653)

---

## 摘要 (Abstract)

隨著自主 AI Agent 普遍持有合法憑證、委託能力並能調用具實體後果之工具，高層 Agent 意圖與底層物理執行之間產生了嚴重的歸因斷層（Attribution Gap）。本文提出 DROS，一套將 Agent 身分與執行授權解耦、並在二進位 C-ABI 邊界強制執行能力約束的四層執行期作業基板。本文不預設安全已被先驗證明，而是將 DROS 表述為一個可被實驗證偽的執行治理邊界，並引入結合自主攻擊搜尋、負向對照、變形測試、獨立帶外神諭（Ground-Truth Oracle）、並發壓力與開源可重現性的漸進式對抗驗證方法論。本評測體系將因果鏈解構為「意圖、授權、執行與物理效應」，使強制決策得與內核及外部狀態觀測進行獨立交叉驗證。在涵蓋自適應攻擊、多 Agent 委託鏈、撤銷競態、突變測試與神諭探針的實例化評測語料庫中，於明確儀表化之觀測邊界內未觀測到任何未授權物理效應。本文將所得保證宣告為評測狀態空間上的實證不變量而非全域安全證明，並開源評測基板與反例協議以實現持續之對抗性證偽。

**關鍵字：** AI Agent 安全、執行期作業基板、受控 C-ABI 授權邊界、自主對抗性評測、RCU 狀態切換、動態資訊流控制 (IFC)、歸因治理。

---

## 1. 引言與語義-內核悖論 (Introduction & Semantic-Kernel Paradox)

當自主 AI Agent 具備合法憑證、OAuth 會話 Token 與資料庫連線權限時，在已驗證身分的應用層濫用情境下，傳統周界控制單獨運作顯然不足，因為惡意行為係來自經認證的內部實體。

### 1.1 語義-內核悖論 (The Semantic-Kernel Paradox)
現代系統文獻指出了 AI 防禦機制的根本分裂：
1. **語義應用中介軟體 (高語義，零確定性)：** 提示詞防火牆、JSON 模式驗證器與應用中介能理解自然語言與宣告架構。然而它們缺乏執行邊界約束力；一旦攻擊者利用直譯器逃逸（`eval`、`bash`）或未宣告路徑，此類應用層策略即告失效。
2. **內核沙盒機制 (高確定性，零語義)：** OS 底層機制（如 Seccomp、Linux Namespaces、eBPF）能強制執行二進位系統呼叫規則，但無法識別同一個 Worker 行程中的資料庫連線是由合法的財務 Agent 還是被劫持的客服 Agent 所發起。

### 1.2 DROS 四層基板物理架構定位與核心設計主張 (Core Design Thesis)
DROS 介於上層應用框架與底層作業系統之間，確立四層深度防護（**L1 機率性偵測可能失效，但 L2–L4 確定性強制約束**）：

```text
應用層框架 (OpenAI Agents, LangGraph, CrewAI, AutoGen)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ L1: 偵測情報層 (Detect - 語義過濾與啟發式防護)              │
├─────────────────────────────────────────────────────────────┤
│ L2: 身分與零信任網格 (Attribute - 3-Tier PKI + DIT 綁定)    │
├─────────────────────────────────────────────────────────────┤
│ L3: 動態 IFC 資料治理 (Constrain Data - 污點追蹤與遮蔽)     │
├─────────────────────────────────────────────────────────────┤
│ ★ L4: 實體執行強制層 (Enforce - 亞微秒 Fail-Closed 拒絕路徑)│
└────────────────────────────┬────────────────────────────────┘
                             │ (受控二進位 C-ABI / FFI 授權邊界)
                             ▼
  底層作業系統 / 實體後端 API / 資料庫 (OS Syscall, Physical Side-Effects)
```

### 1.3 本文核心主張與研究問題 (Core Thesis & Research Questions)
> **DROS 不宣稱「安全已被先驗證明」，而是建立一個可被持續證偽的確定性執行治理邊界 (An experimentally falsifiable execution-governance boundary)。**

為系統化驗證此一主張，本文明確設定並回答以下四個核心研究問題：
* **RQ1 (Enforcement / 強制執行有效性)**：在應用層完全受陷 ($C_A = 1$) 的 Post-Compromise 條件下，受治理執行路徑能否確定性阻止未授權操作轉化為儀表化物理副作用？
* **RQ2 (Revocation / 並發撤銷原子性)**：在並發執行與策略撤銷的時間競態下，是否存在因過期策略產生的非預期授權窗口？
* **RQ3 (Evaluator Sensitivity / 評測敏感度)**：評測框架與測試基板能否有效捕獲故意植入的安全退化與變形突變體？
* **RQ4 (Oracle Independence / 神諭獨立性)**：授權判定是否能由執行端與實體端解耦的獨立觀測者完成客觀交叉驗證？

---

## 2. 威脅模型、評測空間與認識論邊界 (Threat Model & Epistemic Boundaries)

### 2.1 受陷後執行期威脅模型 (Post-Compromise Assumptions: $C_A = 1$)
本文評測建立在嚴格的**「受陷後 (Post-Compromise)」**前置假設之上：
* **假設 1 (應用層與 Agent 完全受陷 $C_A = 1$)**：攻擊者已達成 Prompt Injection、掌握內部宣告的 Tool Schema，並能直接操作直譯器上下文與變數。
* **假設 2 (合法憑證持有)**：攻擊者持有有效的 OAuth Session Token、資料庫連線字串或內部 API 金鑰。
* **假設 3 (多 Agent 串謀與代理)**：攻擊者控制多個異質 Agent，並嘗試透過多跳委派（Delegation Chain）與混淆代理人（Confused Deputy）進行特權提升。
* **信任根約束**：受控二進位 C-ABI / FFI 執行閘門與 OS 內核隔離機制。

### 2.2 四大基準線拓撲定義與攻擊保留原則 (Baselines & Attack Preservation)
為防止因攻擊負載差異產生評測偏差，評測嚴格遵循**攻擊保留原則 ($A_{B0} = A_{B1}$ 且 $\text{Env}_{B0} \approx \text{Env}_{B1}$)**：

| 基準線 ID | 系統拓撲結構 | 核心評測目的 |
| :--- | :--- | :--- |
| **B0 (裸應用層基準)** | `Attacker -> Application -> OS` | 建立未受管攻擊基準，實證攻擊語料具備真實破壞力 ($\Delta S_{B0} > 0$)。 |
| **B1 (DROS/PGM 啟用)** | `Attacker -> Application -> DROS/PGM -> OS` | 主要受測體，驗證二進位邊界之實體副作用消除效果 ($\Delta S_{B1} \equiv 0$)。 |
| **B2 (深度防禦整合)** | `Attacker -> App -> DROS + Enterprise Stack -> OS` | 驗證與既有 EDR / XDR / 提示詞防火牆之相容性與覆蓋率。 |
| **B3 (純二進位孤島)** | `Attacker -> Standalone PGM C-ABI -> OS` | 排除所有上層輔助，單測 C-ABI 二進位執行閘門之獨立隔離能力。 |

### 2.3 物理副作用與形式化安全不變量 (Physical Effect Formalization)

#### 物理副作用正式定義 (Physical Effect Definition)
為杜絕語義模糊，物理副作用指標 $I_{\text{physical}}(x)$ 嚴格定義為儀表化觀測集合 $\mathcal{S}_{\text{obs}}$ 上的狀態位移：

$$I_{\text{physical}}(x) = \begin{cases} 1, & \exists s \in \mathcal{S}_{\text{obs}}: \Delta(s) > 0 \\ 0, & \forall s \in \mathcal{S}_{\text{obs}}: \Delta(s) = 0 \end{cases}$$

$$\mathcal{S}_{\text{obs}} = \{ \text{Kernel Syscall}, \text{Filesystem Diff}, \text{Database WAL}, \text{Process Tree}, \text{Outbound Network}, \text{IPC State} \}$$

> **認識論界定：** 物理副作用之「0 位移」宣告僅限於明確定義之儀表化觀測集合 $\mathcal{S}_{\text{obs}}$，而非對任意未觀測之全域系統狀態進行絕對保證。

#### 幽靈系統呼叫正式定義 (Ghost Syscall Definition)
幽靈系統呼叫（Ghost Syscall）定義為：**授權判定已被拒絕 (DENY)，但仍越過執行邊界逃逸至操作系統內核之系統呼叫**：

$$G = \# \{ \text{syscall} \mid \text{Auth} = \text{DENY} \land \text{syscall\_observed} = 1 \}, \quad \text{安全目標: } G = 0$$

#### 術語一致性定義 (Terminology Consistency)
* **反例搜尋 (Counterexample Search)**：指稱在實例化狀態空間中主動搜尋可執行之違例狀態 ($C_A \land \neg C_E \implies I_{\text{physical}} > 0$) 的主動探索過程。
* **反例登記與提交 (Counterexample Submission)**：指稱外部研究者透過公開協定向社群登記庫提交已重現反例的驗證機制。

#### 核心形式化安全不變量

$$\boxed{C_A \centernot\implies C_E \quad (\text{授權非繼承性公理})}$$
$$\boxed{C_E(t_0) \centernot\implies C_E(t_1) \quad (\forall t_0 \neq t_1, \text{時間狀態隔離})}$$
$$\boxed{\bigcup_{i=1}^n C_{A_i} \centernot\implies C_E^{\text{unauth}} \quad (\text{能力組合安全性})}$$
$$\boxed{\forall x \in X_{\text{evaluated}}, \quad C_A(x) \land \neg C_E(x) \implies \neg \text{Exec}_{\text{unauthorized}}(x) \implies I_{\text{physical}}(x) = 0}$$
$$\boxed{S_{\text{after}} \equiv S_{\text{before}} \quad (\text{在 } \mathcal{S}_{\text{obs}} \text{ 觀測邊界內實體狀態零位移})}$$

---

## 3. DROS 四層架構與核心實作 (Architecture & Deep Modules Implementation)

### 3.1 L1: 語義情報偵測層 (Detect)
L1 部署於最前端，負責對自然語言輸入進行啟發式與輕量語義過濾。在 DROS 設計中，**L1 被明確定性為「機率性防禦」**。當 L1 遭遇高強度越獄或複雜混淆而失效時，威脅由 L2–L4 進行確定性阻截。

### 3.2 L2: 3-Tier PKI 身分與 DIT 動態授權層 (Attribute)
L2 建立基於密碼學的 3-Tier PKI 歸因模型（Enterprise CA $\rightarrow$ Task Issuer $\rightarrow$ Ephemeral Worker Agent），並生成動態意圖權能 Token（Dynamic Intent Token, DIT）。DIT 將 Agent 具體執行的 Tool Name、參數哈希、時間戳與授權位元遮罩進行 Ed25519 簽名綁定，杜絕身分偽造與參數竄改。

### 3.3 L3: 動態資訊流控制 (IFC) 與帶內資料遮蔽 (Constrain Data)
L3 在記憶體內實施動態污點追蹤（Taint Tracking）與帶內機密遮蔽。當機密資產（如專利配方、財務帳目、私鑰）流經 Agent 上下文時，L3 自動進行即時動態脫敏（替換為 `[REDACTED_BY_DROS_POLICY_GATE]`），降低大模型經由 Prompt 側信道外洩核心商業機密之風險。

### 3.4 L4: 二進位 C-ABI / FFI 授權執行閘門 (Enforce Execution)
L4 是受控二進位授權執行的關鍵組件，以 Rust 編寫並封裝為純 C-ABI 動態函式庫。
1. **$O(1)$ 常數時間策略查表**：位元遮罩比對耗時控制在亞微秒級。
2. **RCU 原子策略狀態切換 ($T_{\text{swap}} = 420\text{ ns}$)**：能力表指針透過 `AtomicPtr` 管理。策略撤銷時，分配新表並進行原子指針置換（Swap）。實測之 $T_{\text{swap}} = 420\text{ ns}$ 係指狀態指標切換之機制延遲，確保後續受管呼叫無法讀取過期策略。
3. **亞微秒 Fail-Closed 拒絕路徑 (<500 ns)**：一旦位元遮罩不匹配或缺少授權，受治理執行路徑立即走入 Fail-Closed 拒絕分支中斷呼叫，阻止未授權操作越過邊界抵達受管作業系統介面。

---

## 4. 漸進式對抗驗證體系 (Progressive Adversarial Validation Framework)

本文建立由淺入深的漸進式反例證偽體系：

```text
Level 1: 基礎基準校準 (Baseline Validation) ── 確立功能正確性與 B0 穿透 (ΔS_B0 > 0)
   ↓
Level 2: 自主反例搜尋 (Autonomous Adversarial Search) ── Strix 白盒自適應攻擊 (max I_physical)
   ↓
Level 3: 動態極限壓力 (Dynamic Stress & Chaos) ── 100-Agent 模擬網格、RCU 時間競態、故障注入
   ↓
Level 4: 測試元驗證 (Meta-Verification) ── 陰性對照 (Sabotaged PGM) 與 100 變形突變體
   ↓
Level 5: 神諭獨立性 (Oracle Independence) ── 4階段客觀事實鏈 (Intent → Auth → Exec → Effect)
   ↓
Level 6: 跨環境組態驗證 (Configuration Validation) ── 跨 x86_64, aarch64, glibc, musl, MSVC 組態
   ↓
Level 7: 開源反例證偽協議 (Open Falsification) ── 公開自足復現靶場與永久反例登記庫
```

### 4.1 對抗評測維度覆蓋與實測結果矩陣 (Adversarial Coverage vs. Results Matrix)

| 攻擊維度 (Dimension) | 測試變體與情境 (Evaluated Variants) | 觀測到的強制防禦與存證 | 違例反例數 |
| :--- | :--- | :--- | :--- |
| **身分 (Identity)** | 合法憑證 / 偽造身分 / 角色替換 | Ed25519 驗簽失敗，L2 阻絕偽造 Token | **0** |
| **權能 (Capability)** | 權限缺失 / 超額權限 / 跨角色組合 | L4 位元遮罩不匹配即刻觸發 Fail-Closed | **0** |
| **參數 (Parameter)** | 合法負載 / 參數逃逸竄改 / 重放注入 | SHA-256 參數哈希比對失敗，拒絕執行 | **0** |
| **時間 (Temporal)** | 期限內 / 過期 Token / RCU 即時撤銷 | 原子指針置換使過期 Token 立即失效 | **0** |
| **委派 (Delegation)** | 直接呼叫 / 多跳委派鏈 / 混淆代理人 | DIT 嚴格綁定 Task Issuer，拒絕鏈路越權 | **0** |
| **直譯器 (Interpreter)** | Shell 注入 (`bash`) / 動態直譯 (`eval`) | 逃逸呼叫缺乏有效 DIT，被 C-ABI 攔截 | **0** |
| **並發 (Concurrency)** | 序列呼叫 / 高並發湧浪 / 納秒時序競態 | 無鎖 RCU 實現並發隔離，0 競爭窗口 | **0** |
| **編碼 (Encoding)** | 標準 JSON / 語義混淆 / Metamorphic 變形 | 規範化位元遮罩比對免疫語義混淆 | **0** |
| **Agent 拓撲** | 單一 Agent / 100-Agent 模擬網格 / 階層鏈 | 跨網格委派均須獨立驗簽，0 權限繼承 | **0** |
| **故障與中斷 (Failure)**| 連線逾時 / 行程崩潰 / 過期狀態讀取 | 兩階段原子提交確保故障時 0 殘留狀態 | **0** |

### 4.2 驗證層級全景與對抗數據矩陣 (Multi-Layer Adversarial Evaluation Results)

| 驗證層級 | 測試方法與受測條件 | 攻擊負載與規模 | 觀測到的強制存證 | 反例數 | 判定狀態 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1 基準校準** | B0/B1 A/B 移除對照 | 50 次未受管攻擊 | 驗證 B0 穿透 ($\Delta S_{B0} > 0$), B1 阻絕 ($\Delta S_{B1} \equiv 0$) | 0 | **PASS (RQ1)** |
| **L2 自主搜尋** | Strix 白盒適應性攻擊 | 2,410 次執行嘗試 (21.4M Tokens) | 到達網關之未授權探針於受測語料中全數被拒絕 | 0 | **PASS (RQ1)** |
| **L3 極限壓力** | 100-Agent 模擬網格 + RCU 競態 | 400 條代理鏈 + 250 次突發 | RCU 420 ns 指標切換，未觀察到重放執行 | 0 | **PASS (RQ2)** |
| **L4 測試元驗證**| 陰性對照 + 100 突變體 | 5 故意缺陷 + 100 突變體 | 5/5 缺陷捕獲；100% 突變體擊殺 (實例化語料) | 0 | **PASS (RQ3)** |
| **L5 神諭驗證** | 9 大神諭壓力向量 | 450 次神諭突變探針 | $\mathcal{S}_{\text{obs}}$ 邊界內 $G=0$ 幽靈 Syscall 洩漏；0 狀態分歧 | 0 | **PASS (RQ4)** |
| **L6 組態驗證** | 跨 OS / 架構組態驗證 | 7,500 次自動化探針 | 跨 x86_64, ARM64, Windows 組態驗證策略語義一致性 | 0 | **PASS** |

### 4.3 測試元驗證與突變得分 (Meta-Verification & Mutation Testing - RQ3)
為驗證評測框架具備捕獲真實漏洞之靈敏度，本研究建立了 5 組故意植入缺陷之陰性對照二進位（Sabotaged PGM），並在策略引擎中植入 100 個實例化突變體（涵蓋 M1 權能位元過寬、M2 身分替換、M3 過期繞過、M4 參數哈希遺漏、M5 過期策略讀取、M6 授權檢查移除、M7 Fail-Open 分支、M8 審計抑制等 8 大類別）：

$$\text{Mutation Score} = \frac{\text{Killed Mutants}}{\text{Total Instantiated Mutants}} = \frac{100}{100} = \mathbf{1.0\ (100\%\ \text{mutation-killing rate over the instantiated mutation corpus})}$$

陰性對照組之 5 大故意漏洞全數被評測基板捕獲 ($5/5$)，實證評測框架非「橡皮圖章」。

---

## 5. 多點獨立客觀事實神諭與實證結果 (Ground-Truth Oracle & Results)

### 5.1 四階段客觀事實鏈路 (The Four-Stage Independent Ground-Truth Pipeline - RQ4)
為落實 **「任何單一層級皆不得成為其自身的唯一證人 (No Single Component May Act As Its Own Sole Witness)」**，DROS-VEP 建立解耦事實鏈路 ($O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$)：

$$\boxed{\text{意圖 } (O_I) \longrightarrow \text{授權 } (O_A) \longrightarrow \text{執行 } (O_E) \longrightarrow \text{物理副作用 } (O_P)}$$

1. **意圖神諭 ($O_I$)**：記錄攻擊者提交之原始 Tool Invocation Payload。
2. **授權神諭 ($O_A$)**：PGM C-ABI 閘門獨立評估位元遮罩並記錄授權決策 (DENY)。
3. **執行神諭 ($O_E$)**：獨立內核行程監控確認在受測邊界內 **$G = 0$ 幽靈 Syscall (Ghost Syscall) 洩漏**。
4. **物理副作用神諭 ($O_P$)**：帶外 DB WAL、檔案系統與行程樹差分確認在 $\mathcal{S}_{\text{obs}}$ 內 $\boxed{S_{\text{after}} \equiv S_{\text{before}}}$。

### 5.2 物理副作用抑制率分析 ($\Delta I_{\text{physical}}$ - RQ1)

$$\Delta I_{\text{physical}} = I_{\text{physical}}(B0) - I_{\text{physical}}(B1) = 1.0 - 0.0 = \mathbf{100\%\ \text{observed physical-effect suppression over the evaluated attack corpus}}$$

實測表明：在缺乏 DROS/PGM 二進位閘門之環境下，應用層受陷將轉化為實體後端狀態污染 ($\Delta S_{B0} > 0$)；而在啟用 DROS/PGM 閘門後，未授權物理副作用在受測範圍內被抑制 ($\Delta S_{B1} \equiv 0$)。

### 5.3 效能與延遲開銷評測 (Performance Overhead)
在 AMD Ryzen 9 7950X / Ubuntu 24.04 實機壓測環境下：
* **端到端決策延遲 (P50)**：$26.1\ \mu\text{s}$（包含 HTTP 解析、DIT 驗簽與位元遮罩檢驗）。
* **端到端決策延遲 (P99)**：$31.4\ \mu\text{s}$。
* **RCU 狀態指標切換延遲 ($T_{\text{swap}}$)**：$420\text{ ns}$（純記憶體屏障與指標置換，與網路延遲明確區隔）。
* **L4 Fail-Closed 拒絕路徑延遲**：$<500\text{ ns}$。

---

## 6. 公開反例證偽協議與討論 (Open Falsification & Discussion)

### 6.1 局限性與認識論邊界 (Limitations & Gap in Scope)
1. **本體語義依賴**：DROS 執行邊界依賴於 L2 DIT 對業務語義的位元遮罩對齊；若開發者在策略編譯期將高危險 Tool 賦予了所有 Role，則屬於策略配置錯誤而非基板執行逃逸。
2. **觀察邊界限制**：本文之「0 反例」結論嚴格定錨於當前實驗所具體實例化的 60,000+ 探針、100-Agent 模擬網格、競態與混沌狀態空間中，不構成對所有未知攻擊空間的先驗數學證明。
3. **組態可移植性 vs. 原生內核執行邊界 (Gap in Scope)**：L6 驗證策略與組態語義在異質環境下的可移植性（Portability of Policy Semantics），明確不代表在所有目標平台均完成了原生內核層之硬體 MMU 與驅動執行驗證。

### 6.2 永久反例登記庫與開源復現協議 (Public Counterexample Protocol)
本專案已在 GitHub 開源全套可重現性靶場，並設立永久反例登記庫 (`reproducibility/counterexamples/`)。我們公開邀請全球學術界與安全社群依據以下標準格式提交反例：

```text
公開反例提交結構規範：
├── CE-ID (例如 CE-001)
├── 宿主環境與編譯器參數 (OS, Arch, Compiler Flags)
├── 隨機種子 / 重現腳本 (Reproduction Script)
├── 觀測到的狀態差分 (ΔS > 0 具體證據)
└── 物理副作用存證檔案 (WAL / FS Diff Artifact)
```

---

## 7. 結論與形式化判定宣告 (Conclusion & Declarations)

本文提出並對抗性驗證了 **DROS 四層執行期作業基板與確定性執行強制機制**。透過將 AI Agent 治理邊界下沉至受控二進位 C-ABI / FFI 授權層，DROS 橋接了「語義-內核悖論」。

經由導入 Strix 自主黑客平台、陰性對照組、變形測試與多點獨立神諭之漸進式對抗驗證，實證結果表明：在涵蓋攻擊策略、時間競態、高並發、變形突變與系統故障的實驗實例化狀態空間中，未觀察到任何違反既定安全不變量的可執行反例。

$$\boxed{\text{Final Epistemic Verdict: } \forall x \in X_{\text{evaluated}}, \quad C_A(x) \land \neg C_E(x) \implies I_{\text{physical}}(x) = 0 \quad (\text{PASS})}$$

### 致謝與 AI 協作聲明 (Acknowledgment & AI Collaboration Disclosure)
依據 IEEE / ACM 2023+ 關於生成式人工智慧與學術誠信之指引規範，作者在此明確揭露：
1. **研究原創性與智慧財產權**：本文所述之 DROS 四層架構體系（L1--L4）、動態意圖權杖（DIT）、C-ABI 二進位能力邊界、形式化不變量定義、六階對抗證偽方法學及相關專利權利主張（U.S. PPA No. 64/111,973），均由作者陳濬程獨立構想、設計、推導並驗證。
2. **AI 工具輔助範圍**：大型語言模型（LLM Agent / Gemini）僅作為輔助工具，用於學術英文文法校對、文字組織結構潤飾、LaTeX 語法除錯及開源測試腳本之格式化輔助。AI 模型未參與任何核心專利發明概念之生成或安全性質之實質理論構建。作者對全文之技術正確性、數據真實性與認識論結論承擔完全之學術與法律責任。

---

## 參考文獻 (References)

1. **J. Chen**, *"DROS: A Four-Layer Deterministic Runtime Operation System Bridging the Agent-to-Execution Attribution Gap in Autonomous AI Workloads,"* Zenodo Technical Report, DOI: `10.5281/zenodo.22092008`, 2026.
2. **J. Chen**, *"DROS Trilogy Reading Guide: An Agent Runtime Operation Substrate (Academic Version 3.0),"* Zenodo Technical Guide, DOI: `10.5281/zenodo.22114036`, 2026.
3. **J. Chen**, *"DROS-PGM: Physical Guard Module with Sub-Microsecond C-ABI Binary Execution Boundary,"* Zenodo Research Report, DOI: `10.5281/zenodo.21903687`, 2026.
4. **J. Chen**, *"DROS 6P Architectural Specification: Unified Trust, PKI, and Execution Governance,"* Zenodo Specification, DOI: `10.5281/zenodo.21833970`, 2026.
5. **Strix Security Team**, *"Strix: Autonomous Multi-Agent AI Penetration Testing Framework (v1.5.3),"* 2026. [Online]. Available: `https://strix.ai`
6. **Microsoft**, *"Microsoft Agent Framework Documentation: Tool Calling and Execution Governance,"* Microsoft Learn, 2025.
7. **NVIDIA**, *"NeMo Guardrails: Programmable Guardrails for LLM Applications,"* NVIDIA Developer Documentation, 2024.
8. **European Parliament**, *"Artificial Intelligence Act (Regulation EU 2024/1689), Article 50: Transparency and Traceability of AI Systems,"* Official Journal of the European Union, 2024.
9. **MITRE Corporation**, *"ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems,"* MITRE ATLAS Knowledge Base, 2026.
10. **OWASP Foundation**, *"OWASP Top 10 for Large Language Model Applications,"* OWASP Standard, 2025.
11. **P. E. McKenney**, *"Is Parallel Programming Hard, And, If So, What Can You Do About It? (Read-Copy Update Architecture),"* Linux Technology Center, IBM Operating Systems Review, 2024.
12. **W. Enck et al.**, *"TaintDroid: An Information-Flow Tracking System for Real-Time Privacy Monitoring on Smartphones,"* ACM Transactions on Computer Systems (TOCS), vol. 32, no. 2, pp. 1–32, 2014.
13. **METR (Model Evaluation and Threat Research)**, *"Evaluating Autonomous Capabilities in Frontier AI Models,"* METR Technical Research Standard, 2025.
14. **USENIX Security Symposium**, *"Artifact Evaluation Guidelines and Criteria,"* USENIX Association, 2024.
15. **IEEE S&P Editorial Board**, *"IEEE Symposium on Security and Privacy: Call for Papers and Submission Guidelines,"* IEEE Computer Society, 2026.
