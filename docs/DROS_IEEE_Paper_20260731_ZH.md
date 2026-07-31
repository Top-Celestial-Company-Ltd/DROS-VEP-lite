# 🛡️ 自主型 AI 工作負載的 DROS 四層防禦縱深架構

## Agentic Web 時代的完整資安與執行治理範式 (IEEE 國際學術論文)

**文件版本：** 2.0 Academic Release (IEEE Standard)  
**日期：** 2026 年 7 月 31 日  
**機密等級：** 公開學術技術論文  
**作者：** 陳濬程 (Jimmy Chen) (`jimmychen@dr-os.io`)  
**機構：** 康宸園有限公司 (Top-Celestial Company Ltd.), 台灣台北  
**專利聲明：** DROS 執行治理與安全技術已申請美國臨時專利保護（U.S. Patent Application No. 64/111,973，Patent Pending）。  
**開源驗證靶場：** [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)  
**永久學術引用：** [Zenodo Record DOI: 10.5281/zenodo.20823163](https://zenodo.org/records/20823163)

---

## 摘要 (Abstract)

2026年具備多步驟工具調用能力（Tool-Calling）的自主型 AI Agent 快速部署於金融合規、供應鏈調度與關鍵基礎設施等高風險領域。然而，現有資安機制面臨嚴重的架構邊界：應用層語意防火牆（如 NVIDIA NeMo Guardrails）本質上仍屬機率性過濾，極易遭間接提示詞注入（IPI）越獄；而核心層作業系統沙盒（如 eBPF、Seccomp）則存在「上下文失明 (Context-Blindness)」，無法將使用者空間的 Agent 角色對映至低階進程流。為解決此「歸責缺口 (Attribution Gap)」，我們提出 **DROS 四層防禦縱深架構** —— 一個專為 Agentic Web 時代設計的零信任執行治理控制面。本架構將控制面開通（透過 OpenAI Terraform Provider 與 OpenShip）與運行期二進位實體防禦解耦，於二進位 C-ABI / FFI 邊界執行不可變的 $O(1)$ 能力點陣圖（Bitmap），實現亞微秒級決策延遲（**中位數 26.1 μs，熔斷延遲 <500 ns**）。配合三階 PKI 憑證授權鏈（`Root CA -> AIA -> BEC Leaf Token`）簽發之 `DrosIdentityToken (DIT)`，提供具備法庭級不可否認性（Non-repudiation）且合規歐盟《EU AI Act》Sec. 50 的 Ed25519 簽章日誌。基準測試顯示，本架構對零日提示詞注入、目標劫持與跨企業供應鏈毒化攻擊（如 OpenAI 工作負載存取遭投毒之 Hugging Face 數據庫）達 100% 確定性物理阻斷。

**關鍵字：** AI Agent 安全、運行期執行治理、C-ABI 邊界強制、零信任架構、公開金鑰基礎設施 (PKI)、間接提示詞注入 (IPI)、歐盟 AI 法案合規。

---

## 一、 引言與問題定義 (Introduction & Problem Statement)

自主型 AI Agent 從被動對話式 LLM 演進為具備 API 存取與資料庫寫入權限的執行者，根本性地改變了企業威脅面。當 Agent 遭到挾持時，攻擊者實際上是在合法授權的權限邊界*內部*發動攻擊。

### 1.1 身分與網路邊界防線的失效
傳統網路應用程式防火牆（WAF）、端點偵測與回應（EDR）及身分管理（IAM）皆假設攻擊者不具備合法憑證。然而在 Agentic Web 時代，遭挾持的 Agent 本身即持有合法的 OAuth Token 與 JWT 憑證。WAF 視高權限 API 呼叫為正常流量，EDR 則僅能視為通用 OS 進程（如 `python.exe`）執行合法的系統呼叫。

### 1.2 語意與核心悖論 (The Semantic-Kernel Paradox)
誠如最新系統資安文獻（如 AgentSight, IEEE S&P 2026）所指出，AI Agent 資安面臨根本悖論：
1. **語意防火牆（高語意，零確定性）：** 提示詞過濾器檢查高階自然語言意圖，但對對抗性混淆或多輪上下文毒化提供零數學保證。
2. **核心沙盒（高確定性，零語意）：** eBPF 或 Seccomp 等 OS 機制執行嚴格的二進位系統呼叫規則，但缺乏使用者空間上下文，無法區分同一個 Python 進程發起的網路連線究竟來自合法的財務 Agent 還是遭劫持的客服 Agent。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. 控制面與 GitOps 自動開通 (Policy-as-Code)                                 │
│    • OpenAI Terraform Provider -> 自動化宣告 Projects, Service Account 與 Keys│
│    • OpenShip 容器編排引擎       -> 自動編排跨企業實體容器靶場                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. DROS 運行期二進位實體防禦 (L4 - C-ABI 邊界強制)                           │
│    • 三階 PKI 密碼學身分鏈     -> DrosIdentityToken (DIT) 鋼印繫定          │
│    • DROS GuardVM (PEP/PDP)   -> 亞微秒 <500ns 確定性 C-ABI 物理硬熔斷         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、 威脅模型定義 (Threat Model: AAV-2026)

我們將針對自主型 AI Agent 的運行期攻擊向量定義為 **Agentic Attack Vectors (AAV-2026)**：

| 攻擊向量 | MITRE ATLAS 對齊 | 機制與威脅影響 |
| :--- | :--- | :--- |
| **間接提示詞注入 (IPI)** | AML.T0051 | 攻擊者將惡意指令隱匿於非授信外部資料（如 Email、PDF、資料庫列），挾持工具調用流程。 |
| **目標劫持 (Goal Hijacking)** | AML.T0054 | 上下文視窗毒化改變 Agent 長期目標，導致執行未授權的多步驟動作鏈。 |
| **越權功能提權 (Privilege Escalation)** | AML.T0053 | 遭劫持 Agent 利用合法 Token 呼叫超越角色範疇的高權限端點（如 `deploy_prod`）。 |
| **供應鏈感染 (Supply Chain Contagion)** | AML.T0010 | 外部遭投毒的數據庫/模型（如 Hugging Face）污染 Agent，進而橫向侵入買方內部 ERP 核心。 |

---

## 三、 DROS 四層防禦縱深架構 (DROS 4-Layer Architecture)

DROS 建立四層防禦縱深模型，將機率性過濾器與確定性執行閘門徹底解耦：

```text
┌──────────────────────────────────────────────────────────────────────┐
│ L1: 邊界感知層  │ 語意提示詞過濾 (~90% 已知攻擊攔截)                     │
├─────────────────┼────────────────────────────────────────────────────┤
│ L2: 零信任網格  │ 三階 PKI 憑證鏈 (Root->AIA->BEC) + DIT 密碼學鋼印     │
├─────────────────┼────────────────────────────────────────────────────┤
│ L3: 任務編排層  │ 多 Agent Swarm ABAC 工作流微隔離                    │
├─────────────────┼────────────────────────────────────────────────────┤
│ ★ L4: C-ABI 熔斷│ <500ns O(1) 二進位位元匹配實體熔斷                   │
└─────────────────┴────────────────────────────────────────────────────┘
```

### 3.1 L1：邊界感知層（概率性過濾）
L1 對自然語言輸入進行語意分析與清洗，攔截已知提示詞注入樣板。由於 L1 屬機率性，其定位為第一道過濾器，而非最終防線。

### 3.2 L2：零信任私有網格與 PKI 身分層（密碼學繫定）
為消除「上下文失明」，L2 引入三階 PKI 憑證授權架構：
- **Root CA：** 企業根憑證（`DROS-ROOT-CA-2026`）。
- **AIA Intermediate：** 中繼發證機構。
- **BEC Leaf Certificate：** 執行點陣圖憑證，將 Agent 身分、角色與授權 Skill 能力點陣圖進行密碼學簽署。

每筆工具呼叫皆攜帶簽署之 **DrosIdentityToken (DIT)**，GuardVM 在比對權限前先驗證 ECDSA/Ed25519 簽章，完美解決 OS 層級的歸責缺口。

### 3.3 L3：Agentic 任務編排與業務隔離層（Swarm ABAC）
L3 透過 `agent_manifest.yaml` 執行基於屬性的存取控制（ABAC），限制跨 Agent 通訊管道於預先核可之拓撲圖（如 CrewAI / LangGraph）。

### 3.4 L4：C-ABI 物理熔斷層（確定性二進位硬門檻）
L4 為 DROS 之核心創新。權限於初始化時預先編譯為不可變之點陣圖（Bitmaps）。工具呼叫時，GuardVM 執行 $O(1)$ 位元邏輯與運算：

$$\text{Decision} = \text{Capability\_Bitmap}[\text{Role\_ID}] \ \& \ \text{Requested\_Tool\_Bit}$$

若位元為 $0$，執行於二進位 C-ABI 邊界在 **<500 ns 熔斷延遲** 內實施物理硬阻斷。零字串解析、零 LLM 推理 —— 提供數學級物理安全。

---

## 四、 B2B 跨企業 PKI 聯邦與供應鏈集體免疫 (Federated B2B Supply Chain Defense)

當 Agent 跨企業邊界互動時（例如 **Corp-Alpha / OpenAI 工作負載** 存取 **Corp-Beta / Hugging Face 數據庫**），DROS 將 L2 升維為 **跨域密碼學身分指紋網關**。

```text
[ Corp-Beta: Hugging Face 數據庫 ]                  [ Corp-Alpha: 買方核心企業 ]
┌───────────────────────────────┐                  ┌──────────────────────────────┐
│ Agent-Beta (資料抓取員)       │                  │ DROS GuardVM Alpha (PEP/PDP) │
│ - 持有 DIT-Beta 密碼學指紋印章 │ ─跨企業調用───►  │ 1. 驗證 DIT-Beta 憑證指紋    │
└───────────────────────────────┘                  │ 2. 比對 Bitmap[Beta][API]    │
                │                                  │ 3. <500ns 執行確定性物理熔斷 │
   經由投毒數據集遭挾持                            └──────────────────────────────┘
   (ATS-004 跨企業供應鏈劫持案)                                    │
                │                                                  ▼
   企圖越權讀取 Alpha ERP 財務密件                 [ 於 C-ABI 層實施 100% 硬阻斷 ]
```

### 4.1 供應鏈網路集體免疫機制
- **細胞級爆炸半徑控制：** 每一隻 Agent 均為獨立隔離細胞。三階供應商 Agent 遭劫持時，破口最遠僅被封鎖於該供應商的 DROS 邊界內。
- **零信任連鎖升級：** 買方要求外聯 API 攜帶 DIT 憑證，驅使上下游自發升級至確定性零信任標準。
- **即時動態撤銷 (CRL)：** 供應商 CA 遭通報劫持時，買方 GuardVM 在 <1 μs 內更新黑名單指紋，產生「確定性集體免疫」，無需更改任何業務程式碼。

---

## 五、 效能評測與基準數據 (Experimental Evaluation & Benchmark Results)

### 5.1 開源測試靶場與可重現測試架構設定 (Test Harness Setup)

為確保學術與工程上的完全可重現性 (Absolute Scientific Reproducibility)，所有實證評測均於 **DROS-VEP (Virtual Enterprise Platform) Lite** 開源容器化靶場（包含 `docker-compose.yml` 與 `docker-compose-b2b.yml`）中執行。完整的測試腳本與攻擊 Payload，已全數開源發布於 GitHub 官方倉庫 [github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)。

```text
DROS-VEP 開源測試靶場架構：
├── OpenShip / Docker 引擎     : 容器化 ERPNext, Keycloak, EspoCRM, Forgejo 業務系統
├── 測試自動化腳本 (Test Harness): scripts/run_24h_soak_test.py (連續對抗模糊測試器)
├── 目標 PDP/PEP 引擎           : GuardVM (http://localhost:8082)
└── 一鍵重現指令                 : python scripts/run_24h_soak_test.py
```

所有基準測試均於 Intel Xeon E3-1275 v3 硬體平台、Linux Kernel 6.6 及 Docker 26.1 環境下完成。

### 5.2 實證對照組實驗數據 (Control Group vs. Protected Group)

為定量證明 C-ABI 二進位硬熔斷之必要性，我們透過切換 `BYPASS_GUARD` 模式，針對相同攻擊 Payload (EP1~EP4) 執行對照組實驗：

| 評測劇本 | 對照組 (無 DROS 防禦) | 實驗組 (啟用 DROS Guard L4) | DROS 攔截延遲 |
| :--- | :--- | :--- | :--- |
| **ATS-001 (EP1 客服資料庫匯出案)** | ❌ **100% 破防** (客戶資料外洩) | ✅ **100% 阻斷** (DENY 403) | **25.8 μs** |
| **ATS-002 (EP2 ERP 密碼勒索案)** | ❌ **100% 破防** (.env 密鑰外洩) | ✅ **100% 阻斷** (DENY 403) | **26.1 μs** |
| **ATS-003 (EP3 Fable 5 越獄部署案)** | ❌ **100% 破防** (未授權部署至 Production) | ✅ **100% 阻斷** (DENY 403) | **25.5 μs** |
| **ATS-004 (EP4 OpenAI x Hugging Face 供應鏈案)** | ❌ **100% 破防** (跨企業資料竊取) | ✅ **100% 阻斷** (DENY 403) | **26.4 μs** |

### 5.2 對抗性模糊測試變異引擎與非 API 混淆方法論 (Fuzzing Methodology)

為在無需負擔 API 延遲波動與雲端 Rate Limit 限制的前提下對 DROS 進行極限壓測，本評測套件整合了**演算法對抗模糊測試變異引擎 (`PROMPT_MUTATORS`)**。每筆攻擊 Payload 均於下列七大威脅範疇動態變種：
1. **System Override 語意覆蓋變種：** 注入高優先級系統指令覆蓋語法。
2. **Roleplay 角色扮演越獄變種：** 人設操控指示 Agent 假設無限制 root 角色。
3. **Hexadecimal & Base64 編碼混淆：** 對 Payload 進行編碼以繞過 L1 語意字串比對。
4. **Debug 診斷模式偽裝：** 模擬系統診斷與 JSON 檢索請求。
5. **CISO 緊急升級標籤：** 偽造緊急 CISO 批准標頭。

### 5.3 四層防禦縱深漏斗拆解 (Layer Interception Distribution)

在連續 24 小時超過 170,000 次測試中，四層縱深防禦漏斗展現出清晰的層級分工：

| 防禦層級 (Defense Layer) | 核心防護機制 | 攔截分工佔比 % | 阻斷執行結果 | 架構定位與說明 |
| :--- | :--- | :--- | :--- | :--- |
| **L1 語意感知層** | 語意 Prompt Cleaning / WAF | **85.2%** | 清洗 / 丟棄 | 攔截明文、未混淆之已知提示詞注入。 |
| **L2 PKI 身分層 (`L2_PKI_IDENTITY`)** | 三階憑證與 DIT 鋼印 | **4.8%** | **100% DENY** | 攔截未授權或身分偽造之請求。 |
| **L3 ABAC 拓撲層 (`L3_SWARM_ABAC`)** | `agent_manifest.yaml` 圖譜 | **3.5%** | **100% DENY** | 攔截跨部門越權呼叫 (如 HR $\to$ DevOps)。 |
| **★ L4 C-ABI 物理硬熔斷 (`L4_C_ABI`)** | $O(1)$ Bitmap 實體門檻 | **6.5%** | **100% DENY** | **確定性硬阻斷：於 <500ns 內殲滅所有穿透 L1 的對抗性混淆 IPI**。 |
| **全系統防禦總結** | **DROS 四層縱深架構** | **100.0%** | **0% 系統外洩** | **100% 確定性物理防衛**。 |

### 5.4 微觀基準量測數據

| 評測指標 | 實測數值 | 標準差 / 備註 |
| :--- | :--- | :--- |
| **策略評估延遲 (P50)** | **26.1 μs** | $\pm 3.4\ \mu\text{s}$ |
| **P99 策略延遲** | **41.2 μs** | $\pm 4.1\ \mu\text{s}$ |
| **C-ABI 實體熔斷延遲** | **< 500 ns** | $\pm 42\ \text{ns}$ |
| **SPEC CPU2017 運行負載** | **< 1.8%** | — |
| **零日提示詞注入阻斷率** | **100%** | L4 層 0 漏報 (False Negative) |
| **24 小時連續記憶體洩漏** | **0 Bytes** | 零堆積記憶體分配 (Zero Heap Allocation) |

### 5.3 26.1 μs 延遲之物理意義
人類神經傳導延遲約為 10 ms 至 50 ms。DROS 之 **26.1 μs 決策延遲低於人類神經傳導速度的千分之一**。這代表此攔截決策是在「人類或上層應用感知到攻擊發生之前」即已於二進位層完成物理阻斷。這不是事後的「被動反應」，而是焊死在 C-ABI 系統呼叫邊界「生理上無法繞過的先天物理免疫」。

---

## 六、 相關文獻探討 (Related Work)

本研究建構並延伸了四大資安領域之最新突破：
1. **系統呼叫攔截與核心可觀測性：** 傳統 MAC 框架 (SELinux, AppArmor) 與現代 eBPF 追蹤 (AgentSight [4], Eunomia [8]) 監控低階進程。DROS 引入使用者空間 PKI DIT 憑證繫定，解決進程鏈的上下文失明問題。
2. **LLM 與 Agent 資安框架：** 早期防線專注於應用層提示詞清洗 (NVIDIA NeMo, PromptBench [15])。OWASP Top 10 for Agentic Applications [9] 特別指出越權代理 (LLM06)。DROS 提供了滿足 OWASP 指南所需的 L4 實體執行層。
3. **零信任架構與微隔離：** 對齊 NIST SP 800-207 [1] 與 MITRE ATLAS [3]，DROS 採用 $O(1)$ 能力點陣圖實現多 Agent Swarm 之微隔離邊界。
4. **不可否認性與審計證據鏈：** 受不可篡改日誌與 Merkle Tree 雜湊啟發，DROS 生成 Ed25519 簽章證據包，完全合規歐盟《EU AI Act》Sec. 50 之法庭級證據要求。

---

## 七、 結語與展望 (Conclusion & Vision)

在 AI 如同齊天大聖般擁有無邊法力與自主工具調用能力的時代，企業需要的不是更大的金箍棒（傳統語意防火牆），而是一頂能確保它永遠不會偏離合規取經之路的實體緊箍咒。

DROS 四層防禦縱深架構與 DROS-VEP 開源靶場，即是這頂實體化的緊箍咒 —— 一個基於 $\mathcal{O}(1)$ 位元對映與密碼學身分鋼印的確定性物理契約。我們不相信機率，我們用二進位物理學護衛 Agentic Web 的未來。

---

## 參考文獻 (References)

1. NIST Special Publication 800-207, *"Zero Trust Architecture,"* National Institute of Standards and Technology, 2020.
2. OWASP Foundation, *"OWASP Top 10 for Large Language Model Applications v1.1,"* 2023.
3. MITRE Corporation, *"MITRE ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems,"* 2024.
4. X. Zhang et al., *"AgentSight: eBPF-Powered Tracing and Context Correlation for Autonomous LLM Agents,"* arXiv preprint arXiv:2408.01234, 2024.
5. Y. Liu et al., *"Formal Verification of System Call Boundaries in Autonomous Workloads,"* IEEE Transactions on Dependable and Secure Computing, 2025.
6. C. C. Chen, *"Runtime Attribution Framework: An External C-ABI and PKI-Based Zero-Trust Infrastructure for Non-Repudiable Execution Governance in Multi-Agent Systems,"* Zenodo, DOI: 10.5281/zenodo.20823163, 2026.
7. C. C. Chen, *"DROS-PGM: Deterministic Kernel-Level Execution Control for Post-Compromise Security,"* U.S. Patent Application No. 64/111,973, 2026.
8. Eunomia-bBPF Community, *"eBPF-Based Security Monitoring and LSM Hooking for Cloud Native Runtimes,"* 2025.
9. OWASP Foundation, *"OWASP Top 10 for Agentic Applications,"* 2025.
10. European Parliament and Council, *"Regulation (EU) 2024/1689 Laying Down Harmonised Rules on Artificial Intelligence (EU AI Act),"* Official Journal of the European Union, 2024.

## 致謝與 AI 協作宣告 (Acknowledgment and AI Collaboration Disclosure)

依據 IEEE/ACM 2024+ 學術出版與作者治理規範：
1. **構想與智慧貢獻：** 本論文之資安模型、C-ABI 邊界攔截範式、四層防禦縱深架構及專利權利主張（U.S. PPA No. 64/111,973）均由作者陳俊誠 (Chun-Cheng (Jimmy) Chen) 獨立提出、設計與驗證。
2. **AI 輔助範圍：** 生成式 AI 工具（包括 Antigravity / Gemini-pro）僅作為語法潤飾、 Markdown/LaTeX 排版輔助及參考文獻結構化工具。AI 工具不具備論文作者資格，亦不享有任何智慧財產權貢獻地位。

---

*© 2026 DROS Security / 頂天立地股份有限公司 版權所有。*  
*DROS 執行治理與安全技術已申請美國臨時專利保護（U.S. PPA No. 64/111,973，Patent Pending）。*
