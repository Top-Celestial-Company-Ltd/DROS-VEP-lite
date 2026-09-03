# DROS-6P：針對企業級 AI Agent 六大信任邊界的確定性執行期治理架構

**投稿會議：** IEEE International Conference on Autonomic / Autonomous Systems (IEEE ICA 2026)  
**投稿類別：** Regular Paper（雙盲匿名審查）  
**研究領域：** AI Agent 資安、執行期系統治理與自律計算  

---

## 摘要

自主型 AI Agent 正日益被委託處理關鍵企業工作流程，但其內部推理本質上屬於在不可信上下文上的概率性運作。傳統依賴身分驗證或應用層過濾的防禦機制，一旦惡意操作來自於合法憑證持有者，即無法區分合法與遭劫持的行為，造成了根本性的**「語意—執行治理斷層（Semantic-Execution Governance Gap）」**。

本文提出 **DROS-6P**，這是一個圍繞六大互補信任邊界構建的帶內確定性執行期治理架構：主體身分（$P_1$）、能力授權（$P_2$）、工具/動作邊界（$P_3$）、策略閘門（$P_4$）、防篡改審計（$P_5$）以及動態撤銷（$P_6$）。本架構嚴格將 Agent 的「意圖層」與「執行權限」解耦，並透過二進位 C-ABI 邊界仲介所有受保護的操作。能力授權採用常數時間 $O(1)$ 的 64 位元能力點陣圖比對，動態策略撤銷則採用無鎖 RCU（Read-Copy-Update）原子狀態指針切換（$T_{\text{swap}} \approx 420\text{ ns}$）。

我們形式化了兩大執行治理不變量：**未授權執行硬封鎖**（$\text{DENY} \implies \text{Exec} = 0$）與**執行至證據完整性**（$\text{Exec} = 1 \implies \text{Audit} = 1$）。在涵蓋 160,611 次連續請求的 72 小時浸泡壓力評測中（包含 137,751 次策略執行探測與 22,860 次良性對照），系統展現了 $26.21\ \mu\text{s}$ 的中位數決策延遲與 $242.69\ \mu\text{s}$ 的 P99 延遲。在預定義的紅隊對抗情境與六大異質產業測試軌道中，於所評估的涵蓋空間內均觀測到零未授權物理狀態轉變。實證結果支持將帶內確定性仲介作為企業級 AI Agent 執行期治理的實踐基礎。

**關鍵字：** AI Agent 資安、執行期治理、六大信任邊界、C-ABI 邊界執行、RCU 無鎖切換、執行至證據不變量。

---

## 一、 緒論 (Introduction)

自主型 AI Agent 正廣泛部署於企業的核心運算場景中，例如金融總帳管理、客戶關係自動化與軟體持續部署。與傳統具備確定性控制流的軟體服務不同，自主 Agent 是依據大型語言模型（LLM）在不可信外部上下文上的概率性推理，動態生成工具呼叫指令。

### 1.1 語意—執行治理斷層 (The Semantic-Execution Governance Gap)
現代企業防禦架構在治理自主 Agent 工作負載時面臨根本性的架構分裂：
1. **應用層語意防火牆（Semantic Firewalls）：** Prompt 檢查器、輸出分類器與 JSON Schema 驗證器主要檢查自然語言 Token，但缺乏物理執行邊界的硬約束力；直譯器逃逸、混淆參數與多輪上下文投毒均能繞過概率性過濾。
2. **作業系統核心沙箱（Kernel Sandboxes）：** 底層 OS 原語（如 Linux Seccomp、Namespaces、eBPF）執行二進位系統呼叫過濾，但缺乏應用層的語意上下文。它們無法分辨特定資料庫寫入操作是由合法的財務 Agent 所發起，還是由同一 Worker 行程內被劫持的客服 Agent 所發起。

當 Agent 因間接提示詞注入（IPI）或目標劫持而遭操控時，攻擊者是**從已驗證的安全邊界內部**發起操作，使傳統 IAM 與周界防禦完全陷入上下文失明。我們稱此為**「Agent 至執行歸因斷層（Agent-to-Execution Attribution Gap）」**。

### 1.2 研究命題與核心貢獻 (Thesis & Contributions)
DROS-6P 的核心命題在於：有效的執行期治理必須將以往分散於不同層級的六大信任邊界，**架構性地統合於同一個執行邊界（Execution Boundary）**，使授權決策能直接確定性地約束物理執行，並產生相應的密碼學存證。

本文主要貢獻包括：
1. **六大信任邊界模型（Six Trust Boundaries Model）：** 形式化定義了封閉 Agent 執行六大本質問題的治理模型（$P_1$--$P_6$），結構化為 DROS-6P 框架。
2. **確定性帶內執行底座（Deterministic In-Band Substrate）：** 提出將 Agent 意圖與執行權限解耦的架構，在二進位 C-ABI 邊界實施 $O(1)$ 點陣圖比對與 RCU 原子指針切換（$T_{\text{swap}} \approx 420\text{ ns}$）。
3. **形式化不變量實證（Empirical Invariant Evaluation）：** 在 72 小時連續浸泡評測（160,611 次請求）與六大異質產業測試軌道中，驗證了在所評估的測試空間內達成零未授權物理執行與 100% 審計鏈完整性。

---

## 二、 六大信任邊界模型 (The Six Trust Boundaries, P1–P6)

為了提供全生命週期的執行治理，執行底座必須持續對 Agent 的每一個實質操作進行六個互補維度的仲介，為可信自主 Agent 建立結構化的操作基準：

```text
              不可信上下文輸入 (Untrusted Context)
                              │
                              ▼
                      ┌───────────────┐
                      │  意圖推理平面 │ (LLM 概率性推理與工具呼叫提案)
                      │ (Intent Plane)│
                      └───────┬───────┘
                              │
                         工具調用請求
                              │
                              ▼
        ╔════════════════════════════════════════════════╗
        ║          DROS-6P 執行治理邊界 (C-ABI)          ║
        ║                                                ║
        ║  P1 主體身分 (Principal)   ──► DIT 密碼學驗證  ║
        ║  P2 能力授權 (AuthZ)       ──► 64-bit 點陣圖   ║
        ║  P3 工具邊界 (Tool Bound)  ──► Schema 參數防護 ║
        ║  P4 策略閘門 (Policy Gate) ──► 帶內 PEP/PDP    ║
        ║  P6 動態撤銷 (Revocation)  ──► RCU 原子交換    ║
        ║                                                ║
        ║                       │                        ║
        ║                 確定性執行決策                 ║
        ║                       │                        ║
        ║  P5 審計證據 (Audit Log)   ──► SHA-256 哈希鏈  ║
        ╚═══════════════════════╤════════════════════════╝
                                │
                         放行   │ 拒絕 (<500 ns)
                                ▼
                         物理世界執行 (資料庫、Socket、Syscall)
```

* **P1: 主體身分 (Principal Identity - 誰在行動？)：** 建立 Agent 實例與短期身分憑證（`DrosIdentityToken`, DIT）的密碼學繫定，內含代理識別碼與 Ed25519 數位簽章。
* **P2: 能力授權 (Authorization - 允許做什麼？)：** 64 位元能力點陣圖，精準編碼允許的操作類別，消除通用 Worker 的上下文失明。
* **P3: 工具邊界 (Tool/Action Bound - 呼叫哪個工具與參數？)：** 對工具呼叫請求與參數進行正規化校驗與宣告式 Schema 邊界過濾。
* **P4: 策略閘門 (Policy Gate - 依據何種策略？)：** 帶內策略決策點（PDP）與策略執行點（PEP），實施微秒級確定性檢查。
* **P5: 審計存證 (Audit Log - 存在何種可驗證證據？)：** 連續 SHA-256 哈希鏈式執行日誌，提供具備密碼學完整性與防篡改性的存證。
* **P6: 時效撤銷 (Expiry & Revocation - 權限是否仍然有效？)：** 紀元（Epoch）時間邊界結合無鎖 RCU 原子指針切換，達成有界延遲的策略狀態撤銷。

---

## 三、 確定性執行期強制架構 (Enforcement Architecture)

### 3.1 意圖與執行平面解耦
DROS-6P 在「意圖平面（LLM 推理與工具呼叫格式化）」與「執行平面（物理系統呼叫、網路連線、資料庫寫入）」之間實施強制隔離。應用層 Worker 行程無法直接調用受保護的底層資源，所有請求必須穿透二進位 C-ABI 閘門。

### 3.2 C-ABI 能力點陣圖評估 ($O(1)$)
為防止多 Agent 高併發場景下的延遲放大，授權策略預先編譯為不可變的 64 位元點陣圖：
$$\text{Decision} = \begin{cases} \text{PERMIT}, & \text{若 } (\text{Mask}_{\text{agent}} \land \text{Mask}_{\text{req}}) == \text{Mask}_{\text{req}} \\ \text{DENY}, & \text{否則} \end{cases}$$
若請求的能力位元未被置位，執行點立即硬中斷。隔離環境下的二進位拒絕路徑原語耗時實測小於 $500\text{ ns}$（不含輸入解析、DIT 驗證與審計鏈寫入）。

### 3.3 RCU 原子狀態撤銷 ($T_{\text{swap}} \approx 420\text{ ns}$)
動態策略更新與緊急資安撤銷透過 Read-Copy-Update (RCU) 執行：
$$\text{AtomicPtr.swap}(\&P_{\text{active}}, P_{\text{new}}, \text{Ordering::Release})$$
指針交換原語耗時約為 $420\text{ ns}$。原子狀態轉換線性化（Linearized）之後，後續的所有授權檢查皆能立即觀測到更新後的策略狀態。

### 3.4 雙向執行治理不變量 (Dual Execution Invariants)
令 $Auth_E(x) = f(P_1, P_2, P_3, P_4, P_6)$ 為綜合計算後的有效授權決策。**請注意：$P_5$（審計日誌）在架構上故意不納入 $Auth_E$ 的計算輸入，因為審計是「證據邊界」而非「授權輸入」**，其職責在於約束成功執行的證據完整性。

本架構在被評估的覆蓋空間 $X_{\text{covered}}$ 內強制保證兩大數學不變量：
$$\text{硬封鎖不變量 (Containment Invariant):} \quad \forall x \in X_{\text{covered}}, \; Auth_E(x) = \text{DENY} \implies Exec(x) = 0$$
$$\text{證據完整不變量 (Evidence Invariant):} \quad \forall x \in X_{\text{covered}}, \; Exec(x) = 1 \implies Audit(x) = 1$$
其中 $Exec(x) = 0$ 代表該操作在物理世界產生零副作用；$Audit(x) = 1$ 代表事件已寫入密碼學鏈式結構並通過完整性校驗。

---

## 四、 實驗方法與實體測量 (Experimental Methodology)

### 4.1 評測硬體與系統配置
所有基準測試均在隔離的容器化評測環境中進行：

| 參數維度 | 實體機與虛擬機規範 |
| :--- | :--- |
| **宿主機處理器 (Host CPU)** | Intel(R) Xeon(R) CPU E3-1275L v3 @ 2.70GHz (4核/8緒) |
| **宿主機記憶體 (Host RAM)** | 16 GB Dual-Channel DDR3 RAM |
| **宿主機作業系統 (Host OS)** | Windows 10 Enterprise LTSC (Build 19044, 64-bit) |
| **評測虛擬機 (Guest VM)** | Ubuntu 22.04 LTS (Linux Kernel 5.15 / Docker 24.0) |
| **執行引擎 (Execution Engine)**| DROS-6P In-Band Daemon (多執行緒 C-ABI) |
| **容器基準環境 (Baseline)** | Python 3.11 Runtime / 隔離 Linux Container |

### 4.2 測量邊界定義
端到端決策延遲 $t_{\text{decision}}$ 明確定義為五個構成階段之和：
$$t_{\text{decision}} = t_{\text{ingress}} + t_{\text{DIT\_verify}} + t_{\text{bitmask}} + t_{\text{audit\_chain}} + t_{\text{egress}}$$
使用高解析度單調時鐘（`perf_counter_ns`）在 1 至 50 個併發 Worker 執行緒下，對 160,611 次連續請求進行精確採樣。

---

## 五、 實證結果與壓力評測 (Empirical Results)

### 5.1 72 小時連續浸泡評測 ($N = 160,611$)
在 72 小時連續多情境負載中，系統處理了 160,611 次請求（137,751 次越權探測，22,860 次良性對照）：

| 指標類別 | 實測參數 | 觀測數值 |
| :--- | :--- | :--- |
| **延遲指標 (Latency)** | 端到端決策中位數 (P50) | $26.21\ \mu\text{s}$ |
| | 端到端決策 P95 延遲 | $38.45\ \mu\text{s}$ |
| | 端到端決策 P99 延遲 | $242.69\ \mu\text{s}$ |
| | 隔離二進位拒絕原語 | $< 500\text{ ns}$ |
| **資源穩定度 (Stability)** | 常駐記憶體 (RSS) 增長 | **$0\text{ MB}$（無可觀測增長）** |
| | 行程崩潰 / Panic 次數 | **0 次** |
| **安全不變量 (Invariants)**| 未授權物理操作次數 | **$0 / 137,751$** |
| | 審計哈希鏈完整性驗證 | **100% 通過** |

### 5.2 與無防禦基準組對比 (Direct Baseline Comparison)
在五大預定義威脅情境（ATS-001 至 ATS-005）中，直接執行基準組在每次測試中均產生了未授權物理狀態轉變（100% 淪陷），而 DROS-6P 達成了完全阻斷（0% 淪陷）：

| 情境編號 | 對抗型威脅描述 | 直接執行基準組 (Direct Baseline) | DROS-6P 治理 |
| :--- | :--- | :---: | :---: |
| **ATS-001** | 間接提示詞注入 (IPI) | 100% 淪陷 (Breach) | **0% 淪陷 (Contained)** |
| **ATS-002** | 敏感資料竊取與外洩 | 100% 淪陷 (Breach) | **0% 淪陷 (Contained)** |
| **ATS-003** | 未授權生產環境部署推播 | 100% 淪陷 (Breach) | **0% 淪陷 (Contained)** |
| **ATS-004** | B2B 跨企業供應鏈投毒 | 100% 淪陷 (Breach) | **0% 淪陷 (Contained)** |
| **ATS-005** | 遭劫持後系統呼叫逃逸 | 100% 淪陷 (Breach) | **0% 淪陷 (Contained)** |

### 5.3 六大異質產業應用軌道驗證 (Heterogeneous Industry Tracks)
在製造業、金融洗錢防制、醫療隱私（PHI）、電子政務、金融科技帳戶接管與供應鏈跨租戶等六大軌道共 600 次獨立測試中，未授權物理狀態轉變次數均為 **0 / 100**。

---

## 六、 相關研究與學術定位 (Related Work & Novelty)

本架構與五大現有資安領域建立明確邊界與定位：
1. **LLM Guardrails（NVIDIA NeMo, Microsoft Agent Framework）：** 專注於語意過濾，但屬於概率性防禦，缺乏底層執行約束。
2. **能力型存取控制（Capability Systems - Dennis & Van Horn 1966, Levy 2014）：** DROS-6P 將經典能力理論擴展至自主 Agent，實作為常數時間的 64 位元點陣圖。
3. **系統呼叫核心追蹤（AgentSight eBPF）：** 純 OS 追蹤缺乏應用層 Agent 身分歸因上下文。
4. **資訊流控制與 Provenance（TaintDroid, PASS 2006）：** DROS-6P 將動態資料脫敏與防篡改哈希鏈日誌相結合。
5. **零信任負載身分（SPIFFE/SPIRE, NIST SP 800-207）：** DROS-6P 將工作負載身分融入短生命週期的工具調用治理中。

**核心學術定位（Novelty）：** 現有系統通常在不同的架構層級分別處理單一邊界；DROS-6P 的核心貢獻在於**將六大信任邊界（$P_1$--$P_6$）直接統合於「請求轉化為物理操作」的二進位執行邊界**，確保確定性約束與證據完整性。

---

## 七、 結論 (Conclusion)

本文提出了 DROS-6P，一個封閉企業級 AI Agent 六大本質信任邊界的帶內確定性執行期治理架構。透過在二進位 C-ABI 邊界強制執行 64 位元能力點陣圖，並以 RCU 指針切換（$T_{\text{swap}} \approx 420\text{ ns}$）提供亞微秒級原子撤銷，DROS-6P 成功彌合了語意—執行治理斷層。160,611 次連續請求評測證明了其在所評估空間內的零未授權執行與 100% 審計完整性。

---

## AI 協作宣告 (AI Declaration)

生成式 AI 工具僅用於有限的技術輔助，包括英語語法潤飾與 LaTeX 排版輔助。論文中的概念框架、研究問題、系統架構、形式化不變量、實驗設計、數據詮釋與最終論文 Claim，均由作者獨立確立與驗證。作者對本文之最終內容負全部責任。

---

## 參考文獻 (References)

1. NVIDIA, "NeMo Guardrails: Programmable Guardrails for LLM Applications," *NVIDIA Developer Documentation*, 2024.
2. Microsoft, "Microsoft Agent Framework Documentation: Tool Calling and Execution Governance," *Microsoft Learn*, 2025.
3. X. Zhang *et al.*, "AgentSight: eBPF-Powered Tracing and Context Correlation for Autonomous LLM Agents," *arXiv preprint arXiv:2408.01234*, 2024.
4. J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," *Communications of the ACM (CACM)*, vol. 9, no. 3, pp. 143–155, 1966.
5. H. M. Levy, *Capability-Based Computer Systems*, Digital Press, 2014.
6. W. Enck *et al.*, "TaintDroid: An Information-Flow Tracking System for Real-Time Privacy Monitoring on Smartphones," *ACM Transactions on Computer Systems (TOCS)*, vol. 32, no. 2, pp. 1–32, 2014.
7. K.-K. Muniswamy-Reddy *et al.*, "Provenance-Aware Storage Systems," in *Proc. USENIX Annual Technical Conference (ATC)*, 2006, pp. 43–56.
8. Cloud Native Computing Foundation (CNCF), "SPIFFE: Secure Production Identity Framework for Everyone," *CNCF Standard Specification*, 2020.
9. NIST, "Zero Trust Architecture," *NIST Special Publication 800-207*, 2020.
10. P. E. McKenney, "Is Parallel Programming Hard, And, If So, What Can You Do About It? (Read-Copy Update Architecture)," *Linux Technology Center, IBM*, 2024.
11. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," *OWASP Standard*, 2025.
12. European Parliament, "Artificial Intelligence Act (Regulation EU 2024/1689), Article 50: Transparency and Traceability of AI Systems," *Official Journal of the European Union*, 2024.
