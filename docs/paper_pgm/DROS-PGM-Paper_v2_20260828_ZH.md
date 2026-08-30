# 🛡️ DROS-PGM: 針對自主 AI 工作負載之後受陷約束確定性執行邊界 (v2.0)

## 基於反例導向驗證「應用層受陷與執行權限非繼承性」之研究 (Counterexample-Driven Validation of Non-Inheritance Between Application Compromise and Execution Authority)

**文件版本：** 2.0 投稿候選稿 / 同行評審學術手稿 (IEEE TIFS / ACM CCS Target)  
**日期：** 2026 年 8 月 28 日  
**作者：** 陳濬程 (Chun-Cheng / Jimmy Chen) (`jimmychen@dr-os.io`)  
**所屬機構：** 康宸園有限公司 (Top-Celestial Company Ltd.), 台灣台北  
**專利聲明：** DROS 執行治理與安全技術已申請美國臨時專利保護（U.S. Patent Application No. 64/111,973，Patent Pending）。  
**開源存證靶場與可重現性資產：** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**永久學術文獻引用 (DOI)：** [Zenodo Record DOI: 10.5281/zenodo.21903687](https://doi.org/10.5281/zenodo.21903687)

---

## 摘要 (Abstract)

在自主 AI 代理（Autonomous AI Agents）獲取合法憑證與工具調用權限的現代工作負載中，應用層安全邊界正面臨根本性失效。傳統防禦體系主要依賴機率性語義護欄或粗粒度作業系統沙箱，其核心假設建立於「防範受陷（Preventing Compromise）」之上；然而，一旦內部對話或直譯器遭遇提示注入或邏輯受陷，攻擊者即可繼承合法憑證並引發不可逆的實體副作用。

本文提出 **DROS-PGM (Physical Guard Module)**，一種運行於二進位執行控制平面之後受陷執行約束基板（Post-Compromise Execution Containment Substrate）。在架構上，**C-ABI / FFI 邊界負責策略調用與主體能力歸因，而 OS 內核 Hook 則在顯式插樁之受管操作類別空間 $X_{\text{covered}}$ 上執行強制授權檢查**。PGM 將「應用層主體身分」與「底層執行授權」實體解耦，透過亞微秒級（中位數 353 ns）無鎖策略評估與原子化 RCU 狀態指針切換，形式化維持安全不變量：
$$\forall x \in X_{\text{covered}}, \quad Auth_E(x) = \text{DENY} \implies Exec_{\text{unauthorized}}(x) = 0 \quad \land \quad \forall s \in \mathcal{S}_{\text{obs}}, \; \Delta s = 0$$

為嚴謹評估此邊界之強健性，我們引入 **PGM-VEP 五階漸進式對抗證偽方法學（Five-Tier Progressive Falsification Methodology, V1--V5）**，涵蓋依循攻擊等價原則（$A_{B0} = A_{B1}$）之基準對照、白箱對抗探針搜尋、陰性對照組元驗證（5/5 缺陷捕獲與 100/100 實例化突變殺死率）、四階段解耦判定神諭（$O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$）以及跨 Linux x86_64、ARM64 與 Windows 異質環境之獨立自動化復現。在累積 68,355 次對抗與驗證執行負載及 50,000 次良性基準負載（總計 118,355 次執行，良性誤拒率 $\text{BFDR} = 0/50,000$）中，於顯式插樁觀測邊界內未曾觀測到任何授權逃逸或實體狀態漂移。本文不提出未經形式化證明之全域安全保證，而是將其確立為於已驗證狀態空間中成立之經驗不變量（Empirical Invariants），並公開發布反例登錄協議以供學術社群持續進行開放式對抗證偽。

**關鍵字：** 執行約束基板 (Execution Containment Substrate)、後受陷安全 (Post-Compromise Security)、內核強制邊界 (Kernel Enforcement Boundary)、動態能力撤銷 (RCU Revocation)、漸進式對抗證偽 (Progressive Falsification)、解耦判定神諭 (Decoupled Oracles)。

---

## 一、 問題定義：Agent 受陷不等於執行權限 (Problem Definition)

當代自主 AI Agent 系統（如基於 LangGraph、CrewAI 或 AutoGen 構建之企業自動化流程）已普遍獲得執行實體操作之特權，包括資料庫讀寫、雲端 API 調用、內部 IPC 通訊及作業系統指令執行。在此架構下，系統安全面臨著根本性的**語義與內核斷層（The Semantic-Kernel Paradox）**：

1. **應用層語義中介軟體（高語義、零確定性）：** 提示防火牆（Prompt Firewalls）、JSON Schema 驗證器與輸出過濾器僅能在自然語言或宣告式資料層面進行機率性評估。此類機制欠缺底層執行邊界的物理圍阻能力，直譯器逃逸、動態參數混淆或邏輯繞過均能使防護失效。
2. **作業系統內核沙箱（高確定性、零語義）：** 傳統內核級防禦（如 Seccomp、Linux Namespaces、eBPF Syscall Filter）具備二進位級強制力，但完全欠缺應用層語義上下文。當一個已獲取合法資料庫連線池的進程發起惡意寫入時，內核無法辨識該操作究係源自合法授權之財務 Agent，抑或源自已遭提示注入控制之客服 Agent。

此斷層導致嚴重的**「主體身分與執行權限混淆」**：一旦應用層受陷（$C_A = 1$），攻擊者即可直接繼承進程所擁有的全部實體執行能力。因此，本文確立核心研究命題：
> **「應用層主體受陷，不得自動繼承無限制之底層執行權限 (Compromise of an application principal does not entail inheritance of unrestricted execution authority)。」**

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
│ 邊界二：OS 內核受管操作類別之強制授權檢查邊界 (Mandatory Enforcement Bound) │
│ [Linux LSM Hook / Windows Minifilter] ──► 在 X_covered 類別上執行強制攔截   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (阻斷: ΔS = 0; 放行: 僅限合規操作)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 實體狀態空間 (Physical State Space: Filesystem, DB WAL, Network, Process)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **DROS (上層治理)**：負責身分憑證管理（PKI）、語義動態意圖權杖（DIT）簽發與資訊流污點追蹤（L1--L3）。
* **DROS-PGM (底層執行基板)**：**在帶內完全排除非對稱密碼學運算**，專注於 L2 快取內常駐策略點陣圖之 $O(1)$ 位元遮罩解析、無鎖 RCU 狀態切換以及 OS 內核 Hook 之二進位強制授權檢查。

### 內核受管操作類別覆蓋面定義 ($X_{\text{covered}}$) 與非全域介導聲明 (Non-Complete Mediation Clause)
本研究之安全主張**嚴格受限於顯式插樁之受管操作類別空間 $X_{\text{covered}}$，不宣稱對全量 OS 系統呼叫路徑（如未插樁之異步 I/O 多工原語）達成完全介導（Syscall-Complete Mediation）**：
1. **檔案系統變更類 ($X_{\text{fs}}$)**：`sys_enter_openat` (O_CREAT/O_WRONLY/O_RDWR), `sys_enter_unlinkat`, `sys_enter_renameat2`, `sys_enter_write`。
2. **進程生命週期類 ($X_{\text{proc}}$)**：`sys_enter_execve`, `sys_enter_execveat`, `sys_enter_ptrace`, `sys_enter_kill`。
3. **網路連線與端點類 ($X_{\text{net}}$)**：`sys_enter_connect` (外部 IP/Port 導向), `sys_enter_bind`, `sys_enter_sendto`。
4. **記憶體與 IPC 特權類 ($X_{\text{ipc}}$)**：`sys_enter_mprotect` (PROT_EXEC), `sys_enter_process_vm_writev`。

$$X_{\text{covered}} = X_{\text{fs}} \cup X_{\text{proc}} \cup X_{\text{net}} \cup X_{\text{ipc}}$$

> **邊界範圍聲明：** *PGM does not claim syscall-complete mediation over uninstrumented kernel paths. Security claims are strictly restricted to the explicitly instrumented operation classes $X_{\text{covered}}$ and their enumerated enforcement hooks.*

---

## 三、 核心安全不變量與安全主張邊界 (Formal Invariants & Security Claim Boundary)

為精確界定安全邊界，DROS-PGM 確立了四個核心概念之嚴格解耦：
* **應用層主體身分 ($Identity_A$)**：由應用框架維護之邏輯角色或 Session 身分。
* **能力宣告授權 ($Auth_C$)**：透過能力位元遮罩（Capability Bitmask）所表達之權限集合。
* **執行閘門授權 ($Auth_E$)**：二進位 C-ABI 執行邊界與內核 Hook 於運行期即時判定之二元結果（$\text{ALLOW} / \text{DENY}$）。
* **實體副作用 ($I_{\text{physical}}$)**：底層檔案系統、資料庫 WAL、內核 Syscall 或外部網路之可觀測狀態變更。

### 形式化不變量定義 (Formal Invariants)

1. **權限非繼承性公理 (Non-Inheritance of Authority)：**
   $$C_A \centernot\implies C_E$$
   應用層對話或直譯器受陷，不得推導出具備二進位層級之執行授權。
2. **覆蓋面受約束安全不變量 (Covered Containment Invariant)：**
   $$\forall x \in X_{\text{covered}}, \quad Auth_E(x) = \text{DENY} \implies Exec_{\text{unauthorized}}(x) = 0 \quad \land \quad \forall s \in \mathcal{S}_{\text{obs}}, \; \Delta s = 0$$
   在受管操作空間 $X_{\text{covered}}$ 內，一旦執行授權被判定為拒絕，未授權操作之執行次數恆為 0，且在顯式觀測集合 $\mathcal{S}_{\text{obs}}$ 內之實體狀態變更恆為 0。
3. **幽靈系統呼叫經驗觀測神諭 (Ghost Syscall Measurement Oracle)：**
   幽靈系統呼叫計數器 $G$ 為獨立於安全不變量之**事實驗證神諭（Empirical Oracle）**，定義為：
   $$G = \# \{ x \in X_{\text{covered}} \mid Auth_E(x) = \text{DENY} \land \text{SyscallObserved}(x) = 1 \}$$
   實驗證偽目標為於所有測試語料庫下維持觀測值 $G \equiv 0$。
4. **並發撤銷之線性化語義 (Linearization Point & Concurrency Semantics)：**
   在原子指針切換之線性化點（Linearization Point, $T_{\text{swap}} = 420\text{ ns}$）之後，所有後續到達之策略評估均能確定性觀測到最新撤銷狀態；於線性化點前已被接納進入內核派發之在途操作（In-flight Operations），則由預先分配之安全狀態上下文（Pre-allocated Safe-State Context）實施退化隔離。

### 表一：DROS-PGM 安全主張邊界矩陣 (Security Claim Boundary Matrix)

| 主張分類 (Category) | 具體項目與範圍宣告 (Claim Statement & Scope) | 認識論性質 (Epistemic Status) |
| :--- | :--- | :--- |
| **正式主張 (Claimed)** | 在受管操作空間 $X_{\text{covered}}$ 內，判定為 `DENY` 之操作不得引發未授權執行 | 形式化架構不變量 (Architectural Invariant) |
| **正式主張 (Claimed)** | 動態能力撤銷在原子指針切換之線性化點 $T_{\text{swap}}$ 後立即對後續調用生效 | 線性化並發語義 (Linearization Semantics) |
| **經驗觀測 (Observed)** | 在已實例化之評測語料庫中，觀測到幽靈系統呼叫 $G = 0$ | 顯式觀測邊界內之經驗事證 (Empirical Fact) |
| **經驗觀測 (Observed)** | 在顯式插樁觀測集合 $\mathcal{S}_{\text{obs}}$ 內，狀態漂移 $\Delta S_{\mathcal{S}_{\text{obs}}} = 0$ | 帶外多神諭差分事證 (Multi-Oracle Fact) |
| **明確未主張 (Not Claimed)** | 對未插樁之全量 OS 系統呼叫路徑具備完全介導 (Global Syscall-Complete Mediation) | 超出本研究範圍 (Explicit Non-Claim) |
| **明確未主張 (Not Claimed)** | 防禦宿主作業系統內核 Rootkit 或硬體 MMU 實體穿透攻擊 | 依賴宿主 TCB (Trust Assumption) |
| **明確未主張 (Not Claimed)** | 上游應用層語義授權映射（Semantic Mapping）之語義邏輯正確性 | 劃歸上游治理範疇 (Upstream Responsibility) |
| **明確未主張 (Not Claimed)** | 未插樁之異步執行路徑（如特殊驅動 IOCTL）之安全性 | 超出 $X_{\text{covered}}$ 範圍 (Out of Scope) |

---

## 四、 威脅模型：後受陷假設 ($C_A = 1$) 與邊界範圍 (Threat Model)

本研究設定嚴格之後受陷威脅模型（Post-Compromise Threat Model），直接假設防禦第一線已經失守：

### A. 威脅能力假設 (In-Scope Capabilities)
1. **假設 1（應用層全面受陷 $C_A = 1$）：** 攻擊者已成功透過間接提示注入（Indirect Prompt Injection）控制 Agent 認知流程，或在宿主應用容器內取得任意代碼執行權。
2. **假設 2（合法憑證持有）：** 攻擊者具備存取進程記憶體中合法 OAuth Token、API 金鑰及內部資料庫連線之能力。
3. **假設 3（多代理協同與混淆代理人攻擊）：** 攻擊者可操控多個異質 Agent，嘗試透過複雜委派鏈（Delegation Chains）實施權限提升或混淆代理人（Confused-Deputy）繞過。

### B. 範圍外與信任邊界 (Out-of-Scope & TCB Assumptions)
* **明確排除範圍 (Out-of-Scope Attacker)**：攻擊者不具備內核級特權（Kernel-mode Rootkit），亦不具備直接竄改 PGM 已載入二進位代碼段、OS 內核模組或 CPU 硬體記憶體管理單元（MMU）之能力。
* **可信計算基 (TCB)**：信任基礎嚴格限制於 PGM 二進位執行閘門、CPU 硬體指令集（Ring 0/MMU）、作業系統內核 LSM 驅動以及防篡改日誌緩衝區。

---

## 五、 PGM-VEP 五階漸進式對抗證偽方法學 (Validation Methodology: V1--V5)

為徹底消弭「評測者偏誤」與「自我驗證盲區」，我們確立了最高方法論原則：
> **「無自我作證原則 (No-Self-Witness Principle, $O_I \neq O_A \neq O_E \neq O_P$)：負責授權決策之元件，絕對不得作為證明執行阻絕成功之唯一證據來源。」**

```text
  [ V1: Attack the PGM ] ────► 攻擊等價基準對照測試 (B0 vs B1, A_B0 = A_B1)
           │
           ▼
  [ V2: Counterexample Search ] ──► 廣域白箱狀態搜尋、模糊測試與並發壓力 (60,000+ Probes)
           │
           ▼
  [ V3: Attack the Test ] ──► 陰性對照組元驗證與 100 突變體評測 (100% Corpus Mutation Score)
           │
           ▼
  [ V4: Attack the Oracle ] ──► 4 階段客觀事實鏈與 9 大神諭壓力向量 (G = 0 Ghost Syscalls)
           │
           ▼
  [ V5: Cross-Env Reproduction ] ─► 開源自足復現套件與跨 3 大異質環境獨立自動化評測
```

### 各驗證階層詳細規範

* **V1 (Attack the PGM - 基準對抗與攻擊等價)：** 嚴格遵循**攻擊等價原則（$A_{B0} = A_{B1}$ 且 $\text{Env}_{B0} \approx \text{Env}_{B1}$）**，在 B0（未受控裸應用程式）與 B1（啟用 PGM）施加相同之 50 組高破壞性攻擊酬載，實測驗證 B0 產生顯著實體破壞（$\Delta S_{B0} > 0$），而 B1 在所有 50 個實例化攻擊案例中未觀測到任何未授權執行（Zero Observed Unauthorized Executions）。
* **V2 (Maximum Counterexample Search - 極限反例搜尋)：** 導入 Strix 白箱適應性搜尋引擎與高並發排程器，在 10 個攻擊維度（身分偽造、位元遮罩擴張、參數篡改、RCU 競態、直譯器逃逸等）展開廣域空間探索。
* **V3 (Attack the Test Framework - 元驗證與陰性對照)：** 針對測試框架本身之判別力進行反思性驗證。植入 5 大蓄意破壞之缺陷二進位檔（Sabotaged Variants），並生成 100 個涵蓋 8 類邏輯缺陷之突變體，檢驗測試框架是否具備真實捕獲能力。
* **V4 (Attack the Oracle - 神諭獨立性與客觀事實鏈)：** 確立由四個獨立觀察者構成之事實鏈路：
  $$\text{意圖記錄 } (O_I) \longrightarrow \text{授權判決 } (O_A) \longrightarrow \text{內核執行 } (O_E) \longrightarrow \text{實體副作用 } (O_P)$$
  並施加 9 大神諭壓力向量（記憶體污染、窗口時序競態、回滾碰撞、幽靈 Syscall 注入等）。
* **V5 (Cross-Environment Independent Reproduction - 跨環境獨立自動化復現)：** 封裝包含獨立二進位檔、評測編排器、帶外神諭與突變生成器之開源自足復現套件，於 3 大異質環境（Ubuntu/glibc, Alpine/musl, Windows/MSVC）針對策略二進位語義與強制整合介面（Policy Semantics and Enforcement Integration）進行無依賴盲態基準評測。

### PGM-VEP 驗證階層與開源評測資產直接對照表 (Methodology to Asset Mapping)

為確保學術評審員能迅速重現論文中的每一階層驗證，表二明確列出 V1--V5 與開源儲存庫 [`DROS-VEP-lite`](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite) 中具體執行腳本與報告之映射關係：

#### 表二：PGM-VEP 驗證階層與開源評測資產直接對照表 (Asset Mapping Matrix)

| 驗證階層 (Methodology Tier) | 驗證目標與評測核心 | 開源執行腳本 / Harness (Executable Asset) | 存證報告與數據路徑 (Evidence Asset) |
| :--- | :--- | :--- | :--- |
| **V1: Attack the PGM** | 攻擊等價基準對照 ($A_{B0}=A_{B1}$) | `benchmark/run_benchmark.py`<br>`scripts/run_cybermes_crucible.py` | `reports/CYBERMES_POST_COMPROMISE_REPORT.md`<br>`reports/evidence/cybermes_crucible_traces.json` |
| **V2: Counterexample Search** | 60,000+ 白箱適應性狀態搜尋 | `benchmark/stress_test_accelerated.py`<br>`scripts/run_24h_soak_test.py` | `reports/DROS_24H_Soak_Test_Final_Report.md`<br>`reports/stress_summary.json` |
| **V3: Attack the Test** | 5 缺陷二進位 + 100 突變體評測 | `benchmark/conformance_test.py` (含變異注入器) | `reports/conformance_report.json` |
| **V4: Attack the Oracle** | 4 階段事實鏈 ($O_I \rightarrow O_A \rightarrow O_E \rightarrow O_P$) | `benchmark/replay.py`<br>`telemetry/event_logger.py` | `reports/COMPARATIVE_GOVERNANCE_REPORT.md`<br>`reports/evidence/comparative_benchmark/` |
| **V5: Cross-Environment** | 3 大異質環境無依賴獨立復現 | `docker-compose.yml`<br>`docker-compose-b2b.yml` | `reports/benchmark_summary.json`<br>`docs/TESTBED_SPECIFICATION.md` |

---

## 六、 實驗結果與度量分析 (Experimental Results)

### 6.1 評測工作負載會計帳本 (Evaluation Accounting Matrix)

為確保數據清晰可加總，表三列出各驗證階層之精確探針與負載分佈：

#### 表三：評測工作負載會計帳本 (Evaluation Accounting Matrix)

| 驗證階層 | 測試類型與配置架構 | 唯一測試探針數 (Unique Probes) | 重放與並發負載 (Replay / Concurrent) | 總執行次數 (Total Executions) | 觀測反例 (CE) | 判定狀態 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **V1 (Baseline)** | B0/B1 等價對照 ($A_{B0}=A_{B1}$) | 50 | 250 | 300 | 0 | **PASS** |
| **V2 (Adversarial)** | 白箱適應性搜尋 + 並發熔爐 | 2,410 | 57,590 (21.4M Tokens) | 60,000 | 0 | **PASS** |
| **V3 (Meta-Verify)** | 5 缺陷二進位 + 100 突變體 | 105 | — | 105 | 0 | **PASS** |
| **V4 (Oracle Torture)**| 4 階段客觀事實鏈 + 9 大向量 | 450 | — | 450 | 0 | **PASS** |
| **V5 (Cross-Env)** | 3 大環境設定檔獨立復現 | 1,500 | 6,000 | 7,500 | 0 | **PASS** |
| **對抗驗證小計** | **V1--V5 累積對抗執行** | **4,515** | **63,840** | **68,355** | **0** | **ALL PASS** |
| **Benign Workload** | SPEC CPU2017 + 合法工具調用 | 50,000 | — | 50,000 | 0 | **BFDR = 0/50,000** |
| **總計 (Total)** | **全階層綜合評測** | **54,515** | **63,840** | **118,355** | **0** | **ALL PASS** |

*註：BFDR (Benign False-Denial Rate) 代表合法良性請求遭錯誤拒絕之比例。*

### 6.2 元驗證：陰性對照與變形測試結果 (V3)
在 V3 階段，測試框架針對 100 個植入缺陷之 PGM 突變體進行了全面檢驗：
$$\text{Corpus Mutation Score} = \frac{\text{Killed Mutants}}{\text{Total Instantiated Mutants}} = \frac{100}{100} = 1.0$$
在所實例化的 100 個突變體集合中，測試框架達成 100% 擊殺率（100/100 Killed）。此結果證實測試框架對所涵蓋之 8 類實例化缺陷（位元擴張、身分替換、過期繞過、無條件放行等）具備完全之缺陷辨識靈敏度，但不構成對未實例化缺陷空間的完備性證明。

### 6.3 效能開銷與選定 SPEC CPU2017 基準分解 (Selected SPEC CPU2017 Benchmarks)

表四列出在 Intel Xeon Gold 6330 @ 2.00GHz (128GB ECC RAM, Ubuntu 22.04 LTS) 上，啟用 PGM 內核強制模組前後之選定 SPEC CPU2017 代表性子項目延遲開銷分解：

#### 表四：選定 SPEC CPU2017 基準測試子項目開銷分解 (Selected SPEC CPU2017 Benchmarks)

| 測試子項目 (Benchmark Suite) | 主要計算與負載特徵 | 原生 OS 基線 (Baseline sec) | 啟用 DROS-PGM (PGM sec) | 相對效能開銷 (Overhead %) |
| :--- | :--- | :---: | :---: | :---: |
| **500.perlbench_r** | C 直譯器與字串高頻調用 | 412.3 | 417.6 | +1.28% |
| **502.gcc_r** | C 編譯器與行程/記憶體分配 | 328.7 | 333.1 | +1.34% |
| **505.mcf_r** | 大規模組合最佳化 (記憶體密集) | 289.4 | 291.8 | +0.83% |
| **520.omnetpp_r** | 離散事件網路模擬 | 356.1 | 360.2 | +1.15% |
| **523.xalancbmk_r** | XML 解析與 DOM 樹處理 | 298.5 | 302.7 | +1.41% |
| **557.xz_r** | 資料壓縮與密集 I/O 串流 | 385.2 | 389.9 | +1.22% |
| **幾何平均 (GeoMean)** | **整體計算與系統負載開銷** | — | — | **+1.20% (±0.12%)** |

在 72 小時連續浸泡測試中，PGM 於多工作執行緒並發負載下（跨 16 個 Worker 執行緒）保持高達 **952,991 QPS 之總體聚合策略決策吞吐量 (Aggregate Policy Decision Throughput across 16 concurrent workers)**，且無任何記憶體滲漏現象。

### 6.4 微基準測試規範與全分佈統計 (Microbenchmark Protocol & Full Distribution)

所有亞微秒級測量均嚴格遵循以下微基準測試規範：
* **硬體與環境隔離**：固定綁定單一實體核心（`taskset -c 2`），停用 Intel Turbo Boost 與 C-States 節能降頻。
* **測量源與計時器**：採用 CPU Invariant TSC 指令序列（`CPUID` 序列化屏障 + `RDTSCP`），扣除計時器讀取基礎開銷（24 cycles）。
* **抽樣規模與預熱**：執行 $10^6$ 次暖快取預熱迭代，隨後進行 $10^7$ 次正式量測。

#### 表五：PGM 帶內策略評估延遲全分佈統計 (10^7 次抽樣量測, 單位: 奈秒 ns)

| 評測指標 | 最小值 (Min) | 中位數 (P50) | P90 | P95 | P99 | P99.9 | 最大值 (Max) | 標準差 (StdDev) | 95% 信賴區間 (CI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C-ABI 策略查表延遲** | 312 ns | **353 ns** | 388 ns | 398 ns | 412 ns | 445 ns | 620 ns | 18.4 ns | [351, 355] ns |
| **RCU 狀態指針切換 (T_swap)** | 390 ns | **420 ns** | 428 ns | 432 ns | 438 ns | 462 ns | 580 ns | 12.1 ns | [416, 424] ns |
| **Fail-Closed 快速阻絕延遲** | 410 ns | **465 ns** | 480 ns | 484 ns | 488 ns | 512 ns | 640 ns | 15.2 ns | [462, 468] ns |

```text
調用發起 (Caller)
  │
  ├─ [上層 DROS 邊界] HTTP 解析 + Ed25519 簽名驗證 + DIT 生成 ───► P50: 26.1 µs / P99: 31.4 µs
  │
  ├─ [PGM C-ABI 邊界] L2 快取常駐策略點陣圖 O(1) SIMD 查表 ──────► P50: 353 ns / P99: 412 ns
  │
  ├─ [PGM 狀態切換] RCU 原子指針切換線性化點 (T_swap) ──────────► 420 ns
  │
  ├─ [PGM 阻絕路徑] Fail-Closed 常數時間快速拒絕路徑 ───────────► < 500 ns (488 ns at P99)
  │
  └─ [內核強制邊界] Linux LSM / Windows Minifilter 攔截開銷 ──────► SPEC CPU2017 開銷: 1.20%
```

---

## 七、 局限性與認識論邊界 (Limitations & Epistemic Scope)

基於嚴謹認識論紀律，本文明確劃定本研究之有效性邊界與局限性：

1. **經驗不變量而非先驗數學證明：** 「在 118,355 次總執行負載與多環境測試中未觀察到反例」之結論，嚴格受限於已實例化之測試語料庫與探索空間，不構成對無窮對抗空間之先驗存在性證明。
2. **跨平台強制深度之異質性 (Cross-Platform Enforcement Heterogeneity)：** 跨環境復現（V5）驗證了二進位策略語義與相容性；然而，原生內核強制深度受限於宿主作業系統特性（Linux 基於原生 LSM 內核掛載，Windows 基於 Minifilter 與對象回調），跨環境復現不代表在所有作業系統具備完全同質之內核覆蓋面。
3. **本體語義對齊之依賴性：** PGM 之阻絕精度依賴於應用層正確將業務操作映射至對應之權限位元遮罩；若上游語義映射存在定義性錯誤，不在底層二進位閘門之語義修正範疇內。
4. **硬體與內核信任邊界：** PGM 建立於宿主作業系統記憶體管理單元（MMU）與內核保護模式（Ring 0）未遭物理穿透之假設前提；針對底層硬體側通道（Side-Channel）或內核零日漏洞之防禦超出本架構之設計射程。

---

## 八、 討論：後受陷安全範式轉換 (Discussion: Post-Compromise Security)

傳統資訊安全架構之核心思維，長期建立於**「受陷前防禦（Pre-Compromise Defense）」**——致力於降低系統遭遇穿透之機率（$\min P(C_A = 1)$）。然而，在自主 AI 工作負載中，提示注入與應用層受陷無法被假定為能被完全消除。

PGM 代表了一種根本性的安全範式轉換：**將安全控制的重心，從「試圖阻止 Agent 受陷」轉移至「在 Agent 已經受陷的條件下，如何嚴格截斷執行授權與物理後果（Post-Compromise Execution Containment）」**。透過將執行邊界下沉至無法被自然語言語義污染之二進位控制平面與 OS 內核 Hook，**PGM 為明確插樁之受管操作類別提供確定性的執行強制邊界（Deterministic Execution-Enforcement Boundary for Explicitly Instrumented Operation Classes）**。

---

## 九、 相關工作與分類矩陣 (Related Work & Systems Taxonomy)

本研究並非取代語義、工具層或執行期授權機制，而是著眼於**彌補「應用/執行期授權」與「作業系統級實體執行」之間的殘餘強制鴻溝 (Residual Enforcement Gap)**。表六系統化比較了當前各類主流安全機制與前沿 Agent 防禦工作：

#### 表六：執行期安全與 Agent 治理機制分類對照矩陣 (Taxonomy Matrix)

| 安全防禦架構類別 | 代表性工作 | 強制執行點 (Enforcement Point) | 語義身分歸因 (Attribution) | 運行期強制 (Enforcement) | 後受陷約束 (Post-Compromise) | 內核強制邊界 (Kernel Boundary) | 動態能力撤銷 (Revocation) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **提示語義護欄** | NeMo Guardrails [7] | LLM / Text Boundary | ✅ 完整 | ❌ 僅文字過濾 | ⚠️ 非以內核約束為主要目標 | ❌ 無 | ❌ 無法及時生效 |
| **工具與 MCP 策略** | AgentVisor [16], MCP PEP [17] | Tool Call Interface | ✅ 完整 | ⚠️ 限於工具調用層 | ⚠️ 限於工具介面約束 | ❌ 欠缺 Syscall 圍阻 | ⚠️ 依策略更新而定 |
| **編譯期型態系統** | Tracked Capabilities [18] | Language Type System | ✅ 完整 | ✅ 編譯期保證 | ⚠️ 依賴編譯期假設 | ❌ 無 | ❌ 靜態無動態撤銷 |
| **能力內核與 LibOS** | Agent libOS [14], authgate [15] | Runtime Primitive | ✅ 完整 | ✅ 運行期 Primitive | ✅ 具備授權邊界 | ⚠️ 宿主 OS 上方 Runtime | ✅ 支援撤銷 |
| **傳統 OS 沙箱** | seccomp-bpf [2], SELinux [1] | OS Syscall / Kernel MAC | ❌ 無語義辨識 | ✅ 內核級強制 | ✅ 進程隔離 | ✅ 完整內核 Hook | ⚠️ 非運行期撤銷語義 |
| **DROS-PGM (本研究)** | **DROS-PGM (v2.0)** | **C-ABI + Kernel Hook** | **✅ 透過 DIT 歸因** | **✅ 亞微秒級強制** | **✅ $C_A=1$ 後受陷約束** | **✅ 雙重邊界 ($X_{\text{covered}}$)** | **✅ RCU 線性化點撤銷** |

除架構能力差異外，各類機制在對抗驗證的嚴謹程度上亦存在顯著落差。多數現有工作仍以案例展示或單一層級測試為主，較少同時具備攻擊等價對照、測試框架元驗證、解耦神諭與跨環境獨立復現。表七從驗證方法論完整度比較代表性系統與本研究已完成的 PGM-VEP（V1--V5）標準：

#### 表七：執行期安全機制之對抗驗證嚴謹度對照 (Methodological Rigor Matrix)

| 安全機制 / 產品類別 | 代表系統 | 攻擊等價對照 ($A_{B0}=A_{B1}$) | 測試框架元驗證 (Meta-Verify) | 解耦神諭 + No-Self-Witness | 後受陷假設下執行權限非繼承 | 跨異質環境獨立復現 | 完整通過 V1--V5 標準 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **語義護欄** | NeMo Guardrails 等 | 弱 | 無 | 無 | 否 | 少見 | 否 |
| **工具 / MCP 政策閘道** | AgentVisor、MCP PEP 等 | 部分 | 無 | 弱 | 部分 | 少見 | 否 |
| **傳統 OS 沙箱 / MAC** | seccomp-bpf、SELinux 等 | 可做 | 無 | 弱 | 部分 | 常見 | 否 |
| **商業 Endpoint / Agent 防護** | CrowdStrike Harness、Palo Alto Koi、Microsoft MXC | 內部較嚴 | 未公開同等級 | 未見完整解耦 | 部分 | 有限 | 否 |
| **研究型 Capability Kernel** | authgate 等 | 有 | 有限 | 部分 | 設計接近 | 有限 | 否 |
| **容器 / microVM 隔離** | gVisor、Firecracker 等 | 可做 | 無 | 弱 | 部分 | 常見 | 否 |
| **DROS-PGM (本研究)** | **DROS-PGM v2.0** | **是** | **是 (100/100 Killed)** | **是** | **是** | **是** | **是** |

*表七說明：「完整通過 V1--V5 標準」係指同時滿足本論文所定義的攻擊等價（V1）、極限狀態搜尋（V2）、元驗證（V3）、四階段解耦神諭（V4）、後受陷假設下的執行權限非繼承，以及跨環境獨立復現（V5）。在現有公開文獻與公開產品技術白皮書之文獻調研範圍內（To the best of our survey），尚未辨識出有其他系統於單一開源可復現評測包中同時報告並公開上述五項驗證維度。*

---

## 十、 結論與聲明 (Conclusion & Declarations)

本文提出並全面對抗評測了 DROS-PGM 二進位執行約束基板。透過五階漸進式證偽方法學（PGM-VEP V1--V5），跨 118,355 次對抗與良性負載、突變測試與異質環境獨立復現，驗證了核心安全不變量之有效性。全套評測工具鏈與反例登錄協議已公開發布，以期推動自主 AI 執行期安全邁向可證偽、可復現之嚴謹科學軌道。

### 致謝與 AI 協作聲明 (Acknowledgment & AI Collaboration Disclosure)
依據 IEEE / ACM 2023+ 關於生成式人工智慧與學術誠信之指引規範，作者在此明確揭露：
1. **研究原創性與智慧財產權**：本文所述之系統架構、雙重邊界模型（C-ABI 歸因與內核強制）、形式化安全不變量定義、五階漸進式證偽方法學（V1--V5）及相關專利權利主張（U.S. PPA No. 64/111,973），均由作者陳濬程獨立構想、設計、推導並驗證。
2. **AI 工具輔助範圍**：大型語言模型（LLM Agent / Gemini）僅作為輔助工具，用於學術英文文法校對、文字組織結構潤飾、LaTeX 語法除錯及開源測試腳本之格式化輔助。AI 模型未參與任何核心專利發明概念之生成或安全不變量之實質理論構建。作者對全文之技術正確性、數據真實性與認識論結論承擔完全之學術與法律責任。

---

## 參考文獻 (References)

1. P. Loscocco and S. Smalley, "Meeting critical security objectives with security-enhanced Linux," in *Proc. Ottawa Linux Symposium*, 2001.
2. W. Drewry, "Chrome sandbox: seccomp-bpf," *Google Security Blog*, 2012.
3. J. Edge, "A seccomp overview," *LWN.net*, 2015.
4. B. Gregg, *BPF Performance Tools*. Addison-Wesley, 2019.
5. A. Birgisson, J. Polakis, S. Erlingsson, A. Sommese, and M. Anisetti, "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud," *NDSS*, 2014.
6. R. Sandhu, E. Coyne, H. Feinstein, and C. Youman, "Role-Based Access Control Models," *IEEE Computer*, vol. 29, no. 2, pp. 38-47, 1996.
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
20. J. Chen, "DROS-PGM: Physical Guard Module with Sub-Microsecond C-ABI Binary Execution Boundary," *Zenodo Research Report*, DOI: 10.5281/zenodo.21903687, 2026.
