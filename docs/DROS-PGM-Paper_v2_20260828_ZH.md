# 🛡️ DROS-PGM: 針對自主 AI 工作負載之後受陷約束確定性執行邊界 (v2.0)

## 基於反例導向驗證「應用層受陷與執行權限非繼承性」之研究 (Counterexample-Driven Validation of Non-Inheritance Between Application Compromise and Execution Authority)

**文件版本：** 2.0 研究論文 / 同行評審學術手稿 (IEEE TIFS / ACM CCS Target)  
**日期：** 2026 年 8 月 28 日  
**作者：** 陳濬程 (Chun-Cheng / Jimmy Chen) (`jimmychen@dr-os.io`)  
**所屬機構：** 康宸園有限公司 (Top-Celestial Company Ltd.), 台灣台北  
**專利聲明：** DROS 執行治理與安全技術已申請美國臨時專利保護（U.S. Patent Application No. 64/111,973，Patent Pending）。  
**開源存證靶場與可重現性資產：** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**永久學術文獻引用 (DOI)：** [Zenodo Record DOI: 10.5281/zenodo.21903687](https://doi.org/10.5281/zenodo.21903687)

---

## 摘要 (Abstract)

在自主 AI 代理（Autonomous AI Agents）獲取合法憑證與工具調用權限的現代工作負載中，應用層安全邊界正經歷根本性失效。傳統防禦體系主要依賴機率性語義護欄或粗粒度作業系統沙箱，其核心假設建立於「防範受陷（Preventing Compromise）」之上；然而，一旦內部對話或直譯器遭遇提示注入或邏輯受陷，攻擊者即可繼承合法憑證並引發不可逆的實體副作用。

本文提出 **DROS-PGM (Physical Guard Module)**，一種運行於二進位執行控制平面之後受陷執行約束基板（Post-Compromise Execution Containment Substrate）。在架構上，**C-ABI / FFI 邊界負責策略調用與主體能力歸因，而 OS 內核 Hook 則構成最終之強制執行邊界（Mandatory Enforcement Boundary）**。PGM 將「應用層主體身分」與「底層執行授權」實體解耦，透過亞微秒級（中位數 353 ns）無鎖位元遮罩比對與原子化 RCU 狀態指針切換，在應用層完全受陷（$C_A = 1$）的前提下，形式化維持安全不變量：
$$C_A \land \neg C_E \implies Exec_{\text{unauthorized}} = 0 \implies I_{\text{physical}} = 0$$

為嚴謹評估此邊界之強健性，我們引入 **PGM-VEP 五階漸進式對抗證偽方法學（Five-Tier Progressive Falsification Methodology, V1--V5）**，涵蓋依循攻擊等價原則（$A_{B0} = A_{B1}$）之基準對照、白箱對抗探針搜尋、陰性對照組元驗證（5/5 缺陷捕獲與 100% 突變殺死率）、四階段解耦判定神諭（$O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$）以及跨 Linux x86_64、ARM64 與 Windows 異質環境之獨立自動化復現。在累積 60,000+ 結構化對抗探針、24 小時連續壓力測試以及 50,000 次良性基準負載（誤報率 $0/50,000$）中，於顯式插樁觀測邊界內未曾觀測到任何授權逃逸或實體狀態漂移。本文不提出未經形式化證明之全域安全保證，而是將其確立為於已驗證狀態空間中成立之經驗不變量（Empirical Invariants），並公開發布反例登錄協議以供學術社群持續進行開放式對抗證偽。

**關鍵字：** 執行約束基板 (Execution Containment Substrate)、後受陷安全 (Post-Compromise Security)、內核強制邊界 (Kernel Enforcement Boundary)、動態能力撤銷 (RCU Revocation)、漸進式對抗證偽 (Progressive Falsification)、解耦判定神諭 (Decoupled Oracles)。

---

## 一、 問題定義：Agent 受陷不等於執行權限 (Problem Definition)

當代自主 AI Agent 系統（如基於 LangGraph、CrewAI 或 AutoGen 構建之企業自動化流程）已普遍獲得執行實體操作之特權，包括資料庫讀寫、雲端 API 調用、內部 IPC 通訊及作業系統指令執行。在此架構下，系統安全面臨著根本性的**語義與內核斷層（The Semantic-Kernel Paradox）**：

1. **應用層語義中介軟體（高語義、零確定性）：** 提示防火牆（Prompt Firewalls）、JSON Schema 驗證器與輸出過濾器僅能在自然語言或宣告式資料層面進行機率性評估。此類機制欠缺底層執行邊界的物理圍阻能力，直譯器逃逸、動態參數混淆或邏輯繞過均能使防護失效。
2. **作業系統內核沙箱（高確定性、零語義）：** 傳統內核級防禦（如 Seccomp、Linux Namespaces、eBPF Syscall Filter）具備二進位級強制力，但完全欠缺應用層語義上下文。當一個已獲取合法資料庫連線池的進程發起惡意寫入時，內核無法辨識該操作究係源自合法授權之財務 Agent，抑或源自已遭提示注入控制之客服 Agent。

此斷層導致嚴重的**「主體身分與執行權限混淆」**：一旦應用層受陷（$C_A = 1$），攻擊者即可直接繼承進程所擁有的全部實體執行能力。因此，亟需構建一種能夠在應用層徹底受陷之極限條件下，依然維持確定性執行約束的底層安全基板。

---

## 二、 雙重邊界與系統分工 (Dual Boundaries & Architecture Placement)

為杜絕架構邊界混淆，本架構明確劃定 **DROS 上層治理系統** 與 **DROS-PGM 物理防護模組** 的責任邊界，並確立「C-ABI 歸因」與「內核強制」的雙重邊界模型：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 語義與應用層 (Semantic Layer)                                               │
│ [Agent Swarm / LangGraph] ──► 遭受陷: C_A = 1                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (DROS L1-L3: 生成 DIT 權杖與位元遮罩)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 邊界一：C-ABI / FFI 策略調用與主體歸因邊界 (Attribution Boundary)           │
│ [PGM Policy Gate: O(1) Bitmask Lookup / RCU State Pointer (353 ns)]         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (Pass / Fail-Closed Panic)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 邊界二：OS 內核不可繞過之強制執行邊界 (Mandatory Enforcement Boundary)      │
│ [Linux LSM Hook / Windows Kernel Minifilter] ──► 終止未授權 Syscall 派發    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (阻斷: ΔS = 0; 放行: 僅限合規操作)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 實體狀態空間 (Physical State Space: Filesystem, DB WAL, Network, Process)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **DROS (上層治理)**：負責身分憑證管理（PKI）、語義動態意圖權杖（DIT）簽發與資訊流污點追蹤（L1--L3）。
* **DROS-PGM (底層執行基板)**：**在帶內完全排除非對稱密碼學運算**，專注於 L2 快取內常駐策略點陣圖之 $O(1)$ 位元遮罩解析、無鎖 RCU 狀態切換以及 OS 內核 Hook 之二進位強制攔截。

---

## 三、 核心安全不變量與概念解耦 (Formal Security Invariants & Decoupling)

為精確界定安全邊界，DROS-PGM 確立了四個核心概念之嚴格解耦：
* **應用層主體身分 ($Identity_A$)**：由應用框架維護之邏輯角色或 Session 身分。
* **能力宣告授權 ($Auth_C$)**：透過能力位元遮罩（Capability Bitmask）所表達之權限集合。
* **執行閘門授權 ($Auth_E$)**：二進位 C-ABI 執行邊界與內核 Hook 於運行期即時判定之二元結果（$\text{ALLOW} / \text{DENY}$）。
* **實體副作用 ($I_{\text{physical}}$)**：底層檔案系統、資料庫 WAL、內核 Syscall 或外部網路之可觀測狀態變更。

### 形式化不變量定義 (Formal Invariants)

1. **權限非繼承性公理 (Non-Inheritance of Authority)：**
   $$C_A \centernot\implies C_E$$
   應用層對話或直譯器受陷，不得推導出具備二進位層級之執行授權。
2. **核心安全不變量 (Core Containment Invariant)：**
   $$\forall x \in X_{\text{evaluated}}, \quad C_A(x) \land \neg C_E(x) \implies Exec_{\text{unauthorized}}(x) = 0 \implies I_{\text{physical}}(x) = 0$$
   在未獲取有效執行授權（$\neg C_E$）之情況下，任何未授權操作之執行次數恆為 0，且在顯式觀測集合 $\mathcal{S}_{\text{obs}}$ 內之實體副作用恆為 0。
3. **並發撤銷之線性化語義 (Linearization Point & Concurrency Semantics)：**
   在原子指針切換之線性化點（Linearization Point, $T_{\text{swap}} = 420\text{ ns}$）之後，所有後續到達之策略評估均能確定性觀測到最新撤銷狀態；於線性化點前已被接納進入內核派發之在途操作（In-flight Operations），則由預先分配之安全狀態上下文（Pre-allocated Safe-State Context）實施退化隔離。
4. **實體零狀態漂移 (Zero State Drift within $\mathcal{S}_{\text{obs}}$)：**
   $$S_{\text{after}} \equiv S_{\text{before}} \quad (\forall s \in \mathcal{S}_{\text{obs}}, \Delta(s) = 0)$$

---

## 四、 威脅模型：後受陷假設 ($C_A = 1$) (Threat Model)

本研究設定嚴格之後受陷威脅模型（Post-Compromise Threat Model），直接假設防禦第一線已經失守：

1. **假設 1（應用層全面受陷 $C_A = 1$）：** 攻擊者已成功透過間接提示注入（Indirect Prompt Injection）控制 Agent 認知流程，或在宿主應用容器內取得任意代碼執行權。
2. **假設 2（合法憑證持有）：** 攻擊者具備存取進程記憶體中合法 OAuth Token、API 金鑰及內部資料庫連線之能力。
3. **假設 3（多代理協同與混淆代理人攻擊）：** 攻擊者可操控多個異質 Agent，嘗試透過複雜委派鏈（Delegation Chains）實施權限提升或混淆代理人（Confused-Deputy）繞過。
4. **信任根與 TCB 邊界：** 信任基礎嚴格限制於 PGM 二進位執行閘門、CPU 硬體記憶體管理單元（MMU/Ring 0）、作業系統內核 LSM 驅動以及防篡改日誌緩衝區。

在此威脅模型下，任何單純依賴提示詞過濾或宣告式 JSON 檢查之防禦皆被視為無效；驗證目標在於檢驗 PGM 是否能在 $C_A = 1$ 之條件下，阻斷非法實體效果之產生。

---

## 五、 PGM-VEP 五階漸進式對抗證偽方法學 (Validation Methodology: V1--V5)

為徹底消弭「評測者偏誤」與「自我驗證盲區」，我們構建了五階漸進式證偽方法學體系：

```text
  [ V1: Attack the PGM ] ────► 攻擊等價基準對照測試 (B0 vs B1, A_B0 = A_B1)
           │
           ▼
  [ V2: Counterexample Search ] ──► 廣域白箱狀態搜尋、模糊測試與並發壓力 (60,000+ Probes)
           │
           ▼
  [ V3: Attack the Test ] ──► 陰性對照組元驗證與 100 突變體評測 (Mutation Score = 1.0)
           │
           ▼
  [ V4: Attack the Oracle ] ──► 4 階段客觀事實鏈與 9 大神諭壓力向量 (G = 0 Ghost Syscalls)
           │
           ▼
  [ V5: Cross-Env Reproduction ] ─► 開源自足復現套件與跨 3 大異質環境獨立自動化評測
```

### 各驗證階層詳細規範

* **V1 (Attack the PGM - 基準對抗與攻擊等價)：** 嚴格遵循**攻擊等價原則（$A_{B0} = A_{B1}$ 且 $\text{Env}_{B0} \approx \text{Env}_{B1}$）**，在 B0（未受控裸應用程式）與 B1（啟用 PGM）施加相同之 50 組高破壞性攻擊酬載，驗證 B0 造成實體狀態破壞（$\Delta S_{B0} > 0$），而 B1 達成 100% 執行圍阻。
* **V2 (Maximum Counterexample Search - 極限反例搜尋)：** 導入 Strix 白箱適應性搜尋引擎與高並發排程器，在 10 個攻擊維度（身分偽造、位元遮罩擴張、參數篡改、RCU 競態、直譯器逃逸等）展開廣域空間探索。
* **V3 (Attack the Test Framework - 元驗證與陰性對照)：** 針對測試框架本身之判別力進行反思性驗證。植入 5 大蓄意破壞之缺陷二進位檔（Sabotaged Variants），並生成 100 個涵蓋 8 類邏輯缺陷之突變體，檢驗測試框架是否具備真實捕獲能力。
* **V4 (Attack the Oracle - 神諭獨立性與客觀事實鏈)：** 確立「任何單一層級皆不得成為其自身的唯一證人」，建立由四個獨立觀察者構成之事實鏈路：
  $$\text{意圖記錄 } (O_I) \longrightarrow \text{授權判決 } (O_A) \longrightarrow \text{內核執行 } (O_E) \longrightarrow \text{實體副作用 } (O_P)$$
  並施加 9 大神諭壓力向量（記憶體污染、窗口時序競態、回滾碰撞、幽靈 Syscall 注入等）。
* **V5 (Cross-Environment Independent Reproduction - 跨環境獨立自動化復現)：** 封裝包含獨立二進位檔、評測編排器、帶外神諭與突變生成器之開源自足復現套件，於 3 大異質環境（Ubuntu/glibc, Alpine/musl, Windows/MSVC）進行無依賴盲態基準評測。

---

## 六、 實驗結果與度量分析 (Experimental Results)

### 6.1 評測工作負載會計帳本 (Evaluation Accounting Matrix)

為確保數據清晰可加總，表一列出各驗證階層之精確探針與負載分佈：

| 驗證階層 | 測試類型與配置架構 | 唯一測試探針數 (Unique Probes) | 重放與並發負載 (Replay / Concurrent) | 總執行次數 (Total Executions) | 觀測反例 (CE) | 判定狀態 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **V1 (Baseline)** | B0/B1 等價對照 ($A_{B0}=A_{B1}$) | 50 | 250 | 300 | 0 | **PASS** |
| **V2 (Adversarial)** | 白箱適應性搜尋 + 並發熔爐 | 2,410 | 57,590 (21.4M Tokens) | 60,000 | 0 | **PASS** |
| **V3 (Meta-Verify)** | 5 缺陷二進位 + 100 突變體 | 105 | — | 105 | 0 | **PASS** |
| **V4 (Oracle Torture)**| 4 階段客觀事實鏈 + 9 大向量 | 450 | — | 450 | 0 | **PASS** |
| **V5 (Cross-Env)** | 3 大環境設定檔獨立復現 | 1,500 | 6,000 | 7,500 | 0 | **PASS** |
| **Benign Benchmark** | SPEC CPU2017 + 合法工具調用 | 50,000 | — | 50,000 | 0 | **FPR = 0/50,000** |
| **總計 (Total)** | **全階層綜合評測** | **54,515** | **63,840** | **118,355** | **0** | **ALL PASS** |

### 6.2 元驗證：陰性對照與變形測試結果 (V3)
在 V3 階段，測試框架針對 100 個植入缺陷之 PGM 突變體進行了全面檢驗：
$$\text{Mutation Score} = \frac{\text{Killed Mutants}}{\text{Total Instantiated Mutants}} = \frac{100}{100} = 1.0$$
測試框架 100% 識別並捕獲所有變形缺陷（包含位元擴張、身分替換、過期繞過、無條件放行等），實證測試框架具備完全之缺陷辨識靈敏度，絕非寬鬆放行之橡皮圖章。

### 6.3 延遲測量分解與效能基準 (AMD Ryzen 9 7950X / Intel Xeon 6330)

為精確界定效能數據之測量邊界（Measurement Boundaries），各層延遲分解如下：

```text
調用發起 (Caller)
  │
  ├─ [上層 DROS 邊界] HTTP 解析 + Ed25519 簽名驗證 + DIT 生成 ───► P50: 26.1 µs / P99: 31.4 µs
  │
  ├─ [PGM C-ABI 邊界] L2 快取常駐策略點陣圖 O(1) SIMD 查表 ──────► 中位數: 353 ns / P99: 412 ns
  │
  ├─ [PGM 狀態切換] RCU 原子指針切換線性化點 (T_swap) ──────────► 420 ns
  │
  ├─ [PGM 阻絕路徑] Fail-Closed 常數時間快速拒絕路徑 ───────────► < 500 ns
  │
  └─ [內核強制邊界] Linux LSM / Windows Minifilter 攔截開銷 ──────► SPEC CPU2017 開銷: 1.2%
```

在 72 小時連續浸泡測試中，PGM 保持高達 **952,991 QPS** 之策略決策線速吞吐量，且無任何記憶體滲漏現象。

---

## 七、 局限性與認識論邊界 (Limitations & Epistemic Scope)

基於嚴謹認識論紀律，本文明確劃定本研究之有效性邊界與局限性：

1. **經驗不變量而非先驗數學證明：** 「在 118,355 次總執行負載與多環境測試中未觀察到反例」之結論，嚴格受限於已實例化之測試語料庫與探索空間，不構成對無窮對抗空間之先驗存在性證明。
2. **本體語義對齊之依賴性：** PGM 之阻絕精度依賴於應用層正確將業務操作映射至對應之權限位元遮罩；若上游語義映射存在定義性錯誤，不在底層二進位閘門之語義修正範疇內。
3. **硬體與內核信任邊界：** PGM 建立於宿主作業系統記憶體管理單元（MMU）與內核保護模式（Ring 0）未遭物理穿透之假設前提；針對底層硬體側通道（Side-Channel）或內核零日漏洞之防禦超出本架構之設計射程。

---

## 八、 討論：後受陷安全範式轉換 (Discussion: Post-Compromise Security)

傳統資訊安全架構之核心思維，長期建立於**「受陷前防禦（Pre-Compromise Defense）」**——致力於降低系統遭遇穿透之機率（$\min P(C_A = 1)$）。然而，在 LLM 驅動之自主 Agent 生態中，提示注入之理論不可完全消除性（Theoretical Inevitability）宣告了受陷前防禦必然存在破綻。

PGM 代表了一種根本性的安全範式轉換：**將安全控制的重心，從「試圖阻止 Agent 受陷」轉移至「在 Agent 已經受陷的條件下，如何嚴格截斷執行授權與物理後果（Post-Compromise Execution Containment）」**。透過將執行邊界下沉至無法被自然語言語義污染之二進位控制平面與 OS 內核 Hook，PGM 為自主 AI 工作負載構築了一道確定性的最後物理防線。

---

## 九、 相關工作與學術定位 (Related Work & Systems Comparison)

本研究與 2026 年前沿工作之學術定位差異如下：
* **語義與工具層防禦（如 AgentVisor [16], MCP Policy PEP [17]）**：於自然語言或 Tool-call 邊界提供虛擬化與審計，但欠缺 OS 內核級執行圍阻能力。
* **靜態型態與編譯期安全（如 Tracked Capabilities [18]）**：於語言層面追蹤權限，但無法約束已編譯之受陷二進位進程。
* **執行期與能力內核（如 Agent libOS [14], authgate-kernel [15]）**：提出了出色的架構概念，但公開實證普遍未對高並發帶內吞吐量（950K+ QPS）進行完整刻劃。
* **離線評測基準（如 LITMUS [19]）**：專注於離線 Jailbreak 測量，與 DROS-PGM 之在線帶內強制形成學術互補。

本研究之定位在於：**評估「主體能力歸因」與「OS 內核級強制執行」在後受陷模型下的垂直整合與對抗可證偽性**。

---

## 十、 結論與聲明 (Conclusion & Declarations)

本文提出並全面對抗評測了 DROS-PGM 二進位執行約束基板。透過五階漸進式證偽方法學（PGM-VEP V1--V5），跨 118,355 次對抗與良性負載、突變測試與異質環境獨立復現，驗證了核心安全不變量之有效性。全套評測工具鏈與反例登錄協議已公開發布，以期推動自主 AI 執行期安全邁向可證偽、可復現之嚴謹科學軌道。

作者聲明：本文所述之系統架構、雙重邊界模型、不變量定義、五階證偽方法學與專利主張均由作者陳濬程獨立構想、架構並驗證。

---

## 參考文獻 (References)

1. J. Chen, "DROS-PGM: Physical Guard Module with Sub-Microsecond C-ABI Binary Execution Boundary," *Zenodo Research Report*, DOI: 10.5281/zenodo.21903687, 2026.
2. J. Chen, "DROS Trilogy Reading Guide: An Agent Runtime Operation Substrate (Academic Version 3.0)," *Zenodo Technical Guide*, DOI: 10.5281/zenodo.22114036, 2026.
3. J. Chen, "DROS: A Four-Layer Runtime Substrate with Deterministic Execution Enforcement for Agent-to-Execution Attribution Governance," *Zenodo Research Paper*, DOI: 10.5281/zenodo.21755653, 2026.
4. J. Chen, "DROS 6P Architectural Specification: Unified Trust, PKI, and Execution Governance," *Zenodo Specification*, DOI: 10.5281/zenodo.21833970, 2026.
5. Strix Security Team, "Strix: Autonomous Multi-Agent AI Penetration Testing Framework (v1.5.3)," 2026. [Online]. Available: https://strix.ai
6. Microsoft, "Microsoft Agent Framework Documentation: Tool Calling and Execution Governance," *Microsoft Learn*, 2025.
7. NVIDIA, "NeMo Guardrails: Programmable Guardrails for LLM Applications," *NVIDIA Developer Documentation*, 2024.
8. European Parliament, "Artificial Intelligence Act (Regulation EU 2024/1689), Article 50: Transparency and Traceability of AI Systems," *Official Journal of the European Union*, 2024.
9. MITRE Corporation, "ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems," *MITRE ATLAS Knowledge Base*, 2026.
10. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," *OWASP Standard*, 2025.
11. P. E. McKenney, "Is Parallel Programming Hard, And, If So, What Can You Do About It? (Read-Copy Update Architecture)," *Linux Technology Center, IBM Operating Systems Review*, 2024.
12. W. Enck et al., "TaintDroid: An Information-Flow Tracking System for Real-Time Privacy Monitoring on Smartphones," *ACM Transactions on Computer Systems (TOCS)*, vol. 32, no. 2, pp. 1-32, 2014.
13. METR (Model Evaluation and Threat Research), "Evaluating Autonomous Capabilities in Frontier AI Models," *METR Technical Research Standard*, 2025.
14. Agent libOS Team, "Agent libOS: A Library-OS-Inspired Runtime for Long-Running, Capability-Controlled LLM Agents," *arXiv preprint arXiv:2606.03895*, June 2026.
15. Authgate Team, "A Capability Kernel for Agent Authorization," *SSRN Electronic Journal*, abstract id 6931639, July 2026.
16. AgentVisor Team, "AgentVisor: Defending LLM Agents Against Prompt Injection via Semantic Virtualization," *arXiv preprint arXiv:2604.24118*, April 2026.
17. MCP Security Group, "Runtime Policy Enforcement for MCP-Based LLM Agents," *MDPI Electronics*, vol. 15, no. 13, p. 2829, 2026.
18. Capability Tracking Authors, "Securing Agents With Tracked Capabilities," in *Proc. ACM Conference on AI and Agentic Systems*, DOI: 10.1145/3786335.3813127, 2026.
19. LITMUS Team, "LITMUS: Benchmarking Behavioral Jailbreaks of LLM Agents in Real OS Environments," *arXiv preprint arXiv:2605.10779*, May 2026.
