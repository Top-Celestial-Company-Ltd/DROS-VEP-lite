# DROS：自主 AI 軟體系統中確定性權能強制之執行期架構

> **作者：** 陳濬程（Jimmy Chen）  
> **單位：** Top-Celestial Company Ltd.，中華民國臺灣臺北  
> **聯絡：** jimmychen@dr-os.io  
> **ORCID：** 0009-0001-6387-0500  
> **版本：** v4.0 | 2026-08-28  
> **目標期刊：** IEEE Transactions on Software Engineering (TSE)  
> **開源評測庫：** [DROS-VEP-lite](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite) | [DROS-Home-Lab](https://github.com/Top-Celestial-Company-Ltd/dros-home-lab)  

---

## 摘要 (Abstract)

自主 AI 軟體系統日益在共享的應用程式執行期（Runtime）內並發執行多個邏輯代理人、角色與工作流。儘管應用層策略機制能夠區分這些邏輯主體，但傳統的作業系統存取控制通常僅能觀測到外層包裹的進程識別項（PID/UID），無法識別對特定工具調用負有責任的代理人身分。此種不匹配在軟體層授權決策與底層執行強制之間造成了嚴重的歸因鴻溝。

本文提出 **DROS**——一種能夠跨越「應用程式至執行邊界」保持代理人層級歸因的四層執行期架構，並在受管轄操作進入其具體實作前實施確定性權能強制。DROS 結合了語義過濾、密碼學認證的執行身分、拓撲感知之屬性授權，以及基於不可變角色專屬權能點陣圖的 C-ABI/FFI 強制核心。該架構將機率性的上游決策機制與確定性的執行邊界解耦，使後者能夠提供獨立於語義分類準確性的條件執行保證。

我們在涵蓋 160,611 次請求的 24 小時評測中驗證了 DROS，其中包括橫跨提示注入、目標劫持、特權提升與供應鏈攻擊模式的 137,751 次對抗性嘗試。在定義的受管轄執行期邊界下，DROS 對於到達強制邊界的對抗性調用達到了觀測上的 100% 阻斷率，且在 22,860 筆正常請求中的策略誤報率為 0/22,860。下游策略路徑的中位延遲為 26.21 $\mu\text{s}$（P99 延遲為 242.69 $\mu\text{s}$），而獨立的權能檢查平均僅需 825 ns。最小基質極限評測進一步證實在 906 次敵意嘗試中觀察到零未授權權能轉移。

評測結果證實：確定性執行強制可作為自主 AI 軟體系統的一項內建執行期架構特性，而無需單純依賴上游的機率語義防禦。

**關鍵詞** — 軟體架構、自主 AI 系統、執行期強制、權能安全、屬性存取控制、執行監控、實證軟體工程。

---

## 一、引言 (Introduction)

自主 AI 軟體系統正日益結合大型語言模型（LLM）與外部工具、服務、記憶體系統、軟體函式庫及執行環境。這種架構賦予代理人以極少人類干預完成多步驟任務的能力，但也引入了傳統進程層級授權機制無法充分解決的軟體工程難題。

現代代理人執行期常在單一作業系統進程內託管多個邏輯主體。這些主體可能代表不同的代理人、角色、工作流或被委託之任務，同時共享相同的進程身分、位址空間與執行期基礎設施。因此，作業系統授權機制可能正確判定某個進程被允許存取某項資源，卻完全無法判定負責當前具體操作的特定邏輯代理人是否具備該行動的授權。

相對地，應用層策略系統雖具備豐富的情境資訊（能識別代理人、角色、任務、工作流與工具狀態），但其決策唯有在每項安全相關操作均穿透相應的策略強制點時方能生效。這在軟體層歸因與執行層強制之間形成了架構性的落差，我們將此定義為**代理人-至-執行歸因鴻溝（Agent-to-Execution Attribution Gap）**：

> **定義一（歸因鴻溝，Attribution Gap）：** 在共享的執行期身分下，應用層代理人主體與執行層授權決策之間缺乏值得信賴且可驗證的映射關係。當兩個或更多邏輯上不同的授權主體在同一個作業系統安全主體（如共享的 PID/UID）內執行，而底層執行基質在強制邊界上無法以密碼學方式區分其授權狀態時，即存在歸因鴻溝。

本問題不等同於傳統的「困惑代理人（Confused Deputy）」行為 [Hardy 1988]。在經典困惑代理人情境中，特權組件受騙代表非預期請求者行使其特權；而在本研究情境中，更根本的挑戰在於：執行期在「計算授權」與「執行請求操作」這兩個斷點之間，丟失了邏輯主體的身分歸因。

當單一進程託管具備不同權能包絡線的多個代理人時，此區分尤為關鍵。例如，給定包含三個邏輯角色的執行環境：
$$\mathcal{R} = \{r_1, r_2, r_3\}$$
其中 $r_1$ 允許存取資料庫，$r_2$ 允許調用外部網路，而 $r_3$ 均不允許。若三者運行於同一進程內，傳統進程控制僅能觀察到 $\text{PID} = P$，而無法分辨 $(P, r_1), (P, r_2), (P, r_3)$。軟體執行期因此持有無法在執行邊界體現的授權資訊。

如圖 2 所示，這種非對稱性形成了歸因鴻溝：作業系統沙箱僅能看到單一且經授權的宿主進程 PID，而執行期在分派時遺失了邏輯角色身分。DROS 引入了帶內歸因基質，將每次調用綁定至經認證的密碼學身分令牌，使下游參考監視器能夠強制實施角色專屬的權能邊界。

![圖 2：多主體代理人執行期中的代理人-至-執行歸因鴻溝與 DROS 帶內歸因基質。](figures/fig2_attribution_gap.png)

*圖 2：多主體代理人執行期中的代理人-至-執行歸因鴻溝與 DROS 帶內歸因基質。*

DROS 透過在多個執行期層級中傳遞經認證的角色歸因，並在確定性的 C-ABI/FFI 執行邊界終結授權決策，從架構層面解決此難題。

核心架構設計原則：
> **核心論題（Core Thesis）：** 一項先前未授權之執行，絕不應依賴語義決策維持正確才能被阻斷。DROS 建立執行邊界參考監視器，確保代理人規劃層的認知失陷本身絕不會將其執行權限擴展至超出其密碼學綁定的能力包絡線之外。

DROS 藉此將自主代理人架構中常混雜的兩項職能解耦：
1. **決策與情境推理**：可包含機率性組件（如提示詞解析、LLM 推論）；
2. **執行授權**：一旦請求到達受管轄執行邊界，必須具備確定性。

本研究的核心新穎性並非單純的權能控制，亦非單純的密碼學身分，而是將瞬態行程內代理人主體的歸因關係，完整保真地傳遞至二進位執行邊界所做出的授權決策之架構編排。

### A. 研究問題 (Research Questions)
* **RQ1（歸因保真度）：** 代理人層級之身分歸因能否從自主軟體執行期完整傳遞至執行層授權邊界？
* **RQ2（邊界遏制力）：** 當操作繞過上游應用層控制時，確定性權能強制邊界能否有效阻斷未授權執行？
* **RQ3（執行期開銷）：** 附加的執行期強制架構在關鍵熱路徑上引入了多少效能與延遲開銷？
* **RQ4（長期穩定性與爆炸半徑）：** 當上游治理完全崩潰且面對高密度敵意權能轉移時，架構能否維持穩定性與有界爆炸半徑？

### B. 本文貢獻 (Contributions)
1. **執行期架構：** 定義了一種將邏輯代理人歸因從應用層帶入確定性 C-ABI/FFI 強制邊界的四層執行期架構。
2. **確定性執行機制：** 實作了不可變角色專屬點陣圖與 $O(1)$ 授權檢查，在受管轄操作進入實作主體前同步執行。
3. **條件執行安全模型：** 在顯式的完全仲裁、密碼學完整性、策略不可變性與分派完整性假設下形式化證明安全遏制性質。
4. **實證系統工程評測：** 基於 24 小時 160,611 次請求、對抗性突變實驗、跨架構比較與最小基質極限評測驗證架構效能。

---

## II. 系統模型 (System Model)

### A. 執行期模型
我們將自主 AI 軟體系統模型化為邏輯主體集合 $\mathcal{R} = \{r_1, \dots, r_n\}$。每個主體可執行已登記的系統操作 $\mathcal{M} = \{m_1, \dots, m_k\}$。對於每個角色 $r$，DROS 維護授權點陣圖 $B_r \in \{0,1\}^k$。授權關係表示為：
$$\text{Auth}(r, m_i) = B_r[i]$$
當一項操作進入已登記之 DROS 分派邊界時，即被視為**受管轄（Governed）**。該架構明確界定其防護範疇，不宣稱對受管轄基質外的任意未插樁原生代碼具備控制力。

### B. 歸因鴻溝形式化
令 $I_A$ 代表應用執行期所持有的身分，令 $I_E$ 代表執行邊界所能感知的身分。當授權所需之粒度滿足 $I_A \neq I_E$ 時，即存在歸因鴻溝。傳統進程模型中 $I_E = \text{PID}/\text{UID}$，而 $I_A = (\text{agent}, \text{role}, \text{task}, \text{workflow})$。DROS 建立了可驗證的映射：
$$I_A \xrightarrow{} \text{DIT} \xrightarrow{} r \xrightarrow{} B_r$$
使執行決策直接基於邏輯角色而非僅基於宿主進程身分。

---

## III. DROS 執行期架構 (DROS Runtime Architecture)

DROS 由四個解耦層級構成，形成從機率語義推理到確定性二進位執行的架構流水線（如圖 1 所示）：

![圖 1：DROS 控制平面與執行期強制平面架構。](figures/fig1_dros_architecture.png)

*圖 1：DROS 控制平面與執行期強制平面架構。*

### A. 第一層：語義邊界層 (Semantic Boundary)
L1 負責對輸入提示詞與工具調用情境進行前置語意檢查，定位為機率性分類過濾而非確定性授權。設計目標在於以極低成本（$O(\text{tokens})$）過濾大部分已知未混淆的攻擊。在評測語料庫中，L1 過濾了 85.2% 的已知模板 IPI，對混淆攻擊阻擋率為 0%；正常請求誤報率為 0/22,860。其失效模式完全交由 L2--L4 處置。

### B. 第二層：密碼學執行身分層 (Cryptographic Execution Identity)
L2 引入 **DROS 身分令牌（DIT）**：
```
DIT := {
  agent_id:     UUID,
  role_id:      uint32,
  task_id:      UUID,           // 工作流審計與溯源綁定（非授權原語）
  bitmap_hash:  SHA-256(B_r),   // 策略版本同步之密碼學承諾
  issued_at:    Unix timestamp,
  expires_at:   Unix timestamp  // 短 TTL <= 15 分鐘,
  signature:    Ed25519(private_key_AIA, DIT_body)
}
```
**權威來源與密碼學承諾解耦**：DIT 內的 `bitmap_hash` 僅作為密碼學承諾，確保代理人與 GuardVM 參照完全相同的編譯策略紀元；真正的授權權威嚴格源自 GuardVM 防寫頁面中的 $B_r = \text{PolicyStore}[r]$。DIT 必須由獨立信任域的自動簽發機構（AIA）依據驗證的工作流清單簽發，受入侵的代理人進程無法自行鑄造或偽造未授權角色。

### C. 第三層：執行期拓撲與屬性強制層 (Runtime Topology & ABAC)
L3 施加多代理人拓撲與情境屬性約束（有向無環溝通圖、跨部門調用邊界、工作流調用序列、扇出上限及符號化 ABAC 規則），在最終執行邊界之上提供結構化情境治理。

### D. 第四層：確定性執行邊界層 (Deterministic Execution Boundary)
L4 為核心執行機制。每個受管轄操作映射至固定索引 $m_i \xrightarrow{} i$。對於經認證角色 $r$，強制操作為：
$$\text{allow} = B_r[i]$$
決策時間相對於系統工具總數恆為常數（$O(1)$）。完整執行序列為：
$$\text{Verify}(\text{DIT}) \xrightarrow{} \text{Resolve}(r) \xrightarrow{} \text{Load}(B_r) \xrightarrow{} \text{Check}(B_r[i]) \xrightarrow{} \text{Execute}(m_i)$$
若 $B_r[i] = 0$，分派器返回 HTTP 403 授權錯誤，絕不進入 $m_i$ 的實作主體。核心由 Rust 撰寫，透過零堆積 C-ABI 暴露予受管轄執行環境。

---

## IV. 策略狀態與並發熱更新 (Policy State & Hot Updates)

為確保策略狀態無法被受管轄代碼竄改，每個角色的 $B_r$ 作為不可變策略快照載入於防寫記憶體頁面中。策略更新不對現役點陣圖進行原地修改，而是構建全新經校驗的 $B'_r$，並使用 RCU（讀-複製-更新）原子指標交換進行無鎖置換：
$$B_r \xrightarrow{\text{atomic}} B'_r$$
此設計徹底杜絕並發分派中觀測到半更新狀態之風險，並確保策略更新在零停機下以小於 1.0 $\mu\text{s}$ 的傳播延遲注入工作執行緒，且不在授權熱路徑上引入全域鎖互斥。圖 3 展示了此雙緩衝 RCU 指針交換協議。

![圖 3：DROS GuardVM 中無鎖 RCU 雙緩衝策略熱更新機制。](figures/fig3_rcu_hot_update.png)

*圖 3：DROS GuardVM 中無鎖 RCU 雙緩衝策略熱更新機制。*

---

## V. 安全模型 (Security Model)

我們假設對手能控制外部輸入、構造任意複雜的對抗提示詞、利用多輪情境污染、透過可用工具嘗試特權提升或進行供應鏈工作流操縱。
對手**無法**：偽造 Ed25519 簽名、竄改防寫策略記憶體、修改編譯後的二進位代碼、直接變更受信任環境配置，或透過任意原生代碼注入/核心漏洞繞過受管轄邊界。

### 運作公理 (Operational Assumptions for Complete Mediation)
* **假設 A1（邊界完全仲裁）：** 所有安全相關操作 $m \in \mathcal{M}$ 均嚴格經由插樁之 DROS C-ABI 介面分派；未受管轄之原生逃逸由周邊部署環境約束。
* **假設 A2（密碼學不可偽造性）：** 對手在無私鑰 $K_{\text{AIA}}$ 下無法偽造 Ed25519 簽名，且 SHA-256 碰撞在計算上不可行。
* **假設 A3（策略不可變性）：** 已編譯之能力庫 $B$ 被載入進程內託管代碼無法寫入的防寫記憶體頁面中。
* **假設 A4（分派完整性）：** L4 參考監視器在移交控制權予工具主體前同步完成授權評估。

---

## VI. 形式化執行性質 (Formal Execution Property)

令 $\text{GExec}(r, m_i, s)$ 代表工具 $m_i$ 代表狀態 $s$ 下的角色 $r$，經由已登記之 DROS 分派路徑執行完成。

### 定理一（確定性執行邊界遏制定理）
> **定理一 (Execution Boundary Confinement):** 在假設 A1--A4 成立下，對所有代理人角色 $r \in \mathcal{R}$、所有工具 $m_i \in \mathcal{M}$ 及執行狀態 $s \in \mathcal{S}$，若 $B_r[i] = 0$，則不可發生任何受管轄之執行：
> $$B_r[i] = 0 \implies \neg\text{GExec}(r, m_i, s)$$

*證明：*
1. 根據假設 A1，調用 $m_i$ 必須進入 DROS C-ABI 參考監視器。
2. 根據假設 A4，唯有參考監視器返回 `ALLOW` 時，執行流程方可轉移至工具實作。
3. 根據 L4 之構建，用於能力解析的主體嚴格綁定至經認證之 DIT：
$$\text{DispatchPrincipal}(x) = \text{AuthenticatedRole}(\text{DIT}) = r$$
執行放行（`ALLOW`）若且唯若 $\text{Verify}(\sigma_{\text{DIT}}, K_{\text{AIA}}) = \text{VALID}$、$\text{DispatchPrincipal}(x) == r$（防止呼叫端變數竄改偽造），且位元運算 $B_r[i] == 1$ 為真。
4. 根據假設 A2，對手無法偽造有效 DIT。
5. 根據假設 A3，$B_r[i]$ 在執行期不可被竄改。
6. 因此，若 $B_r[i] = 0$，檢查必為假，觸發 FFI panic 並返回 `DENY` (HTTP 403)，阻斷執行。
7. 故 $\text{GExec}(r, m_i, s)$ 為假。取逆否命題即得：$\text{GExec}(r, m_i, s) \implies \text{ValidDIT}(r, s) \land (B_r[i] = 1)$。$\blacksquare$

---

## VII. 系統實作 (Implementation)

原型系統包含：
* Rust 撰寫的高效能強制核心 (`libdros.so` / `dros.dll`)；
* Python 撰寫的策略與語義編排層；
* 相容於 CPython、Node.js 與 JVM 執行期的 C-ABI 綁定介面；
* 寫保護頁快照儲存庫與 RCU 原子置換機制；
* Ed25519 與 SHA-256 Merkle 審計鏈記錄器。

授權操作零堆積分配，時間複雜度為 $O(1)$，徹底將 $O(\text{LLM})$ 的語意處理路徑與 $O(1)$ 的執行授權路徑解耦。

---

## VIII. 實證系統評測 (Empirical Evaluation)

### A. 測試環境與工作負載
評測硬體為 Intel Xeon E3-1275L v3 (4C/8T, 16GB RAM)，軟體為 Ubuntu 22.04 LTS (Kernel 6.6, Docker 26.1) 與 Windows 10 IoT Enterprise LTSC / Python 3.11。
全量 24 小時測試處理了 160,611 次請求，包含 22,860 次正常請求與 137,751 次橫跨五大類的對抗性請求（已知模板 IPI: 68,420；混淆 IPI: 52,180；目標劫持: 9,251；特權提升: 6,112；供應鏈操縱: 1,788）。所有評測經過 5 次獨立端到端運行。

---

## IX. 逐層累加消融實驗 (Layer Ablation - RQ1 & RQ2)

**表一：累加式層級添加防禦實驗結果**

| 配置層級 | L1 | L2 | L3 | L4 | 已知模板 IPI 阻斷率 | 混淆 IPI 阻斷率 | 中位決策延遲 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 基準無防禦 (Baseline) | N | N | N | N | 0.0% | 0.0% | 0.0 $\mu\text{s}$ |
| +L1 語意過濾 | Y | N | N | N | 85.2% | 0.0% | 45.2 ms |
| +L1+L2 身分綁定 | Y | Y | N | N | 90.0% | 0.0% | 25.8 $\mu\text{s}$ |
| +L1+L2+L3 拓撲約束 | Y | Y | Y | N | 93.5% | 0.0% | 26.0 $\mu\text{s}$ |
| 完整 DROS (L1--L4) | Y | Y | Y | Y | 100.0% | 100.0% | 26.21 $\mu\text{s}$ |
| 觀測誤報率 (FPR) | - | - | - | - | - | - | 0 / 22,860 |

**核心發現：**
1. L1--L3 逐步改善上游過濾，但若無 L4，全部 52,180 筆混淆 IPI 嘗試均能繞過上層防線。
2. L4 彌合了已知模板子集最後 6.5 個百分點的防禦落差（從 93.5% 提升至 100.0%），並作為唯一能夠阻斷全部 52,180 筆混淆嘗試（0.0% 提升至 100.0%）的機制。
3. 實證確認僅靠語意與結構治理無法保障執行邊界的確定性遏制。

---

## X. 效能與延遲開銷評測 (Performance - RQ3)

評測明確解耦語義推論與執行期強制延遲：
* $L_{\text{semantic}} \approx 45.2\ \text{ms}$：評估上游 LLM 意圖解析與提示詞過濾。
* $L_{\text{policy}} = 26.21\ \mu\text{s}$ (P50)：度量自收到 DIT 起算，經 L2 密碼學驗證、L3 ABAC 解析與 L4 點陣圖比對的下游管線延遲。
* $L_{\text{isolated}} = 825.0\ \text{ns}$：度量 L4 C-ABI 邊界零堆積分配下獨立的能力檢查關鍵路徑。
* $L_{\text{P99}} = 242.69\ \mu\text{s}$：於高並發突發微基準測試期間測得。
* CPU 使用率開銷相較於無插樁對等負載小於 1.8%。

---

## XI. 長期穩定性浸泡評測 (Long-Run Stability - RQ4)

在 24 小時持續測試中，系統處理了 160,611 次請求，觀測到 100% 對抗性阻斷（137,751/137,751）、0/22,860 策略誤報率、經 jemalloc 與系統 RSS 監控未檢測出任何記憶體洩漏，點陣圖常駐記憶體小於 1 MB。
*註：分母 22,860 包含 22,854 筆成功授權操作與 6 筆傳輸層 TCP `TIME_WAIT` 埠耗盡瞬時例外；無任何正常業務請求因策略邏輯誤判被阻擋。*

---

## XII. 最小基質極限評測 (Minimal-Substrate Crucible)

當代理人規劃層被完全攻陷且上層治理全部崩潰時（$\mathcal{C}^* = \text{Hostile}$），我們測試了裸奔環境下的 DROS C-ABI 基質：
* 注入 1,000 次敵意權能轉移（906 次未授權，94 次合法）；
* DROS 達成 906/906 未授權攔截（100.0% 阻斷，0 次逃逸），合法請求 94/94 正常放行；
* 經 SHA-256 比對，宣告之受保護狀態集合 $\mathcal{S}_{\text{protected}}$ 內觀測到**零未授權狀態變異**；
* 獨立 C-ABI 決策延遲平均 825 ns（P99 為 2.8 $\mu\text{s}$），含審計鏈插入之端到端輸送量達 52,583 decisions/sec。

---

## XIII. 攻擊鏈力學重現評測 (ATS-006 / PC-11)

重現現代編碼代理人多步驟攻擊力學（$\text{Input} \to \text{Agent} \to \text{Tool} \to \text{Process} \to \text{Resource}$）：
DROS 於 T3（工具替換: 2.5 $\mu\text{s}$）、T5（進程衍生: 0.8 $\mu\text{s}$）及 T6（保護資源存取: 1.0 $\mu\text{s}$）建立三重二進位檢查點實施硬熔斷，並透過 RCU 策略紀元置換（0.6 $\mu\text{s}$）永久終結會話。

---

## XIV. 與既有執行期機制橫向對比 (Comparative Taxonomy)

$\text{DROS}_{\text{runtime}}$ 與 $\text{OS}_{\text{security}}$ 運作於完全不同的身分粒度：作業系統（SELinux、Seccomp）管理進程、使用者與系統呼叫，而 DROS 則將行程內瞬態邏輯代理人身分帶入受管轄執行分派中，兩者在架構上高度互補。

---

## XV. 跨架構邊界覆蓋範圍研究 (Boundary Coverage Study)

**表二：架構邊界覆蓋範圍與決策路徑開銷評測**

| 評測配置 / 強制組別 | 標準工具遏制率 (RQ1) | 未宣告路徑邊界覆蓋率 (RQ2) | P99 決策延遲 (RQ3) |
|:---|:---:|:---:|:---:|
| **組別 A: 基準無防禦** (Baseline) | 0.0% (被利用) | 未受監控 | 0.40 $\mu\text{s}$ |
| **組別 B: 應用中介軟體** (Microsoft AGT v4.x 配置) | 100.0% 阻斷 | 缺乏策略攔截點 | 1.80 $\mu\text{s}$ |
| **組別 C: DROS GuardVM** (C-ABI 執行基質) | 100.0% 阻斷 | 於 C-ABI 確定性 DENY | 1.20 $\mu\text{s}$ |
| **組別 D: 縱深防禦** (AGT + DROS) | 100.0% 阻斷 (L1) | 於 C-ABI 確定性 DENY | 15.90 $\mu\text{s}$ |

*結論：* 應用層策略框架（如 AGT / ACS）治理代理人被允許「請求」什麼，而 DROS 則保證行程內邏輯主體歸因完整傳遞至二進位邊界以決定「執行」什麼。

---

## XVI. 討論 (Discussion)

1. **架構意義：** 確立了 $\text{Semantic Decision} \neq \text{Execution Authority}$，允許上游機率組件保持靈活性，同時在下游杜絕認知失陷蔓延至執行權能擴張。
2. **作為軟體品質屬性的安全性：** 確定性行為、有界決策延遲、顯式授權表示、無鎖並發安全、可測試性與部署隔離。
3. **底層系統呼叫強制之配套研究 (DROS-PGM)：** DROS 聚焦於直譯器 C-ABI/FFI 邊界之代理人歸因，配套研究 DROS-PGM 則於 OS 系統呼叫邊界防護主機二進位惡意軟體，兩者互補且邊界清晰。

---

## XVII. 限制 (Limitations)

1. **未受管轄之原生代碼：** DROS 不宣稱對任意繞過直譯器的原生機器碼具備完全仲裁力；
2. **機率性上游：** 上游語義層本質為機率性，DROS 不保證消除幻覺或改善推理本質；
3. **評測語料庫範疇：** 100% 阻斷率代表於已定義語料庫及受管轄邊界內之實證結果，非對未來一切未知攻擊之數學全肯定；
4. **工具枚舉假設：** 目前依賴初始化已登記之工具宇集 $\mathcal{M}$。

---

## XVIII. 相關工作 (Related Work)

涵蓋代理人軟體架構與提示注入（Perez & Ribeiro 2022; Greshake et al. 2023; InjecAgent 2024; ACM CSUR 2025）、執行期系統與 OS 強制（SELinux 2001; SEAndroid 2013; Seccomp）、權能系統與存取控制架構（Dennis & Van Horn 1966; Levy 1984; RBAC 1996; Macaroons 2014），以及執行期可觀測性（AgentSight 2025; AgentOps 2024）。DROS 核心定位為：應用歸因 + 密碼學綁定 + 情境策略 + 確定性二進位執行之架構編排。

---

## XIX. 結論 (Conclusion)

本文提出 DROS 執行期架構，解決了自主 AI 軟體系統中跨越「應用程式至執行邊界」的代理人身分歸因鴻溝。形式模型證明了在完全仲裁條件下的確定性邊界遏制；實證評測驗證了 160,611 次請求下的高可靠度與次微秒級開銷。其軟體工程意涵在於：自主 AI 軟體系統無須單純依賴語意正確性作為執行安全之後盾，語意決策與執行授權可被解耦為完全獨立的執行期職責。

---

## 致謝與 AI 協作聲明 (Acknowledgments and AI Collaboration Disclosure)

本研究由作者獨立提出架構願景、問題定義、形式模型、實驗方法與論文定稿。生成式 AI 工具輔助了部分文檔結構與語法潤飾。作者承擔完全學術與法律責任。  
**專利聲明：** 本研究核心架構已受美國臨時專利保護（U.S. PPA No. 64/111,973，Patent Pending）。

---

## 參考文獻 (References)
[1] N. Hardy, "The Confused Deputy," ACM SIGOPS OSR, 1988.  
[2] J. P. Anderson, "Computer Security Technology Planning Study," Tech. Rep., 1972.  
[3] OWASP Foundation, "OWASP Top 10 for Agentic Applications (2026 Edition)," 2025.  
[4] J. B. Dennis & E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," CACM, 1966.  
[5] H. M. Levy, Capability-Based Computer Systems, Digital Press, 1984.  
[6] R. S. Sandhu et al., "Role-Based Access Control Models," IEEE Computer, 1996.  
[7] V. Hu et al., "Guide to Attribute Based Access Control (ABAC)," NIST SP 800-162, 2014.  
[8] F. Perez & I. Ribeiro, "Ignore Previous Prompt," NeurIPS MLS, 2022.  
[9] K. Greshake et al., "Not What You've Signed Up For," ACM AISEC, 2023.  
[10] F. He et al., "The Emerged Security and Privacy of LLM Agent," ACM CSUR, 2025.  
[11] Q. Zhan et al., "InjecAgent: Benchmarking Indirect Prompt Injections," ACL, 2024.  
[12] A. Birgisson et al., "Macaroons: Cookies with Contextual Caveats," NDSS, 2014.  
[13] P. Loscocco & S. Smalley, "Integrating Flexible Support for Security Policies into Linux," USENIX ATC, 2001.  
[14] S. Smalley & R. Craig, "Security Enhanced (SE) Android," NDSS, 2013.  
[15] Linux Programmer's Manual, "seccomp(2)," Kernel 6.9, 2024.  
[16] R. C. Merkle, "A Digital Signature Based on a Conventional Encryption Function," CRYPTO, 1987.  
[17] Y. Zheng et al., "AgentSight: System-Level Observability for AI Agents Using eBPF," arXiv:2508.02736, 2025.  
[18] Y. Zheng et al., "AgentOps: Enabling Observability of LLM Agents," arXiv:2411.05285, 2024.  
[19] C. C. Chen, "Runtime Attribution Framework," Zenodo, 2026.  
[20] C. C. Chen, "DROS-PGM: A Deterministic Post-Compromise Execution Containment Substrate," Zenodo, 2026.  
