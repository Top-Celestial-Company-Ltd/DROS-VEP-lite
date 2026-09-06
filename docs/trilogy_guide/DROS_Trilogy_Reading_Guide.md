# DROS 學術研究軌跡全景導讀 (The 6-Paper Program)
## Reading Guide to the DROS Research Trajectory: An Agent Runtime Operation Substrate

**作者 / Author：** 陳濬程 (Chun-Cheng Chen)  
**機構 / Affiliation：** 康宸園有限公司 (Top-Celestial Company Ltd.)  
**類型 / Type：** Technical Note / Reading Guide（非取代各篇正式全文）  
**對應六大核心論文與研究艙 / The 6-Paper Program & Evaluation Vessel：**

1. **DROS-6P** — 閉環企業級 AI Agent 六大信任邊界之確定性執行期治理架構  
   DOI: [10.5281/zenodo.21833970](https://doi.org/10.5281/zenodo.21833970)

2. **DROS（四層）v3** — 彌合自主 AI 負載中「代理人至執行歸因鴻溝」之四層確定性執行期作業系統  
   DOI: [10.5281/zenodo.22092008](https://doi.org/10.5281/zenodo.22092008)

3. **DROS-PGM** — 基於內核級運行期安全之確定性執行控制平面（Post-Compromise）  
   DOI: [10.5281/zenodo.21903687](https://doi.org/10.5281/zenodo.21903687)

4. **DROS-WebMCP** — 針對 Agentic Web 能力暴露之密碼學可歸因執行治理層（時序閉包與 Nonce 架構）  
   DOI: [10.5281/zenodo.22290238](https://doi.org/10.5281/zenodo.22290238)

5. **Post-Compromise Mobile** — 針對自主行動代理人之執行期衰減與攜帶證明授權架構（投遞 IEEE TMC）  
   DOI: [10.5281/zenodo.22253147](https://doi.org/10.5281/zenodo.22253147)

6. **Post-Compromise UAV** — 具身智能實體 AI 物理動作權限之確定性執行期強制（投遞 IEEE TAES）  
   DOI: [10.5281/zenodo.22254372](https://doi.org/10.5281/zenodo.22254372)

**統一評測研究艙 / Evaluation Vessel：**  
[DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite)（RFC-001 可重現驗證與評測平台，Apache 2.0）

---

### 🌟 語意與認知層前傳（Semantic & Epistemic Governance Track）：
* **DROS 創始奠基篇** — 約束即代碼：基於佛教判教與物理熔斷的確定性 LLM 治理 (*Constraint-as-Code: Deterministic LLM Governance via Buddhist Doctrinal Classification and Physical Circuit Breaking*)  
  DOI: [10.5281/zenodo.20823227](https://doi.org/10.5281/zenodo.20823227)  
  *提出 Constraint-as-Code 與金剛合約 (Vajra Contract)，首創透過 C-FFI 物理熔斷 (Thread Panic) 根絕 LLM 幻覺。*

* **DROS v7.3 (DOR 框架)** — 確定性本體路由框架用於領域受限的 LLM 系統：DROS v7.3 的設計與實現 (*Deterministic Ontological Routing Framework for Domain-Restricted LLM Systems*)  
  DOI: [10.5281/zenodo.20776075](https://doi.org/10.5281/zenodo.20776075)  
  *專職解決特定高精密度領域內部之「確定性本體路由、宗派顯現隔離與百萬字文本解耦」。*  
  開源代碼庫 / Repository: [Dharma-Reasoning-Operating-System](https://github.com/Top-Celestial-Company-Ltd/Dharma-Reasoning-Operating-System)

---

### 🛡️ 執行治理奠基與原型驗證（Execution Foundations & Empirical Archetypes）：
* **歸責與身分奠基篇** — 智能體運行期歸責框架：多智能體系統中基於外部 C-ABI 與 PKI 零信任的不可否認性執行治理基礎設施 (*Runtime Attribution Framework: An External C-ABI and PKI-Based Zero-Trust Infrastructure for Non-Repudiable Execution Governance in Multi-Agent Systems*)  
  DOI: [10.5281/zenodo.20823163](https://doi.org/10.5281/zenodo.20823163)  
  *提出執行身分證書（BEC）與 Ed25519 簽章，首創以二進位 C-ABI 消除傳統 eBPF 的「情境盲視」，奠定 DROS-6P 之 Principal 與 Audit Log 法庭級證據鏈始祖。*

* **雙重隔離原型篇** — 防護指令污染與幻覺危害的 DROS：VajraAgent 與 VajraClaw 的執行治理基礎設施 (*Neutralizing Prompt Injection and LLM Hallucinations: The Deterministic Sandboxing of VajraAgent and VajraClaw*)  
  DOI: [10.5281/zenodo.20823189](https://doi.org/10.5281/zenodo.20823189)  
  *首次提出 Vajra 體系（金剛智能體 + 金剛爪），實測 1,000 筆對抗樣本：FSM 阻斷 98.5%，繞過語意的 1.5% 精緻攻擊在 C-FFI 邊界 100% 物理熔斷，為 DROS 4-Layer 漏斗與 PGM 微核心的實證原型。*

---

### 1. 本導讀的目的

DROS 系列不是互相孤立的短文，而是涵蓋**「語意層認知約束」**與**「執行層物理強制」**的完整治理全景：

- **語意層治理（DROS v7.3 / DOR）**：解決模型*生成內容（Content）*的幻覺控制、本體拓撲映射與語意對齊；
- **執行層治理（6-Paper 主軸）**：解決 Agent *對外動作（Action）*的二進位邊界、權限熔斷、網路暴露與動能硬約束。

本導讀說明兩大軌道與六大維度如何分工、建議閱讀順序、合起來的系統定位，以及**保證範圍的邊界**。正式技術主張、實驗協議與證明以各篇全文為準。

---

### 2. 一句話定位

> **DROS 是面向自主 AI 工作負載的確定性執行期治理基板（runtime governance substrate），在 Agent 所產生的意圖與具有效果的實際執行（effectful execution）之間建立可強制的控制邊界。**  
> 語意層引導知識路由與認知對齊（DOR）；執行層在共用邊界上確定性允許或拒絕有效果之動作，並留下可驗證存證。

類比 POSIX：POSIX 並未消除應用複雜度，而是避免每個應用重造底層介面。DROS 對 Agent 治理採同一抽象原則——上層不必重造身份、授權、工具邊界、門閥、審計與撤銷的整套機制。

此類比描述的是**架構角色**，並非宣稱 DROS 取代 Linux／Windows 等通用作業系統。

---

### 3. 研究分工與架構全景一覽

| 軌道 / 論文 | 核心問題 | 在系統中的角色 |
|-------------|----------|----------------|
| **語意奠基：判教與物理熔斷** | 如何將深奧教義轉化為硬性代碼？如何透過 CPU 級物理熔斷根絕模型幻覺？ | **思想奠基與執行期熔斷**：佛教判教（Doctrinal Classification）轉化、Constraint-as-Code、金剛合約 (Vajra Contract)、C-FFI 二進位 Thread Panic 熔斷 |
| **語意架構：DROS v7.3 (DOR)** | 如何在高複雜度專業知識領域中，徹底控制 LLM 生成幻覺並防範跨宗派語意漂移？ | **語意與認知層治理**：扁平文本解耦、確定性本體路由 (DOR)、宗派顯現 (Manifestation) 隔離與嚴格引用驗證 |
| **歸責奠基：Runtime Attribution** | 如何解決多 Agent 協同中 eBPF 等傳統工具的情境盲視？如何實現不可否認之司法級歸責？ | **身分與不可否認歸責始祖**：提出執行身分證書 (BEC) 與 Ed25519 簽章，奠定 6P 之 Principal 執行護照與法庭級證據鏈 |
| **隔離原型：VajraAgent & VajraClaw** | 語意過濾與二進位邊界如何協同？繞過語意的攻擊能否在 C-FFI 邊界 100% 熔斷？ | **雙重隔離實證原型**：Vajra 體系（FSM 狀態機 + 金剛爪），1,000 筆對抗測試證偽，為 4-Layer 漏斗與 PGM 核心原型 |
| **DROS-6P** | 企業級 Agent 落地必須回答的六大信任問題是否在同一執行期閉環中被強制？ | **需求與服務規格**：Principal、Authorization、Tool/Action Bound、Policy Gate、Audit Log、Expiry/Revocation（6P） |
| **DROS 四層 v3** | 為何僅有語義防火牆或僅有 OS 級沙箱仍不足？如何填補「代理人至執行歸因鴻溝」？ | **核心機制**：L1→L4 漏斗；L4 於 C-ABI／FFI 邊界做 O(1) 能力點陣圖強制；消融與（v3）對應用層治理中介之對照 |
| **DROS-PGM** | 身份已過或進程已遭劫持後，執行層能否仍提供確定性關管？ | **Post-Compromise 執行信任**：強調執行與偵測之間的時間差、高併發帶內存活與內核視角的控制平面 |
| **DROS-WebMCP** | 當 Web 邁向 Agentic Web，如何防範 WebMCP 工具能力被越權調用並確立不可否認歸因？ | **網絡能力暴露治理**：DWGR-8 規約、W3C 委託鏈、微觀動作綁定與 Commit-Phase Nonce 時序閉包 |
| **Mobile (TMC)** | 換成智慧手機，execution authority 在 OS/API 上還成立嗎？ | **數位系統實證**：行動作業系統特權 API（相機/通訊錄/位置）之運行期衰減與帶證明授權 |
| **UAV (TAES)** | 如果最後效果是「真的動起來」，物理動能邊界還能約束嗎？ | **具身物理實證**：無人載具在攻陷後之動能包絡線保持與前瞻煞車視界硬約束 |

**建議閱讀順序：**  
* **治理思想起源與認知對齊**：**判教與物理熔斷 (創始篇) → DROS v7.3 (DOR 框架) → 四層 v3 (L1/L2 語意過濾)**  
* **執行治理奠基與原型演化**：**Runtime Attribution (歸責篇) → VajraAgent & VajraClaw (雙重隔離原型) → 6P → 四層 v3**  
* **企業治理與組織合規**：**6P → 四層 v3 → WebMCP**  
* **系統底層與二進位安全**：**VajraClaw 原型 → 四層 v3 → PGM → Mobile**  
* **具身智能與控制工程**：**PGM → UAV**

---

### 4. 合起來的架構圖像

```text
               業務 Agent / 多 Agent / Agentic Web
                                │
                ┌───────────────┴───────────────┐
                │                               │
             Ingress                         Egress
      （資料／特徵入口）               （有效果動作出口）
                │                               │
                └───────────────┬───────────────┘
                                ▼
        ┌───────────────────────────────────────────────┐
        │        DROS 執行期治理基板（本系列）           │
        │  · 6P 核心服務（6P 論文）                      │
        │  · L1–L4 機率→確定性漏斗（四層論文）          │
        │  · Post-Compromise 執行信任（PGM）            │
        │  · 開放身份憑證 + 在地執行強制                │
        └───────────────────────┬───────────────────────┘
                                │ 僅 ALLOW 的動作
                                ▼
                傳統 OS / 網路 / 檔案 / 外部 API
```

對應用層而言，理想上只需穩定經過治理入口與出口；DIT、能力點陣圖、Merkle 審計、RCU 撤銷等複雜度由基板承擔。對跨域 Agentic Web，系列採「**開放身份、在地治理**」：憑證可流通，執行權仍由資源擁有者在邊界強制。

與應用層 Agent 治理中介（例如政策 SDK／工具包）的關係，四層論文 v3 概括為互補：

> **They decide. DROS enforces.**  
> （應用層可做宣告與決策；未託管的執行路徑仍需二進位／FFI 邊界的確定性強制。）

---

### 5. 6P：Agent 執行期的「核心服務表」

| 維度 | 問題 | 典型機制方向（詳見 6P 全文） |
|------|------|------------------------------|
| **Principal** | 代表誰？ | 密碼學執行令牌／護照（DIT 等） |
| **Authorization** | 允許做什麼？ | 能力點陣圖等確定性授權向量 |
| **Tool/Action Bound** | 哪些呼叫能出去？ | C-ABI／FFI（及相關）帶內攔截 |
| **Policy Gate** | 高風險如何控？ | 遮蔽、HITL、選擇性揭露等 |
| **Audit Log** | 如何不可抵賴追溯？ | 雜湊鏈／簽章存證 |
| **Expiry/Revocation** | 如何立刻失效？ | 原子更新／熱切換至拒絕態 |

系列主張：若自主 Agent 要在受監管環境中成為可歸責的執行主體，上述六維應視為**治理完備的最低操作基準**，而非可任意省略的外掛功能。

---

### 6. 實證與可重現性（如何讀數字）

各篇報告之延遲、阻擋率、消融比例與對照實驗，均綁定**已定義威脅模型、評估語料與量測段落**。閱讀時請注意：

- **策略評估延遲**（例如約 $26\,\mu\mathrm{s}$ 量級）與 **C-ABI 強制路徑延遲**（例如 $<500\,\mathrm{ns}$ 量級）可能量測不同程式段落，不宜混為同一端到端數字。  
- **「100% 阻擋」等表述應讀作：在該篇所宣告之威脅模型與已評估語料／配置下**的結果，而非對任意原生程式碼或內核已被攻破情境的無條件保證。  
- 可重現材料以各篇所載測試床與開源倉庫為準（含 DROS-VEP-lite）。

四層論文中的消融實驗，其架構意義在於：在所述配置下，缺少 L4 時仍可能有對抗性混淆負載進入未授權執行；L4 提供執行層的確定性防線。此點支撐「語義防禦與執行邊界強制不可互相取代」的論題。

---

### 7. 保證範圍（必讀）

本系列提供的是**執行期治理與執行邊界強制**方向的架構與實證，而非：

- 模型對齊或「模型永不產生有害意圖」的保證；  
- 對任意未登記原生程式碼路徑、或作業系統內核已被攻破的保證；  
- 對「授權範圍內濫用」（動作在允許集合內但業務上不當）的自動道德判斷；  
- 完整法律合規認證（技術存證可支持審計，合規仍需組織與程序控制）。

各篇「威脅模型／局限性／TCB」章節具有約束力；本導讀不擴大各篇已寫明的保證範圍。

---

### 8. 給不同讀者的路徑

| 讀者 | 建議 |
|------|------|
| **架構師／技術決策** | 本導讀 → 6P 摘要 → 四層架構圖與論題 |
| **Web 與 MCP 開發者** | DROS-WebMCP（DWGR-8 規約與時序閉包） → 四層架構 |
| **資安／風險** | 四層威脅模型與消融 → PGM（Post-Compromise） → Mobile |
| **具身智能／控制工程** | PGM（二進位熔斷） → UAV（物理動能包絡線約束） |
| **工程實作** | VEP-lite 與四層實作／評測章節 |
| **研究者** | 六篇全文 + Related Work；注意與應用層語義防護方案的層級區分 |

---

### 9. 版本與引用

引用技術主張時，請引用**各核心論文 DOI**，而非僅引用本導讀。本導讀僅供導航與定位。

若系列論文更新版本，以 Zenodo 上各 record 之最新 version 與各 PDF 正文為準；本導讀將隨重大架構表述變更而修訂。

---

### 10. 結語

本系列將 Agent 執行期治理收斂為可描述、可驗證、可討論部署的一層基板：  
**6P 定義服務完備性，四層定義執行邊界上的確定性強制，PGM 將同一執行信任延伸至妥協後情境，WebMCP 解決 Agentic Web 網絡歸因閉包，Mobile 與 UAV 則分別在數位作業系統與實體具身智能確立了物理防線。**

讀者若只能記住一句：

> **Agent 要安全落地，需要的不只是更乖的模型，而是對「有效果動作」不可繞過的確定性治理基板。**  

那一層，即為 DROS 系列論文共同界定與驗證的對象。
