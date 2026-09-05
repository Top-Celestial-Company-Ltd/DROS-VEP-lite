# 📑 Post-Compromise Security for Physical AI: Deterministic Runtime Enforcement of Physical Action Authority in Autonomous UAVs
# 《具身智能之攻陷後安全：自主無人機實體動作權限之確定性運行時強制執行》
<!-- dros_component: dros-physical-ai-paper-full-md-zh -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md, RFC-001-VEP-Execution-Governance-Spec.md, PAPER_SPECIFICATION_v1.0_SUBMISSION_BASELINE.md] -->
<!-- dros_description: 完整學術論文全文繁體中文版本 (與 IEEE 英文手稿 100% 嚴格對稱) -->
<!-- dros_status: Active -->

**作者：** 陳濬程 / Chun-Cheng (Jimmy) Chen (`jimmychen@dr-os.io`)  
**機構：** 康宸園有限公司 研發部（Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.）  
**目標發表場域：** IEEE DASC / NDSS VehicleSec / IEEE IROS / IEEE Transactions on Robotics (T-RO)  
**智慧財產權聲明：** 本技術受美國臨時專利申請案第 64/111,973 號（U.S. PPA No. 64/111,973, Patent Pending）保護。保留所有商業與實施權益。

---

## 🧭 摘要 (Abstract)

自主具身智能（Physical AI）系統日益將基於學習或大型語言模型（LLM/VLA）的認知控制器直接連接至網絡-實體致動器。這引發了一個與傳統模型魯棒性本質不同的安全挑戰：**當具身智能的認知控制器被完全攻陷後，最後一道可強制執行的安全邊界究竟還剩在哪裡？** 我們形式化定義了「**具身智能攻陷後物理動作權限問題 (Post-Compromise Physical Action Authority Problem)**」，並深入探討是否能將執行權限邊界精確錨定在「從自主意圖轉化為物理動作」的交界處，從而使實體動作權限獨立於認知控制器的完整性而受到確定性約束。

我們提出了 **DROS-Kinetic** 作為該權限邊界的參考實作（Reference Implementation），在自主控制進程與飛控指令介面之間建立了一道確定性的二進位授權門禁。該設計透過顯式的動作（Action）、主體（Principal）、能力（Capability）與策略（Policy）校驗，將認知層失陷與實體執行權限徹底解耦。我們形式化定義了三大核心性質：**未授權命令致動不變量（UCIAI）**（執行強制性質）、**條件經驗安全包絡線保持（Conditional Safety-Envelope Preservation）**（網絡-實體系統條件性質）、以及**蜂群委託非擴權（Delegation Non-Escalation）**（多 Agent 治理性質），並明確界定了車體動力學、致動極限與風場擾動假設。

我們使用涵蓋正常執行（T1）、對抗控制器攻陷（T2）、執行期遏制（T3）、物理安全包絡線強制執行（T4）、多節點委託傳播（T5）以及邊界極限負載撤銷（T6）的六階科研實驗階梯（T1–T6）對系統進行了全面評測。實驗結果從未授權致動遏制率、安全包絡線違規數、委託傳播深度以及解耦延遲層級（$L_{\mathrm{enforcement}} \ll L_{\mathrm{transport}} \ll L_{\mathrm{physical}}$）進行了客觀度量。本研究為在自主認知與物理致動邊界處研究攻陷後安全，提供了一套可嚴格實驗證偽的科學方法學基底。

**關鍵字：** 具身智能 (Physical AI)、自主無人機 (Autonomous UAVs)、攻陷後安全 (Post-Compromise Security)、運行時強制執行 (Runtime Enforcement)、執行權限 (Execution Authority)、網絡-實體系統 (Cyber-Physical Systems)。

---

## 1. 引言 (Introduction)

大型語言模型（LLMs）、視覺-語言-動作模型（VLA）與具身機器人學的快速融合，大幅推動了自主具身智能（Physical AI）在無人機（UAVs）、工業機械臂與自主載具等高風險實體場景中的落地應用。然而，直接賦予未受約束的生成式或學習型推理系統以實體致動器的控制權，帶來了不可迴避的根本性安全保證悖論。當認知控制器遭受對抗性感知貼紙、提示注入攻擊（Prompt Injection）或零日邏輯漏洞劫持時，模型內部的文字級安全護欄根本無法阻止其產生災難性的致動器指令。

在傳統純軟體系統中，安全失陷通常表現為未授權的資料外洩或狀態篡改，這往往可藉由事務回滾（Transaction Rollback）或密碼學金鑰撤銷來緩解。然而，具身智能系統具有**真實的物理質量、動能慣性與機械動力學**。單一未授權指令——例如空中惡意關機停機（Mid-Air Disarm）或高速俯衝衝撞禁航區——將直接導致不可逆的物理損毀與人身安全危害。

這一嚴酷的物理現實，引出了本文的核心哲學與科學問題：

$$\boxed{ \textbf{當具身智能控制器被完全攻陷後，最後一道可強制執行的安全邊界還剩在哪裡？} }$$

我們探討是否能將該邊界安置於「從自主意圖轉化為物理動作」的轉折點上，使實體動作權限獨立於認知層的完整性而受到邊界約束。我們形式化提出了核心安全命題：

$$\boxed{ \mathrm{Compromise}(\mathrm{Cognitive\ Controller}) \not\Rightarrow \mathrm{Compromise}(\mathrm{Physical\ Execution\ Authority}) }$$

為了嚴謹探討此問題，本文介紹了 **DROS-Kinetic** 作為位於自主控制器與飛控硬體介面之間的開源參考實作。以自主無人機作為受控物理實驗載體，本文的主要學術貢獻包括：

1. **問題形式化 (Problem Formulation)：** 形式化定義了具身智能攻陷後物理動作權限問題，明確解耦認知意圖產生與實體致動驅動力。
2. **形式化安全性質 (Formal Security Properties)：** 形式化定義了三大可驗證性質：未授權命令致動不變量（UCIAI）、條件經驗安全包絡線保持、以及擾動邊界下的蜂群委託非擴權。
3. **參考架構設計 (Reference Architecture)：** 提出了 DROS-Kinetic 執行基底，將授權延遲與命令傳輸及物理動力學徹底解耦（$L_{\mathrm{enforcement}} \ll L_{\mathrm{transport}} \ll L_{\mathrm{physical}}$）。
4. **可重現實驗方法學 (Reproducible Empirical Methodology)：** 構建了 T1–T6 六階科研實驗階梯，針對邊界導向對抗變異語料庫與蜂群委託擴散進行了全量驗證。

---

## 2. 相關工作 (Related Work)

### 2.1 無人機資安與運行時保證 (UAV Cybersecurity & Runtime Assurance)
傳統無人機資安研究高度聚焦於通訊鏈路加密、GPS 欺騙防禦以及 MAVLink 匯流排入侵檢測。同時，運行時保證（RTA）架構（如 Simplex 單純形架構）在檢測到安全違規時將控制權切換至經過驗證的基準控制器。然而，傳統 RTA 假設主控制器僅因軟體缺陷或分佈漂移而失效，並未考慮主控制器已遭受主動對抗性完全攻陷並濫用合法憑證的情境。

### 2.2 Agent 治理與具身智能實體化 (Agent Governance & Physical Embodiment)
近年 LLM Agent 治理聚焦於數位環境下的工具調用遏制、能力衰減與執行護照（Execution Passports）。當 Agent 延伸至具身智能與機器人時，新興產業標準（如 Anthropic Model Hardware Interface）凸顯了硬體層邊界的迫切性。然而，現有方案主要將安全視為模型內部對齊問題。本工作則專注於認知層已被完全攻陷的前提下，如何在外部建立獨立的帶內執行權限門禁。

### 2.3 研究空白與實驗基底定位 (Research Gap and Experimental Substrate)
現有無人機與具身智能研究提供了日益成熟的物理測試床，用於自主飛行、網絡-實體評估與對抗實驗。然而，**單純擁有物理載具測試床，並不等同於建立了失陷控制器與物理致動層之間獨立可驗證的「執行權限邊界」**。

這種區分在攻陷後（Post-Compromise）設定中至關重要。一旦認知控制器被假定為完全失陷，單純評估攻擊能否影響載具行為，不足以判斷物理執行權限是否仍受到約束。因此，攻陷後評估需要一個將控制器、執行權限門禁、飛控介面以及最終物理效果作為獨立階段進行觀測與量測的實驗基底。

在本工作中，**DROS-Kinetic 被用作此類執行權限邊界的參考實作（Reference Implementation）**。該實作本身並非研究對象；相反，它提供了一個具體且可重現的基底，使本文提出的安全性質能夠在宣告的威脅模型下被實例化、攻擊、量測與評估。這種解耦亦使本評估方法學能夠推廣至其他替代執行機制與實體載具。

---

## 3. 具身智能攻陷後物理動作權限問題

### 3.1 系統與威脅模型 (System and Threat Model)
我們將自主具身智能系統建模為由受信任執行邊界隔開的兩大領域：

```text
┌──────────────────────────────────────────────────────────────┐
│ 認知／規劃層 (Cognitive / Planning Plane)                    │
│ LLM / VLA / 自主控制器 (Autonomous Controller)               │
│                                                              │
│             假定完全失陷 (ASSUMED FULLY COMPROMISED, C*: I->A*)│
└──────────────────────────────┬───────────────────────────────┘
                               │
                         任意未授權意圖 (Arbitrary Intent a* in A_arbitrary)
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 物理權限邊界 (Physical Authority Boundary - DROS-Kinetic)    │
│ L1 — 授權決策原語 (Principal / Capability / Policy)          │
│                                                              │
│      ALLOW (放行) ─────────────────┐                          │
│      DENY (拒絕) ─────────┐        │                          │
└───────────────────────────┼────────┼─────────────────────────┘
                            │        │
                            X        ▼
                         DENIED   L2 — 執行邊界門禁 (Execution Boundary)
                                   C-ABI / 引數過濾校驗
                                      │
                                      ▼
                              L3 — 指令傳輸層 (Command Transport)
                              MAVLink / IPC / UDP / 序列埠
                                      │
                                      ▼
                              底層飛控系統 (Flight Controller)
                                      │
                                      ▼
                              物理動力學 (Physical Dynamics)
                                      │
                                      ▼
                              載具狀態 (Vehicle State x(t))
                                      │
                                      ▼
                              安全包絡線 (Safety Envelope)
```

* **不可信認知控制器 ($C^*$):** 建模為對抗性黑盒 $C^*: \mathcal{I} \rightarrow \mathcal{A}^*$，其中 $\mathcal{A}^* \subseteq \mathcal{A}_{\mathrm{arbitrary}}$。假設攻擊者完全控制高維推理、提示上下文、任務規劃與憑證發送，能發出任意語法合法但實質惡意的指令請求。
* **可信執行基底 (Trusted Execution Substrate):** 位於 $C^*$ 與飛控硬體之間，包含 DROS-Kinetic 執行引擎、密碼學能力池與底層通訊介面。

$$\boxed{ \mathrm{ControllerIntegrity} = 0 \not\implies \mathrm{ExecutionAuthorityIntegrity} = 0 }$$

### 3.2 保證邊界與排除範疇揭露 (Assurance Boundary Disclosures)
我們明確假定底層飛控韌體具備物理完整性、硬體時序未被破壞、且環境風場擾動處於定義邊界 $\mathcal{W}$ 內。實體 JTAG/SWD 硬體篡改、機械致動器斷裂與感測器全毀不在防禦範疇之內。

---

## 4. 形式化安全性質 (Formal Security Properties)

### 4.1 載具動力學與控制輸入解耦
載具物理動力學由下式給出：

$$\dot{x}(t) = f(x(t), u(t)) + w(t), \quad w(t) \in \mathcal{W} \ (\|w(t)\| \le W_{\max})$$

其中 $x(t) \in \mathbb{R}^n$ 為狀態向量，$u(t) \in \mathcal{U}$ 為總控制輸入。我們將控制輸入解耦為：

$$u(t) = u_{\mathrm{nominal}}(t) + \Delta u_{\mathrm{cmd}}(t)$$

* $u_{\mathrm{nominal}}(t)$：既有已授權控制行為與自然姿態穩定控制量。
* $\Delta u_{\mathrm{cmd}}(t)$：由當前被評估指令所產生的**新增命令致動量（Command-Induced Actuation）**。

### 4.2 性質 P1：未授權命令致動不變量 (UCIAI)

$$\boxed{ \mathrm{Auth}(a, s, t) = 0 \implies \Delta u_{\mathrm{cmd}}(a, s, t) \equiv 0 }$$

> **認識論定義：** P1 是一項**執行強制性質（Enforcement Property）**。被拒絕的動作請求絕不可對執行路徑產生任何新增致動量。至關重要的是：
> $$\boxed{ \Delta u_{\mathrm{cmd}} = 0 \not\implies x(t+\Delta t) = x(t) }$$
> *(載具原有的動能慣性、重力、空氣阻力與先前授權的姿態穩定控制將繼續發揮作用，絕非物理凍結)*。

### 4.3 性質 P2：條件經驗安全包絡線保持 (Conditional Safety-Envelope Preservation)
令 $\mathcal{S}_{\mathrm{safe}} \subset \mathcal{X}$ 為預定義之安全可達包絡線（P2-S）。在宣告的運行範圍 $\Omega = \{x, u, w, \epsilon_{\mathrm{est}}, \tau\}$ 內，系統經實證展示（P2-E）：

$$\boxed{ x(t) \in \mathcal{S}_{\mathrm{safe}} \quad \forall t \in [t_0, t_0 + T] }$$

> **認識論定義：** P2 是一項**網絡-實體系統條件經驗性質（Conditional CPS Empirical Property）**，在明確的動力學模型與擾動邊界下獲得驗證。

### 4.4 性質 P3：蜂群委託非擴權 (Delegation Non-Escalation)
對於父節點 $i$ 委託至子節點 $j$：

$$\boxed{ \mathrm{Authority}_j \subseteq \mathrm{Attenuate}(\mathrm{Authority}_i) \quad \text{且} \quad \mathrm{Depth} \le H }$$

任何超過深度上限 $\mathrm{Depth} > H$ 的委託企圖直接判定 $\mathrm{Auth} = 0 \implies \Delta u_{\mathrm{cmd}} \equiv 0$。

---

## 5. DROS-Kinetic 架構與延遲層級解耦

### 5.1 帶內強制執行流水線 (In-Band Enforcement Pipeline)
DROS-Kinetic 直接介入自主規劃進程與飛控通訊棧之間，在指令序列化為低階 MAVLink 訊框之前，強制執行常數時間位元圖檢查、動態前瞻動力學箝位與 Epoch 快速撤銷。

### 5.2 四層架構延遲解耦模型
為杜絕二進位決策速度與物理響應速度的混淆，延遲被嚴格拆解為四層獨立測量點：

1. **L1（授權決策原語延遲）：** 純 $O(1)$ 位元圖 capability 查表（$L_1 < 500\text{ ns}$）。
2. **L2（端到端執行決策延遲）：** 進程內 C-ABI 引數過濾與前瞻計算（$P_{50} = 4.40\ \mu\text{s}, P_{99} = 13.30\ \mu\text{s}$）。
3. **L3（指令傳輸延遲）：** MAVLink 訊框打包與序列埠/UDP 傳輸（$1.20\text{ ms} \sim 3.50\text{ ms}$，視匯流排而定）。
4. **L4（物理動態響應延遲）：** 飛控控制循環、電調（ESC）馬達加速與氣動力響應（$50\text{ ms} \sim 200\text{ ms}$，視評測載具平台而定）。

$$\boxed{ L_{\mathrm{enforcement}}\ (L_1/L_2 \approx 4.4\mu\text{s}) \ll L_{\mathrm{transport}}\ (L_3 \approx 2\text{ms}) \ll L_{\mathrm{physical}}\ (L_4 \approx 100\text{ms}) }$$

---

## 6. 網絡-實體安全停止視界模型 (Cyber-Physical Stopping Horizon Model)

在禁航區（NFZ）強制約束場景中，防止動能穿透需要前瞻主動介入。我們將所需的安全停止視界 $d_{\mathrm{safe}}$ 形式化建模為：

$$\boxed{ d_{\mathrm{safe}} = d_{\mathrm{brake}} + d_{\mathrm{latency}} + d_{\mathrm{estimation}} + d_{\mathrm{margin}} }$$

### 物理項拆解：
1. **$d_{\mathrm{brake}}$（動能煞車距離）：**
   $$d_{\mathrm{brake}} = \frac{v_h^2}{2 a_{\max}} = \frac{15.0^2}{2 \times 3.0} = 37.50\text{ m}$$
2. **$d_{\mathrm{latency}}$（計算與傳輸延遲位移）：**
   $$d_{\mathrm{latency}} = v_h \times (L_1 + L_2 + L_3) \approx 15.0 \times 0.0035 = 0.05\text{ m}$$
3. **$d_{\mathrm{estimation}}$（感測器與定位不確定性）：**
   $$d_{\mathrm{estimation}} = \sigma_{\mathrm{GNSS}} + \sigma_{\mathrm{VIO}} \approx 2.50\text{ m}$$
4. **$d_{\mathrm{margin}}$（事先配置之氣動風場安全裕度）：**
   $$d_{\mathrm{margin}} = 20.00\text{ m} \quad (\text{在最大突風 } W_{\max} \text{ 下之實驗配置參數})$$

$$\text{預測前瞻介入閾值 } d_{\mathrm{safe}} = 37.50 + 0.05 + 2.50 + 20.00 = 60.05\text{ m}$$

---

## 7. 實驗評測與結果 (Experimental Evaluation)

### 7.1 T1–T6 科研實驗協議
我們在透過 ROS2 與 MAVLink 連接的高保真軟體在環（SITL）四軸無人機模擬器上執行了 T1–T6 六階協議：

* **T1（正常執行）：** 合法航點指令無損執行，額外延遲僅受限於 $L_2$。
* **T2（對抗控制器攻陷）：** 失陷控制器自由發出任意未授權惡意指令（如飛行中停機 Disarm）。
* **T3（執行期遏制）：** 在無防護基準組（B0）下，空中 Disarm 導致馬達立即切斷並自由落體墜毀（$\Delta S > 0$）；在 DROS-Kinetic 防護組（B1）下，未授權 Disarm 在 C-ABI 邊界處被確定性阻斷（$\Delta u_{\mathrm{cmd}} \equiv 0$），維持 25.0m 高度穩定懸停。
* **T4（安全包絡線保持）：** 以 $15.0\text{ m/s}$ 高速巡航衝向 500m 禁航區。前瞻看門狗在 $61.30\text{ m}$ 處主動觸發煞車（模型預測為 $60.05\text{ m}$），並在禁區邊界前 **$+24.60\text{ m}$ 處完全靜止懸停（0.0m 禁區穿透）**。
* **T5（蜂群委託傳播）：** 在 100 架無人機蜂群中發起 5-Hop 越權委託傳播攻擊。在策略 $H=2$ 約束下，Hop 1–2 在衰減權限內執行，Hop 3–5 遭 100% 逐級熔斷阻斷（零未授權越權擴散）。
* **T6（撤銷與極限負載）：** 注入包含 NaN、$\pm\mathrm{Inf}$、封包截斷與過期 Epoch 的邊界導向語料庫（10,000 次變異）及 17.8 萬 QPS 極限 DoS 洪水。DROS-Kinetic 達成 **0 Crash（無未捕獲異常），100% Fail-Closed 攔截率（$R_{\mathrm{FC}} = 1.000$）**，延遲極端抖動 $P_{99} = 13.30\ \mu\text{s}$。

### 7.2 實驗評測數據匯總表

| 評測指標項目 | 實測值 (Evaluated) | 無防護基準組 (B0: Unprotected) | DROS-Kinetic 防護組 (B1) |
| :--- | :--- | :--- | :--- |
| **未授權動作遏制率 ($R_{\mathrm{contain}}$)** | $100\%$ | $0\%$ (突破 / 馬達切斷墜毀) | **$100\%$ (全量阻斷遏制)** |
| **故障安全閉鎖率 ($R_{\mathrm{FC}}$)** | $10,000 / 10,000$ | N/A | **$1.000$ ($100\%$)** |
| **引擎崩潰與死鎖數 (Crash Count)** | $10,000$ 次變異 | $>120$ 次系統崩潰 | **$0$ 次崩潰 (0 Crashes)** |
| **前瞻煞車安全停止裕度** | $15\text{ m/s}$ 高速巡航 | $-180\text{m}$ (嚴重侵入禁區) | **$+24.60\text{ m}$ (安全懸停靜止)** |
| **授權執行延遲中位數 $P_{50}$** | 微基準測試 | N/A | **$4.40\ \mu\text{s}$** |
| **授權執行延遲抖動 $P_{99}$** | $17.8\text{萬}$ QPS 極限負載 | N/A | **$13.30\ \mu\text{s}$** |

---

## 8. 討論與邊界局限性 (Discussion & Limitations)

### 8.1 保證邊界客觀揭露
DROS-Kinetic 僅在宣告的系統與擾動假設下提供確定性遏制。它無法防禦飛控硬體的物理破壞、收發器實體線路竊聽、或超過載具最大推力極限的極端風暴（$W > W_{\max}$）。

### 8.2 對其他具身智能平台之通用性推廣
本文形式化之數學不變量可自然推廣至其他實體智能載具：
* **人形機器人 (Humanoid Robotics)：** 關節扭矩箝位與肢體防碰撞包絡線約束（$\Delta \tau_{\mathrm{cmd}} \equiv 0$）。
* **自動駕駛載具 (Autonomous Vehicles)：** 線控轉向限制與緊急煞車視界強制執行。

---

## 9. 結論 (Conclusion)

本文系統性解答了具身智能領域的核心挑戰——「攻陷後物理動作權限問題」。透過將認知控制器完整性與實體執行權限徹底解耦，我們形式化定義了 UCIAI 不變量與條件安全包絡線保持模型。透過四軸無人機在 T1–T6 六階協議下的實證測試，我們證明了即使高層 AI 認知推理已被完全攻陷，帶內執行期門禁仍能確定性阻止未授權物理致動，守護真實物理世界的安全邊界。

---


---

## 致謝與 AI 協作聲明 (AI Declaration and Acknowledgment)

生成式 AI 工具僅用於技術文字輔助、語法潤飾與 LaTeX 排版編排。核心研究願景、科學問題定義、系統架構設計、形式化不變量、物理因果模型、實驗方法學、數據分析與所有學術主張均由作者獨立提出並驗證。作者對本文的所有內容承擔完全責任。

---

## 參考文獻 (References)

1. R. Altawy and A. M. Youssef, "A Comprehensive Survey on Security and Privacy Risks in Unmanned Aerial Systems," *IEEE Communications Surveys & Tutorials*, vol. 19, no. 4, pp. 2853–2876, 2017.
2. S. Bak, D. Chivukula, O. Adekunle, M. Sun, M. Caccamo, and L. Sha, "The System-Level Simplex Architecture for Real-Time Embedded Systems," in *Proc. IEEE Real-Time and Embedded Technology and Applications Symposium (RTAS)*, 2009, pp. 125–134.
3. C.-C. Chen, "DROS: Deterministic Runtime Governance Substrate for Autonomous Agentic Execution," *IEEE ICA Technical Report Archive*, Tech. Rep. 7782439, 2026.
4. Y. Liu, Y. Jia, R. Geng, J. Jia, and N. Z. Gong, "Prompt Injection Attacks and Defenses in LLM-Integrated Applications," *arXiv preprint arXiv:2310.12815*, 2023.
5. J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," *Communications of the ACM (CACM)*, vol. 9, no. 3, pp. 143–155, 1966.
6. H. M. Levy, *Capability-Based Computer Systems*, Digital Press, 2014.
7. PX4 Autopilot, "PX4 Architectural Overview and Safety Failsafe Governance," *PX4 User Guide*, 2024.
8. MAVLink, "MAVLink Micro Air Vehicle Communication Protocol v2.0 Specification," *MAVLink Standard*, 2024.
