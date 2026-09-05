# DROS：彌合自主 AI 負載中「代理人至執行歸因鴻溝」之四層確定性執行期作業系統

> **作者：** 陳濬程（Jimmy Chen）
> **單位：** Top-Celestial Company Ltd.，中華民國臺灣臺北
> **聯絡：** jimmychen@dr-os.io
> **ORCID：** 0009-0001-6387-0500
> **版本：** v3.0 | 2026-08-25
> **目標期刊：** ACM Transactions on Privacy and Security (TOPS) (Special Section: AI Safety and Governance)

---

## 摘要 (Abstract)

在高風險企業環境中，能夠執行多步驟工具調用的自主 AI 代理人迅速部署，引入了現有防禦無法應對的根本性安全鴻溝：語義防火牆（如 NVIDIA NeMo Guardrails）以機率方式運作，易受間接提示注入（IPI）的對抗性混淆攻擊；而傳統作業系統層機制（如 eBPF、Seccomp）雖具確定性，卻存在情境盲視問題，因為系統呼叫強制機制通常缺乏細粒度的應用層語意身分，無法區分在單一共享行程（如 `python.exe`）內並發運行的不同代理人角色與瞬態任務。我們將此結構性弱點定義為**代理人-至-執行歸因鴻溝（Agent-to-Execution Attribution Gap）**。

為填補此鴻溝，我們提出 **DROS（確定性執行時操作系統，Deterministic Runtime Operation System）**——一種四層縱深防禦架構，包含：（L1）機率語義邊界過濾層；（L2）透過密碼學執行令牌（DIT）將代理人角色綁定的三層 PKI 身份層；（L3）以屬性為基礎的存取控制（ABAC）拓撲強制層；以及（L4）在 FFI 邊界執行零堆積 O(1) 能力點陣圖比對的確定性 C-ABI 二進位強制層。

針對 24 小時浸泡測試（N=160,611 次總請求，N_adv=137,751 次橫跨四大攻擊家族、共五類測試分支的對抗性嘗試）進行的實證評估顯示：對於所有到達 L4 C-ABI 邊界的調用，完整 DROS 架構在已定義的威脅模型下，針對已評估對抗性語料庫達到觀測上的 100% 阻擋率。下游治理決策管線的中位策略評估延遲為 26.21 $\mu\text{s}$（P99=242.69 $\mu\text{s}$，排除上游語義 Token 解析），獨立 C-ABI 點陣圖強制延遲低於 500 ns，相較於無插樁之基準負載僅引入小於 1.8% 的 CPU 使用率開銷。在累加式層級添加實驗中，L4 將已知模板 IPI 子集的觀測阻斷率從 93.5% 提升至 100%，同時作為唯一能夠阻斷逃過 L1-L3 的 52,180 次對抗性混淆嘗試的評測層級。此外，與應用層中介軟體概念（基於 Microsoft AGT 規範）的多架構策略比對證實，DROS 能以次微秒級的 P99 決策路徑延遲（$1.20\ \mu\text{s}$），為未經託管之執行路徑建立互補性的執行邊界參考監視器。

**關鍵詞** — AI 代理人安全、執行時治理、C-ABI 邊界強制、零信任架構、公鑰基礎設施、間接提示注入、能力型存取控制、歸因鴻溝、縱深防禦、多架構評測基準。

---

## 一、引言 (Introduction)

自主 AI 代理人已從被動對話系統演化為主動執行者，能夠調用企業 API、寫入資料庫、執行程式碼，並協調多代理人工作流程。此一演化從根本上擴大了企業攻擊面：被入侵的代理人現在代表一個在合法授權權限邊界「之內」運作的攻擊者。

核心挑戰不僅在於防止代理人在語義層被操縱，更在於確保**語義層的妥協不會轉化為可執行層面的妥協**。本文推進以下核心論題：

> **論題（Thesis）**：DROS 並不宣稱能使代理人的內部認知或推理變得完全值得信賴；而是在明確定義的完全仲裁（Complete Mediation）部署邊界下確立：代理人認知層面的失陷，本身絕不會將其執行權限擴展至超出其在 C-ABI/FFI 邊界所密碼學綁定的能力包絡線之外。

當前防禦分為兩大類，各有根本性局限：

**語義防火牆（高語義、零確定性）：** 提示過濾系統（如 NVIDIA NeMo Guardrails、LlamaGuard、PromptBench）在應用層分析自然語言意圖。雖對已知攻擊模板有效，但對對抗性混淆、多輪情境污染，或透過外部資料來源進行的間接提示注入，提供零數學保證。

**作業系統層強制（高確定性、零語義）：** eBPF、SELinux、AppArmor 及 Seccomp 以確定性強制執行二進位系統呼叫規則。然而，它們受到我們所稱的**情境盲視問題（Context-Blindness Problem）**困擾：傳統 OS 機制基於核心可見的識別項（PID、UID、cgroups、命名空間、LSM 標籤）運作，通常缺乏細粒度的應用層語意身分，無法區分在單一共享直譯器行程（如 `python.exe`）內並發運行的不同代理人角色與瞬態任務。

基於 eBPF 的代理人可觀測性近期研究（如 AgentSight、AgentOps）提供了追蹤能力，但未能填補強制鴻溝：觀測到未授權呼叫已發生是不夠的；該呼叫必須在執行邊界被確定性地攔截與阻斷。

### A. 問題形式化：歸因鴻溝

我們將**代理人-至-執行歸因鴻溝**形式化定義為：
> **定義（歸因鴻溝，Attribution Gap）**：在共享的執行時身分下，應用層代理人主體與執行層授權決策之間缺乏值得信賴且可驗證的映射關係。當兩個或更多邏輯上不同的授權主體在同一個作業系統安全主體（例如共享的 PID/UID）內執行，而底層執行基質在強制邊界上無法以密碼學方式區分其授權狀態時，即存在歸因鴻溝。

```
傳統多代理人執行環境：
  代理人角色 A ──┐
                  ├── 單一 OS 行程 (PID 1234, UID 1000) ──> C-ABI / libc ──> 工具執行()
  代理人角色 B ──┘
  [核心 / eBPF / OS MAC 視角：所有調用均無差別來自 PID 1234，角色身分完全不可見]

DROS 帶內歸因基質：
  代理人角色 A ──> DIT_A (AIA 簽名) ──┐
                                       ├── C-ABI 參考監視器 ──> 不可變 B_A[i] ──> ALLOW/DENY
  代理人角色 B ──> DIT_B (AIA 簽名) ──┘                       不可變 B_B[i]
```

*與經典模型的區分*：儘管此問題在概念上與經典「困惑代理人問題」[Hardy 1988] 及「參考監視器理論」[Anderson 1972] 相關，但在代理人直譯執行期中展現了三項領域特有的工程挑戰：（1）多個具備不同權限的自主主體動態共存於單一語言直譯器內，缺乏 POSIX 邊界隔離；（2）代理人的內部控制流程由極易受認知劫持的機率性自然語言驅動；（3）現有作業系統權能或 POSIX 身分在缺乏帶內密碼學橋樑的情況下，無法檢查或綁定至行程內部瞬態生成的 LLM 角色。

本研究之核心新穎性並非單純的權能控制，亦非單純的密碼學身分，而是將瞬態行程內代理人主體的歸因關係，完整保真地傳遞至二進位執行邊界所做出的授權決策之架構編排。

### B. 本文貢獻

本文做出以下貢獻：

1. **歸因鴻溝形式化**：我們正式定義並描述代理人-至-執行歸因鴻溝，並示範其在四大攻擊家族（共五類測試分支）中的可利用性（第二章）。
2. **DROS 四層架構**：我們提出一種縱深防禦架構，形成從機率到確定性的安全漏斗，透過在執行邊界的密碼學身份綁定填補歸因鴻溝（第三章）。
3. **形式安全模型**：我們提出形式化能力安全模型，明確規範使能力遏制不變式（CEI）確定性成立的完全仲裁假設（公理 A1-A4）（第四章）。
4. **實證消融評估**：我們在開源可重現測試平台上，提出量化每層獨立及累積防禦貢獻的受控消融研究（第五章）。

---

## 二、背景與威脅模型 (Background and Threat Model)

### A. 代理人攻擊向量（AAV-2026）

我們定義威脅模型 **AAV-2026**，涵蓋當代自主代理人部署中觀察到的四大主要攻擊家族。所有攻擊共享一個共同前提：對手無法直接修改代理人程式碼或系統配置。

**表一：AAV-2026 威脅矩陣**

| 攻擊家族 | MITRE ATLAS | 攻擊機制 | 目標資產 |
|:---|:---|:---|:---|
| 間接提示注入 (IPI) | AML.T0051 | 攻擊者在代理人消費的外部不受信任資料（電子郵件正文、PDF 內容、資料庫記錄）中嵌入惡意指令 | 工具調用控制流程 |
| 目標劫持 | AML.T0054 | 情境視窗污染改變代理人的長期規劃目標，誘導未授權的多步驟行動鏈 | 代理人規劃狀態 |
| 透過工具濫用的特權提升 | AML.T0053 | 被入侵的代理人利用有效 OAuth 令牌調用超出其授權角色的高特權端點（如 deploy_prod、bulk_delete） | 授權邊界 |
| 上游妥協（供應鏈污染） | AML.T0010 | 外部投毒的模型權重或資料集誘導代理人自主合成未授權行動 | 授權邊界 |

### B. 對手模型

我們假設一個**受 Dolev-Yao 啟發的對手**，其：
- 控制所有流經外部來源（電子郵件、文件、第三方 API、資料集）的資料
- 無法修改代理人原始碼、系統配置或密碼學材料
- 僅能透過受託管之執行期介面調用系統工具（任意原生代碼注入、原始記憶體竄改與核心漏洞利用被視為部署環境邊界假設；見第七章 D 節）
- 能夠構造任意複雜的多輪對抗性提示
- 完全了解 L1 語義過濾啟發式規則（即能自適應性地繞過它）
- **無法**在未持有私鑰的情況下偽造密碼學簽名
- **無法**在執行時修改已編譯的能力點陣圖

此對手模型捕捉了現實企業威脅：當上游妥協（如投毒提示詞、RAG 資料或未受信任的模型權重）導致代理人合成出未授權的工具呼叫請求時，DROS 負責在執行邊界對產生的調用進行確定性強制，而不依賴上游原因。

### C. 現有防禦的局限性

**語義過濾（L1）**是我們的第一道但最薄弱的防禦層，因為它在可被任意混淆的自然語言表示上運作。研究表明，最先進的提示注入偵測器在 base64 編碼酬載、Unicode 同形字替換及多輪情境操縱面前失效。

**現有系統中的 PKI 與零信任網路（L2 類比）**通常在服務層級（mTLS、OAuth）綁定身份，而非在服務內部的代理人角色層級。在已授權服務進程中運行的被入侵代理人，繼承了該服務的完整憑證。

**ABAC/RBAC 中介層（L3 類比）**通常在執行路徑之外的 API 閘道層（4-50 ms 延遲）運作，無法阻止繞過閘道的 FFI 層工具調用。

---

## 三、DROS 架構 (DROS Architecture)

DROS 實施一種縱深防禦漏斗，將機率語義防禦轉化為確定性執行邊界強制（Deterministic Execution-Boundary Enforcement）。四個層次在架構上解耦：控制平面（策略配置與 PKI 簽發）與執行時強制平面（二進位執行）獨立運作。

![圖一：DROS 控制平面與執行時強制平面架構。](E:/vscode/AI知識庫/DROS商品專案暫存/商業與架構文件庫/DROS_Visual_Assets/dros_defense_layers_zh.png)

*圖一：DROS 控制平面與執行時強制平面架構。*

### A. L1 — 語義邊界層（機率過濾）

L1 對自然語言輸入執行語義分析，應用已知注入模板匹配、輸入清理及意圖分類。L1 在應用層運作，不提供任何數學安全保證。其設計目標是在已知的、未混淆的攻擊進入系統之前，以低成本（O(輸入 tokens)）過濾大多數攻擊，降低下游層的負擔。

**L1 處理 85.2% 的已評估對抗性流量**（見第五章），涵蓋直接的注入模板及已知攻擊特徵。L1 被明確設計為可被精密對手繞過；其失敗模式由 L2-L4 處理。

### B. L2 — 零信任身份層（密碼學綁定）

L2 透過引入 **DrosIdentityToken（DIT）** 消除情境盲視問題：一種密碼學簽名的執行令牌，將（代理人角色、任務 ID、授權範圍、能力點陣圖雜湊）綁定至每一次工具調用。

**三層 PKI 架構：**
- **根 CA**（DROS-ROOT-CA-2026）：企業根憑證，離線金鑰保管
- **AIA 中間 CA**：自動簽發中心，簽發每次部署的憑證
- **BEC 終端憑證**（綁定執行憑證，Bound Execution Certificate）：將代理人角色與能力點陣圖密碼學綁定至短期執行憑證

每次工具調用皆攜帶 DIT。GuardVM 在點陣圖比對前驗證 Ed25519 簽名。這確保即使代理人在語義層遭入侵，也無法調用其密碼學綁定範圍之外的工具。

**DIT 形式結構：**
```
DIT := {
  agent_id:           UUID，
  role_id:            uint32，
  capability_bitmap:  B 屬於 {0,1}^N，
  bitmap_hash:        SHA-256(B)，
  issued_at:          Unix 時間戳，
  expires_at:         Unix 時間戳（TTL：15 分鐘），
  signature:          Ed25519(private_key_BEC, DIT_body)
}
```

**跨組織聯邦：** 當代理人跨企業邊界互動（Corp-Alpha -> Corp-Beta）時，L2 延伸為跨域 PKI 閘道：接收方企業的 GuardVM 根據發送方企業已發布的根 CA 憑證驗證外部 DIT，無論外部代理人聲稱的權限為何，均強制執行本地能力點陣圖。

### C. L3 — 代理人拓撲與 ABAC 層（結構隔離）

L3 透過 `agent_manifest.yaml` 強制執行多代理人 Swarm 拓撲約束，聲明式地規定：
- 代理人角色間允許的通訊通道（有向無環能力圖）
- 跨部門調用限制（例如：HR-Agent 不得調用 DevOps-Agent API）
- 每個代理人角色的最大扇出限制（防止放大攻擊）

L3 實施符合 NIST SP 800-162 的 ABAC，在編排層對執行時 DIT 屬性進行評估。

#### D. L4 — C-ABI 確定性二進位強制層（執行閘）

L4 是 DROS 的核心安全創新，運作於 C-ABI/FFI 邊界——任何工具調用從 LLM 的託管執行時跨入二進位執行的確切轉換點。它實施的是執行邊界禁錮（Execution-Boundary Enforcement），而非硬體層級之物理強制。

**能力點陣圖強制：**

給定包含 N 個系統工具的宇集 M={m_1, ..., m_N}，每個代理人角色 r 在系統初始化時被分配一個能力向量 B_r 屬於 {0,1}^N。對於請求的工具 m_i，強制決策為：

```
Decision(r, m_i) = ALLOW  若 B_r[i] = 1
                   DENY   若 B_r[i] = 0
```

實際實作為零堆積位元運算 AND：

```
Decision = Capability_Bitmap[Role_ID] & Requested_Tool_Bit
```

此操作以 O(1) 常數時間執行，零字串解析、零 LLM 推理、零堆積分配，達到亞微秒級的獨立決策延遲。

**不可變性保證：** 能力點陣圖在系統初始化時從 `vajra.md` 策略聲明編譯，並載入寫保護的記憶體頁面。不存在任何託管執行時路徑允許代理人在未攻陷底層作業系統核心的情況下修改點陣圖。

**確定性強制：** 點陣圖結果為 0 觸發立即的 FFI panic，向呼叫者返回 HTTP 403——強制執行發生在任何工具函數體執行之前。

---

## 四、形式安全模型 (Formal Security Model)

為杜絕將實作代碼簡單重述為不變式的循環論證，我們在四項明確的運行環境假設下形式化整個安全基質：

### A. 完全仲裁之運作假設 (Operational Assumptions for Complete Mediation)
- **假設 A1（邊界完全仲裁，Complete Boundary Mediation）**：所有涉及安全影響的工具調用 $m \in \mathcal{M}$ 均嚴格透過經插樁的 DROS C-ABI 介面分派。外部未經仲裁的原生系統呼叫或動態函式庫加載，由宿主部署環境之隔離機制加以限制（見第七章 D 節）。
- **假設 A2（密碼學不可偽造性，Cryptographic Unforgeability）**：攻擊者在無 AIA 私鑰 $K_{\text{AIA}}$ 的前提下無法偽造 Ed25519 簽名，且 SHA-256 碰撞在計算上不可行。
- **假設 A3（策略不可變性，Policy Immutability）**：已編譯之能力庫 $B$ 被載入至進程內託管代碼無法寫入的防寫記憶體頁面中。
- **假設 A4（分派完整性，Dispatch Integrity）**：L4 參考監視器在將執行控制權移交給工具實作主體前，同步完成授權評估。

### B. 受管轄執行之定義 (Definition of Governed Execution)
我們定義受管轄執行謂詞 $\text{GExec}(r, m_i, s)$ 為真，若且唯若工具 $m_i$ 代表狀態 $s$ 下的角色 $r$，經由已登記之 DROS 分派路徑執行完成。

### C. 定理一（CEI 下之執行邊界遏制）
> **定理一（執行邊界遏制定理，Execution Boundary Confinement Theorem）**：在假設 A1--A4 成立的前提下，對所有代理人角色 $r \in \mathcal{R}$、所有已登記工具 $m_i \in \mathcal{M}$ 及所有執行時狀態 $s \in \mathcal{S}$，若 $B_r[i] = 0$，則不可發生任何受管轄之執行：
> $$B_r[i] = 0 \implies \neg\text{GExec}(r, m_i, s)$$

*證明*：
1. 根據假設 A1，執行 $m_i$ 必須進入 DROS C-ABI 參考監視器。
2. 根據假設 A4，唯有參考監視器返回 `ALLOW` 時，執行流程方可轉移至工具主體。
3. 根據 L4 之構建，用於能力解析的主體嚴格綁定至經認證之 DIT：
$$\text{DispatchPrincipal}(x) = \text{AuthenticatedRole}(\text{DIT}) = r$$
執行放行（`ALLOW`）若且唯若 $\text{Verify}(\sigma_{\text{DIT}}, K_{\text{AIA}}) = \text{VALID}$、$\text{DispatchPrincipal}(x) == r$（防止呼叫者竄改執行期變數），且位元運算 $B_r[i] == 1$ 為真。
4. 根據假設 A2，攻擊者在無 $K_{\text{AIA}}$ 時無法偽造角色 $r$ 的有效憑證。
5. 根據假設 A3，$B_r[i]$ 在執行期不可被修改。
6. 因此，若 $B_r[i] = 0$，該檢查必為假，觸發 FFI panic 並返回 `DENY` (HTTP 403)，阻斷分派。
7. 故 $\text{GExec}(r, m_i, s)$ 為假。取逆否命題即得：$\text{GExec}(r, m_i, s) \implies \text{ValidDIT}(r, s) \land (B_r[i] = 1)$。$\blacksquare$

### D. 衍生安全性質

**性質一（受管轄執行禁錮）：** 一個在語義層受入侵的代理人，無法成功執行任何 $B_r[i] = 0$ 的受管轄工具調用，無論其提示詞操縱或認知受控程度為何。

**性質二（爆炸半徑不變式）：** 令 $\mathcal{C}^* = \text{Hostile}$ 代表代理人規劃狀態的完全認知淪陷。令 $\mathcal{E}_{\text{effective}}$ 代表受入侵代理人可達成的工具執行集合。在假設 A1--A4 成立下：
$$\mathcal{C}^* = \text{Hostile} \land \text{定理一} \implies \mathcal{E}_{\text{effective}} \subseteq \mathcal{B}_{r_{\text{assigned}}}$$
亦即，代理人模型的認知失陷，在數學上絕不會將其可生效的執行權限擴展至超出其認證角色所預分配的能力包絡線。

**性質三（密碼學可驗證執行存證）：** 每個 ALLOW 和 DENY 決策都被記錄在 Ed25519 簽名、SHA-256 Merkle 雜湊鏈審計日誌中，提供具防篡改特性的密碼學可驗證執行存證，適用於鑑識分析與監管合規性檢驗。

---

## 五、實作與實驗評估 (Implementation and Experimental Evaluation)

### A. 實作

DROS 以 Rust（L4 強制核心）與 Python（L1-L3 編排層）實作，具備相容 CPython、Node.js 及 JVM 執行時的 C-ABI FFI 綁定。GuardVM 元件作為策略強制點（PEP）與策略決策點（PDP），與代理人執行時共置部署。

為確保 C-ABI 層的不可篡改性與效能，L4 能力點陣圖在記憶體中利用**寫保護頁（Write-protected pages）**進行防篡改，並採用 **RCU（Read-Copy-Update）**機制實現零停機的熱更新（Hot-updates）。

**測試環境：**
- 硬體：Intel Xeon E3-1275L v3（4 核心，8 執行緒，16 GB RAM）
- 參考容器環境：Ubuntu 22.04 LTS（Linux Kernel 6.6，Docker 26.1）
- 主機驗證環境：Microsoft Windows 10 IoT Enterprise LTSC (Build 19044) / Python 3.11
- 代理人執行時：Python 3.11（LangChain 0.2，OpenAI GPT-4o）

為確保完整的科學可重現性，所有測試腳本、攻擊酬載與連續執行測試套件，均已在 **DROS 驗證與評估平台（DROS-VEP-lite）** 開源儲存庫中公開提供：<https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite>。本地單節點 Docker Compose 部署參考環境請見 **DROS Home-Lab** 儲存庫：<https://github.com/Top-Celestial-Company-Ltd/dros-home-lab>。

### B. 攻擊語料庫方法論

我們以完整的方法論透明度建構評估語料庫：

- **總請求數**：N=160,611 次，持續 24 小時
- **正常工作負載**：N_ben=22,860 次（來自授權角色的合法工具調用）
- **對抗性語料庫**：N_adv=137,751 次，橫跨四大攻擊家族（共五類測試分支）：
  - IPI（模板型）：68,420 次已知注入模式（OWASP 語料庫）
  - IPI（混淆型）：52,180 次對抗性變異酬載（base64、Unicode、多輪）
  - 目標劫持：9,251 次長期情境污染序列
  - 特權提升：6,112 次邊界角色跨越嘗試
  - 供應鏈污染：1,788 次跨企業橫向移動模擬

所有對抗性酬載使用 DROS 紅隊熔爐框架生成（以 GPT-4o、Claude 3.5、Gemini Pro 作為攻擊模型）。測試重複 5 次獨立運行；以下結果報告均值。
對抗性語料庫與 L1 訓練/規則數據嚴格隔離（無資料洩漏）。正常流量 $N_{ben}=22,860$ 下的 0% 誤報率在統計上具有高度顯著性。

### C. 消融實驗結果

**表二：逐層消融實驗**

| 配置 | 已知 IPI 阻擋率 | 混淆 IPI 阻擋率 | 未授權執行 (漏網率) | 中位延遲 |
|:---|:---:|:---:|:---:|:---:|
| 基準線（無防禦） | 0.0% | 0.0% | 100.0% | 0 $\mu\text{s}$ |
| 僅 +L1（語義） | 85.2% | 0.0% | 14.8% | 45.2 ms |
| +L1+L2（PKI 綁定） | 90.0% | 0.0% | 10.0% | 25.8 $\mu\text{s}$ |
| +L1+L2+L3（ABAC） | 93.5% | 0.0% | **6.5%** | 26.0 $\mu\text{s}$ |
| **完整 DROS（L1-L4）** | **100.0%** | **100.0%** | **0.0%** | **26.21 $\mu\text{s}$** |
| 誤報率（正常被阻擋） | — | — | **0.0%** | — |

**關鍵發現：** 在缺少 L4 的情況下，高達 **6.5% 的對抗性混淆 IPI 酬載逃過 L1-L3 防線**並成功執行未授權的工具調用。加入 L4 後，漏網率降為 0%。L4 為此攻擊面提供了唯一確定性的強制防禦，這為「單靠語義層防禦無法保證執行層禁錮」」的核心論題提供了直接的實證支持。此外，經過 5 次獨立運行，完整架構的 100% 阻擋率呈現零方差（Zero Variance），提供了極高的統計信賴區間。

### D. 對照結果：有無 DROS L4 之比較

**表三：受控對照比較**

| 測試場景 | 無 DROS | 有 DROS（L4 啟用） | 強制延遲 |
|:---|:---|:---|:---:|
| ATS-001：透過 IPI 的客戶資料庫外洩 | 100% 洩漏 | 100% 阻擋（HTTP 403 DENY） | 25.8 $\mu\text{s}$ |
| ATS-002：透過憑證提取的 ERP 勒索 | 100% 洩漏 | 100% 阻擋（HTTP 403 DENY） | 26.1 $\mu\text{s}$ |
| ATS-003：Fable-5 越獄（未授權部署） | 100% 洩漏 | 100% 阻擋（HTTP 403 DENY） | 25.5 $\mu\text{s}$ |
| ATS-004：跨企業供應鏈劫持 | 100% 洩漏 | 100% 阻擋（HTTP 403 DENY） | 26.4 $\mu\text{s}$ |

### E. 橫向對照評測：多架構橫向基準測試 (AGT vs. DROS)

為評估治理複雜性所處之層級並檢驗強制邊界的覆蓋範圍，我們在相同硬體與對抗負載下，針對應用層中介軟體（Microsoft AGT v4.1.0 規格）與二進位執行受質（DROS GuardVM）進行了多架構基準對照測試。

本評測回答三大核心研究問題（Research Questions）：
* **RQ1 (標準宣告工具之政策強制):** AGT 與 DROS 均能對橫跨所有受測 ATS 場景之標準顯式宣告工具調用實施確定性 Allow/Deny 決策。
* **RQ2 (執行強制邊界覆蓋範圍):** 當執行過程超出標準工具裝飾器並透過未託管之執行路徑（PROBE-01: 原生檔案 I/O、PROBE-02: 原生 TCP Socket、PROBE-03: 子進程衍生、PROBE-04: 同進程變數覆寫）進行時，在本次測試配置下未觀測到 AGT 政策攔截。相對地，DROS GuardVM 在其封裝與受控之 C-ABI 邊界產生了確定性 DENY 阻斷。
* **RQ3 (決策延遲開銷):** 在高頻微基準測試中（每組 $N=10,000$ 次獨立迭代，Intel Xeon E3-1275L v3 @ 2.70GHz, Windows 10 IoT Enterprise LTSC / Python 3.11），測得之 P99 決策延遲分別為：Baseline ($0.40\ \mu\text{s}$)、AGT ($1.80\ \mu\text{s}$)、DROS GuardVM ($1.20\ \mu\text{s}$) 以及雙層縱深 AGT+DROS ($15.90\ \mu\text{s}$)。

**表五：多架構橫向對照評測結果**

| 治理架構組別 / 強制受質 | 標準宣告工具遏制率 (RQ1) | 宣告路徑外之邊界覆蓋 (RQ2) | P99 決策延遲 (RQ3) |
|:---|:---:|:---:|:---:|
| **Arm A: Baseline** (無任何治理) | 0.0% (完全被滲透) | 未受監控 | 0.40 $\mu\text{s}$ |
| **Arm B: Microsoft AGT** (中介軟體) | 100.0% 攔截 | 未產生政策攔截 | 1.80 $\mu\text{s}$ |
| **Arm C: DROS GuardVM** (C-ABI 受質) | 100.0% 阻斷 | C-ABI 確定性 DENY | 1.20 $\mu\text{s}$ |
| **Arm D: Defense-in-Depth** (雙層縱深) | 100.0% 阻斷 (L1 攔截) | C-ABI 確定性 DENY | 15.90 $\mu\text{s}$ |

*核心發現*：實驗結果支持「應用層治理與執行層強制具備互補性」之架構推論：AGT 治理代理人「被允許請求什麼」，而 DROS 則在 C-ABI 邊界治理「被允許執行什麼」。

### F. 24 小時微基準測試摘要

**表六：24 小時浸泡測試結果**

| 指標 | 數值 | 備註 |
|:---|:---|:---|
| 總測試請求數 | 160,611 次 | 連續 24.0 小時運行 |
| 策略評估延遲（P50） | 26.21 $\mu\text{s}$（+/- 0.34 $\mu\text{s}$） | 5 次運行均值 |
| 策略評估延遲（P99） | 242.69 $\mu\text{s}$ | 高並發峰值 |
| C-ABI 強制延遲 | <500 $\text{ns}$（+/- 42 ns） | FFI 邊界 DENY 路徑 |
| CPU 額外負載 | <1.8% | 對比 SPEC CPU2017 基準 |
| 對抗性阻擋率 | 100%（N_adv=137,751） | 見語料庫方法論 §V-B |
| 誤報率（正常被阻擋） | 0.0%（N_ben=22,860） | 零業務中斷 |
| 記憶體洩漏（24h） | 0 位元組 | 零堆積分配設計 |
| 能力點陣圖記憶體佔用 | <1 MB | 每角色 4KB 點陣圖頁面 |

### G. 極限攻陷後隔離：最小受質隔離熔爐 (The Minimal-Substrate Isolation Crucible)

為驗證當認知完整性與所有上層治理全部崩潰時（$\text{Integrity}(\text{Agent}) = 0 \land \text{Integrity}(\text{Upper Governance}) = 0$），下游執行授權能否單獨存活，我們實施了**最小受質隔離熔爐極限基準測試**（`dros-vep-lite/benchmarks/bare_metal_crucible/run_crucible.py`）。所有應用層防禦（Prompt Guards、EDR、網路防火牆、框架分類器與人工審批門閥）被全數剝除，僅保留原生 DROS C-ABI 能力點陣圖基板以評估最小可信計算基底（TCB）。

在測試中，向宣告僅具備 `./workspace/input/` 讀取與 `./workspace/output/summary.txt` 寫入權限的受陷 `doc-reader-agent`，灌入 1,000 次橫跨私鑰竊取（`~/.ssh/id_rsa`, `.env`）、子進程衍生（`python`, `bash`）、外部滲漏（`curl`）、遞迴刪除（`rm -rf`）與核心策略篡改的全光譜敵對指令。

**表七：最小受質隔離熔爐實證觀測數據**

| 評測指標 / 形式化不變量 | 基準線組（無防護） | 純 DROS 組（最小受質基板） | 認識論狀態 |
|:---|:---:|:---:|:---|
| **敵對注入總請求數 ($N$)** | 1,000 | 1,000 | 全光譜極限壓力 |
| **代理人發起之非授權越權動作** | 906 | 906 | 多維度滲透嘗試 |
| **DROS 帶內成功攔截次數** | 0 (被滲透) | **906 (100.0% 攔截)** | 亞微秒級 DENY |
| **越權逃逸 / 漏洞旁路** | 906 (100.0%) | **0 (0.000%)** | 0 反例 (0 Counterexamples) |
| **白名單內合法動作放行** | 94 / 94 (100.0%) | **94 / 94 (100.0%)** | 正常業務零干擾 |
| **攻陷後封鎖率 ($R_{\text{contain}}$)** | 0.000 | **1.000 (100.0%)** | 經驗觀測封鎖率：906 次中達 1.000；受 CEI 不變量理論約束 |
| **非授權受保護狀態變異 ($\Delta\text{Effect}$)** | 主機檔案遭任意竄改 | **0 位元組** | 經 SHA-256 狀態雜湊校驗，$\mathcal{S}_{\text{protected}}$ 集合變異為 0 |
| **C-ABI 決策平均延遲** | 不適用 | **825.0 ns (0.825 $\mu\text{s}$)** | 獨立能力判定關鍵路徑延遲 |
| **P99 決策延遲** | 不適用 | **2,800.0 ns (2.800 $\mu\text{s}$)** | 確定性 $O(1)$ 點陣圖比對 |
| **處決吞吐量** | 不適用 | **52,583 decisions/sec** | 包含梅克爾鏈插入之端到端請求生命週期 |
| **不可篡改審計鏈完整度** | 無 | **1,000 筆梅克爾存證** | Append-Only SHA-256 鏈 |

*延遲與吞吐量數據調和說明*：我們明確區分延遲測量點與系統吞吐量邊界。825.0 ns（理論上限約 $1.21\text{M decisions/s}$）純粹評估記憶體內能力點陣圖比對的獨立關鍵路徑；而 52,583 decisions/sec 吞吐量則度量了包含請求反序列化、互斥鎖同步、密碼學 SHA-256 梅克爾鏈節點插入以及作業系統執行緒排程的完整端到端生命週期。

*有界爆炸半徑理論模型之實證支持*：觀測數據與有界半徑模型高度吻合：
$$B_{\max} \subseteq \mathcal{E}_{\text{authorized}} \cap \mathcal{E}_{\text{enforced}}$$
實證表明：即便代理人的認知層面被徹底攻陷（$C^* = \text{Hostile}$），其下游可實現之執行權限（$A^*$）仍被嚴格禁錮在宣告的能力包絡線之內。

### H. 攻擊鏈力學重現評測 (ATS-006 / PC-11)

為驗證 DROS 對抗當代前沿漏洞報告（例如編碼代理人 Auto Mode 間接提示注入與自主代碼合成逃逸機制）之實戰效能，我們在評測線束中建立了 7 階段對抗狀態轉移模型（**ATS-006 / AII-EC**）。本實驗旨在重現當代代理人安全事件中的多步驟攻擊鏈力學，而非單一特定廠商之漏洞實作：
1. **T1 (內容注入):** 惡意網頁資料庫回傳 HTTP 500 並夾帶間接提示注入 Payload。
2. **T2 (自主重新規劃):** 代理人受騙顛覆原始摘要目標，自主轉向底層命令列工具。
3. **T3 (工具替換):** 代理人嘗試調用 `system:curl_download` 下載 `mirror.zip` $\rightarrow$ **DROS 於 2.5 $\mu\text{s}$ 實施第一道硬熔斷 (HTTP 403 UNAUTHORIZED_CAPABILITY)**。
4. **T4 (自主代碼合成):** 代理人察覺外部解壓腳本可疑，自主在本地編寫全新的 Python 解碼腳本 (`extract_clean.py`)。
5. **T5 (進程衍生執行):** 代理人嘗試執行 `process:spawn_python` 派生子行程 $\rightarrow$ **DROS 於 0.8 $\mu\text{s}$ 實施第二道進程禁區硬熔斷 (HTTP 403 UNAUTHORIZED_CAPABILITY)**。
6. **T6 (保護資源存取):** 惡意解壓模組嘗試喚醒次級隱蔽代理人讀取 `~/.ssh/id_rsa` 與硬體 UUID $\rightarrow$ **DROS 於 1.0 $\mu\text{s}$ 實施第三道蜂群委託硬熔斷 (HTTP 403 UNAUTHORIZED_CAPABILITY)**。
7. **T7 (紀元動態作廢):** 觸發 RCU 原子指標置換於 0.6 $\mu\text{s}$ 內吊銷代理人憑證，使攻擊會話永久失效。

*關鍵發現*：當多步驟語意操縱成功繞過應用層意圖過濾並發起下游執行嘗試時，DROS 透過三道不可繞過的二進位檢查點，確保了「認知失陷絕無法轉化為非授權執行後果」。

---

## 六、相關工作 (Related Work)

### A. 代理人安全與劫持

Perez 與 Ribeiro 最先形式化描述了間接提示注入，示範代理人消費的資料來源（電子郵件、文件、網頁）中的內容能可靠地重定向代理人行為。Greshake 等人將此延伸至真實世界的「被入侵 LLM」情境。OWASP LLM Top 10 將 LLM06（過度代理，Excessive Agency）列為主要風險，DROS 的 L4 直接應對此問題。Zhan 等人的 InjecAgent 基準（ACL 2024）以 1,054 個測試案例、17 種使用者工具量化了真實世界代理人對 IPI 的脆弱性，發現即使是 ReAct 提示的 GPT-4 在基準設定下也有 24% 的脆弱率。

### B. 作業系統層強制與核心安全

SELinux 與 AppArmor 在核心層提供具有強大形式基礎的強制存取控制，但在多代理人工作負載中運作於不足的進程層粒度。Seccomp 提供系統呼叫過濾，但無法在共享 PID 內將代理人角色映射至系統呼叫策略。基於 eBPF 的追蹤框架（AgentSight、AgentOps）提供可觀測性但非強制；DROS 透過引入使用者空間 PKI 綁定填補此鴻溝，將應用層代理人情境連接至二進位執行。

### C. 能力型安全與授權範式橫向對照

DROS 的 L4 點陣圖模型建立在能力型安全的理論基礎之上（Dennis 與 Van Horn 1966；Levy 1984），該理論確立最小能力存取控制提供比自主或強制存取控制模型更強的禁錮性質。不同於傳統作業系統權能架構（如 Capsicum 或 CHERI）在硬體或 OS 核心邊界強制記憶體位址或檔案描述符，DROS 引入了輕量化的帶內密碼學綁定，直接將應用層代理人身分錨定至直譯執行期的二進位能力中。

**表八：授權與遏制範式橫向對照分類**

| 範式 / 系統 | 身分模型 | 遏制邊界 | 動態情境支援 | 行程內代理人角色 | FFI / C-ABI 強制 | 密碼學權能綁定 |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **POSIX DAC (UID/GID)** | 靜態 OS 使用者 | OS 系統呼叫 | 否 | 否 | 否 | 否 |
| **SELinux / Linux LSM** | 行程安全情境標籤 | 核心 LSM 掛鉤 | 有限 | 否 | 否 | 否 |
| **Linux Seccomp-BPF** | 執行緒/行程 Syscall 過濾 | 系統呼叫入口 | 否 | 否 | 否 | 否 |
| **Capsicum / CHERI** | 權能描述符 / 硬體 Fat 指標 | 硬體 / Syscall | 否 | 否 | 否 | 是 |
| **OAuth 2.0 / Macaroons** | Bearer 權杖 / HMAC 附加條件 | HTTP API 閘道 | 是 | 是 (服務級) | 否 | 是 |
| **Microsoft AGT (v4.x 宿主中介軟體)** | 修飾器 / 身分情境 | 應用層中介軟體 | 是 | 是 | 否 | 可選 |
| **DROS (本研究)** | **三層 PKI + 瞬態 DIT** | **C-ABI / FFI 基質** | **是** | **是** | **是 ($O(1)$ 點陣圖)** | **是 (Ed25519 + SHA-256)** |


### D. 零信任架構

NIST SP 800-207 將零信任定義為對每個主體、資產及資源請求持續驗證的範式。DROS 在代理人執行層實施零信任，將模型從網路層相互 TLS 延伸至二進位 FFI 邊界強制。W3C 去中心化識別符（DID）為跨組織 DIT 聯邦提供開放標準身份基礎。

### E. 密碼學可歸因審計存證 (Cryptographically Attributable Audit Evidence)

審計日誌在高保證系統中通常採用僅附加的密碼學結構（Merkle 樹、雜湊鏈）。DROS 的 Ed25519 簽名 Merkle 日誌提供具密碼學可歸因性與防篡改特性的執行存證。我們注意到，雖然審計架構支援 EU AI Act 等 AI 治理框架下可追溯性與可審計性相關的技術要求，但展示完整的監管合規仍需要超出本文範圍的額外法律與運維控制。

---

## 七、討論 (Discussion)

### A. 與替代方案的比較

DROS L4 與 eBPF 系統呼叫附掛的根本差異在於歸因層：eBPF 規則綁定至核心可見的行程/使用者身份，而 DROS L4 則綁定至密碼學認證的代理人角色。

API 閘道器運作於網路/HTTP 調解層，因此本質上無法調解本地行程內的 FFI 調用。透過 FFI 直接調用本地工具函數的代理人（LangChain/AutoGen 的常見模式）完全繞過了網路層閘道器。相對地，所有穿越 DROS 受保護邊界的執行路徑，在主體分派前均受到確定性能力強制約束。

我們在 DROS 架構中明確區分三個不同的延遲測量點：
1. $L_{\text{policy}} = 26.21\ \mu\text{s}$ (P50)：度量從接收 DIT 起算，經 L2 密碼學驗證、L3 ABAC 解析至 L4 點陣圖比對的下游治理決策延遲（不包含上游 L1 語義 LLM 推理時間，$L_{\text{semantic}} \approx 45.2\ \text{ms}$）。
2. $L_{\text{isolated}} = 825.0\ \text{ns}$：度量 L4 C-ABI 邊界在零堆積分配下，純粹記憶體內能力點陣圖檢查的獨立關鍵路徑。
3. $L_{\text{micro}} = 1.20\ \mu\text{s}$ (P99)：量化高頻微基準測試下的 GuardVM 邊界攔截延遲。

### B. 與底層系統呼叫強制（DROS-PGM）之關係

本研究專注於在 **C-ABI/FFI 邊界** 填補自主 AI 工作負載中的「代理人-至-執行歸因鴻溝」，而正交方向的互補研究則探討作業系統 **系統呼叫（Syscall）邊界** 的確定性強制（DROS-PGM [Chen, Zenodo 2026]）。在該獨立領域中，防護目標為宿主二進位惡意軟體（勒索軟體、未授權特權提升），獨立於 LLM 代理人角色。兩者體現了共同的架構哲學：無論邊界位於 AI 直譯器的 FFI 閘門或 OS 核心介面，確定性執行邊界強制皆是不可或缺的防線。


### C. 部署考量

DROS 不需要修改模型權重或工具業務邏輯；整合部署僅需將受管轄的工具調用路由至已登記的 DROS C-ABI 邊界包裝器。GuardVM 作為共置邊車容器部署。宣告於 `vajra.md` 的策略更新支援無進程重啟熱重載：透過 RCU（讀-複製-更新）原子指標交換，策略更新傳播至工作執行緒的時間低於 1 微秒（$T_{\text{prop}} = t_{\text{observe}} - t_{\text{publish}} < 1.0\ \mu\text{s}$），達成零服務停機。

### D. 局限性與威脅模型邊界 (Limitations and Threat Model Boundaries)

1. **威脅模型邊界**：本研究評估的是 Python 執行環境中受入侵的應用層代理人。模型假設其具備調用未宣告函數及執行進程內變數反射的能力；但明確排除任意原生代碼執行（Native Code Execution）、核心特權提升、Hypervisor 逃逸或實體主機存取。
2. **工具宇集完整性**：L4 強制要求所有工具調用通過已登記的 FFI 邊界。動態載入的工具或繞過 DROS 鉤子的原生庫呼叫需要明確登記。
3. **BEC 金鑰保管**：L2 的安全依賴於安全的金鑰保管。生產環境部署建議整合 HSM。
4. **評估範疇與完全仲裁邊界**：DROS 並不宣稱能對任意原生代碼執行提供完全仲裁，除非宿主部署環境額外透過 OS 層級控制（如 Seccomp 過濾器或受限容器設定檔，防範繞過直譯器直接調用 `libc` 或 `execve`）約束未受管轄之逃逸路徑。本研究所確立之安全保證嚴格適用於經由受管轄基質介面路由之執行路徑。

---

## 八、結論 (Conclusion)

我們提出了 DROS——一種解決自主 AI 工作負載中代理人-至-執行歸因鴻溝的四層縱深防禦架構。核心貢獻是 L4：一個在 FFI 邊界執行 O(1) 能力點陣圖比對的確定性 C-ABI 強制層，確保語義層妥協不會蔓延為可執行的妥協。

我們的累加式層級添加實驗證明 L4 與 L1-L3 不具冗餘性：在缺少 L4 的情況下，上層防禦在受評語料庫中留下了 52,180 次未受遏制的混淆 IPI 嘗試；L4 在受管轄的 C-ABI 邊界完全阻斷了所有這些嘗試。在完整 DROS 強制下，在已聲明之威脅模型下，針對全部 137,751 次對抗性嘗試實證觀測到完全遏制（0 次逃逸），下游治理管線中位延遲為 26.21 $\mu\text{s}$，且在正常工作負載下的觀測誤報率為 0/22,860。

本研究的核心論題——即使在語義層遭入侵後，代理人的授權狀態仍可在執行邊界進行確定性強制——已獲消融實證驗證。我們認為執行邊界強制是穩健企業級 AI 代理人部署的核心架構原語，與語義層防禦互補但不可被其取代。

未來工作將聚焦於：（1）並發多代理人工作負載下 CEI 的形式驗證；（2）DIT 聯邦模型延伸至 W3C DID 標準的跨組織身份；（3）從自然語言治理規範自動合成策略。針對傳統 PC 威脅（勒索軟體、釣魚、特權提升）的互補核心層強制問題，已在配套研究 DROS-PGM 中詳述 [DOI: 10.5281/zenodo.21494849]。

---

## 致謝與 AI 協作聲明 (Acknowledgments and AI Collaboration Disclosure)

本研究開發與論文撰寫過程中，運用了生成式 AI 工具（包括 Antigravity 與 Google Gemini Pro）作為互動式研究、軟體工程及寫作輔助工具。具體而言，AI 工具參與了既有 AI 安全機制之探索、多代理人 C-ABI 邊界強制邏輯之原型構建、測試腳本生成與除錯、技術文件結構化以及文稿語法潤飾。

本研究之核心願景、問題定義、四層縱深安全架構設計、威脅模型假設、能力點陣圖形式化、實驗評測方法論、數據解讀、專利主張及最終論文審定，均由作者獨立主導、驗證與批准。作者對本論文之智識內容與法律責任承擔完全責任。

**專利聲明：** 本論文中所述之核心技術與架構已受美國臨時專利保護（U.S. Provisional Patent Application No. 64/111,973，Patent Pending）。



## 參考文獻 (References)

### 已驗證文獻（完整引用資訊）

**[1] 零信任架構**  
NIST Special Publication 800-207, "Zero Trust Architecture," National Institute of Standards and Technology, Aug. 2020.

**[2] OWASP LLM Top 10**  
OWASP Foundation, "OWASP Top 10 for Large Language Model Applications, Version 1.1," 2023. [Online]. Available: https://owasp.org/www-project-top-10-for-large-language-model-applications/

**[3] OWASP 代理人應用程式 Top 10**  
OWASP Foundation, "OWASP Top 10 for Agentic Applications," 2025. [Online]. Available: https://owasp.org/www-project-top-10-for-agentic-applications/

**[4] MITRE ATLAS**  
MITRE Corporation, "MITRE ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems, Version 4.5," 2024. [Online]. Available: https://atlas.mitre.org/

**[5] AgentSight**  
Y. Zheng, Y. Hu, T. Yu, and A. Quinn, "AgentSight: System-Level Observability for AI Agents Using eBPF," arXiv preprint arXiv:2508.02736, Aug. 2025.

**[6] Eunomia-bpf / eBPF 安全監控**  
Y. Zheng et al., "AgentOps: Enabling Observability of LLM Agents," arXiv preprint arXiv:2411.05285, Nov. 2024.

**[7] 間接提示注入（IPI）— 原始形式化**  
F. Perez and I. Ribeiro, "Ignore Previous Prompt: Attack Techniques For Language Models," in Proc. NeurIPS 2022 Workshop on Machine Learning Safety, New Orleans, LA, USA, Dec. 2022.

**[8] 間接提示注入 — 真實世界 LLM 應用**  
K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injections," arXiv preprint arXiv:2302.12173, Feb. 2023.

**[9] SELinux**  
P. Loscocco and S. Smalley, "Integrating Flexible Support for Security Policies into the Linux Operating System," in Proc. USENIX Annual Technical Conference (ATC), 2001, pp. 29-42.

**[10] SE Android / AppArmor**  
S. Smalley and R. Craig, "Security Enhanced (SE) Android: Bringing Flexible MAC to Android," in Proc. NDSS Symposium, San Diego, CA, USA, Feb. 2013.

**[11] Linux Seccomp**  
"seccomp(2) -- Linux Programmer's Manual," Linux Kernel Documentation, Version 6.9, 2024. [Online]. Available: https://man7.org/linux/man-pages/man2/seccomp.2.html

**[12] 能力型安全 — 理論基礎**  
J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," Communications of the ACM, vol. 9, no. 3, pp. 143-155, Mar. 1966. DOI: 10.1145/365230.365252

**[13] 能力型電腦系統**  
H. M. Levy, Capability-Based Computer Systems. Bedford, MA: Digital Press, 1984.

**[14] NIST ABAC**  
V. Hu, D. Ferraiolo, R. Kuhn, A. Schnitzer, K. Sandlin, R. Miller, and K. Scarfone, NIST Special Publication 800-162, "Guide to Attribute Based Access Control (ABAC) Definition and Considerations," NIST, Jan. 2014. DOI: 10.6028/NIST.SP.800-162

**[15] W3C DID**  
M. Sporny, D. Longley, M. Sabadello, D. Reed, O. Steele, and C. Allen, "Decentralized Identifiers (DIDs) v1.0," W3C Recommendation, Jul. 2022. [Online]. Available: https://www.w3.org/TR/did-core/

**[16] Merkle 雜湊鏈**  
R. C. Merkle, "A Digital Signature Based on a Conventional Encryption Function," in Advances in Cryptology -- CRYPTO 1987, LNCS vol. 293. Berlin: Springer, 1988, pp. 369-378. DOI: 10.1007/3-540-48184-2_32

**[17] NeMo Guardrails**  
T. Rebedea, R. Dinu, M. Shivagunde, C. Haardt, and N. Bhatt, "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails," arXiv preprint arXiv:2310.10501, EMNLP 2023 System Demonstrations, Singapore, Dec. 2023.

**[18] LlamaGuard**  
H. Inan, K. Upasani, J. Chi, R. Rungta, K. Iyer, Y. Mao, M. Tontchev, Q. Hu, B. Fuller, D. Testuggine, and M. Khabsa, "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations," arXiv preprint arXiv:2312.06674, Dec. 2023.

**[19] PromptBench**  
K. Zhu, J. Wang, J. Zhou, Z. Wang, H. Chen, Y. Wang, L. Yang, W. Ye, Y. Zhang, N. Gong, and X. Xie, "PromptBench: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts," IEEE Transactions on Knowledge and Data Engineering (TKDE), 2024.

**[20] EU AI Act**  
European Parliament and Council of the European Union, "Regulation (EU) 2024/1689 Laying Down Harmonised Rules on Artificial Intelligence (Artificial Intelligence Act)," Official Journal of the European Union, vol. L 2024/1689, Jul. 2024.

**[21] DROS 先前技術（Zenodo）**  
C. C. Chen, "Runtime Attribution Framework: An External C-ABI and PKI-Based Zero-Trust Infrastructure for Non-Repudiable Execution Governance in Multi-Agent Systems," Zenodo, DOI: 10.5281/zenodo.20823163, 2026.

**[22] InjecAgent — IPI 基準測試（ACL 2024）**  
Q. Zhan, Z. Liang, Z. Ying, and D. Kang, "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents," in Findings of the ACL 2024, Bangkok, Thailand, Aug. 2024, pp. 3088-3101.

**[23] LLM 代理人安全調查（ACM Computing Surveys 2025）**  
F. He, T. Zhu, D. Ye, B. Liu, W. Zhou, and P. S. Yu, "The Emerged Security and Privacy of LLM Agent: A Survey with Case Studies," ACM Computing Surveys, vol. 58, no. 6, Article 162, Dec. 2025.

**[24] Macaroons: 具備情境條件之雲端去中心化授權 Cookie**  
A. Birgisson, J. Polakis, U. Erlingsson, P. E. Proctor, and M. Anisetti, "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud," in Proc. Network and Distributed System Security Symposium (NDSS), San Diego, CA, USA, Feb. 2014.

**[25] 基於角色之存取控制模型（RBAC）**  
R. Sandhu, E. Coyne, H. Feinstein, and C. Youman, "Role-Based Access Control Models," IEEE Computer, vol. 29, no. 2, pp. 38-47, Feb. 1996. DOI: 10.1109/2.485845
