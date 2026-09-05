# 🌐 DROS™ 官方全量技術與商業統一 FAQ 主庫 (Master FAQ Hub)
<!-- dros_component: dros-master-faq-hub -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0_ZH.md, DROS_SAFETY_AND_LEGAL_WARNINGS_ZH.md] -->
<!-- dros_description: 官方單一信任源 (Single Source of Truth) 全量 FAQ，同時驅動官網 (dr-os.io) 與正式發行商品包 -->
<!-- dros_status: Active -->

> **本庫定位：** DROS 官方單一信任源 (SSOT) 核心問答庫。  
> **同步目標：** 官網常見問題區塊 (`dr-os.io/faq`)、發行商品包 (`DROS_Commercial_Release_Specification_v1.0.zip`)、Gumroad 商店與技術客服知識庫。  
> **專利與標準：** U.S. Provisional Patent App. No. 64/111,973 · RFC-001 / RFC-010 · IEEE 6-Pillars

---

## 🧭 目錄 (Table of Contents)
* [一、 概念與架構定位 (Concept & Architectural Positioning)](#一-概念與架構定位-concept--architectural-positioning)
* [二、 核心安全與防禦能力 (Security & Defensive Invariants)](#二-核心安全與防禦能力-security--defensive-invariants)
* [三、 商業授權與收費邊界 (Licensing & Commercial Boundaries)](#三-商業授權與收費邊界-licensing--commercial-boundaries)
* [四、 企業部署與運維實施 (Enterprise Operations & Deployment)](#四-企業部署與運維實施-enterprise-operations--deployment)
* [五、 法規合規、專利與免責 (Legal, Patents & Compliance)](#五-法規合規專利與免責-legal-patents--compliance)

---

## 一、 概念與架構定位 (Concept & Architectural Positioning)

### Q1.1 什麼是「開放身份，在地治理 (Open Identity, Localized Governance)」？外部 Agent 持護照來訪會威脅企業嗎？
**A：完全不會！這正是 DROS 解決 Agentic Web 跨企業信任衝突的核心範式。**
* 外部 Agent 攜帶 RFC-010 護照 (`libdros-id`) 來訪時，僅提供其身分歸因 (Principal) 與發行簽章。
* **企業在地 GuardVM 網關保有 100% 的確定性執行裁量權**：企業在 VajraAgent 主控頁上，可直接為該外部護照設定在地 Capability Bitmaps (位元圖矩陣)。即使外部護照聲稱自己具備超級管理員權限，DROS 在 C-ABI 帶內層級 (26.1 μs) 依然僅允許其調用企業開通的特定 API。任何越權呼叫直接物理熔斷並返回 HTTP 403。

### Q1.2 DROS 提出的「6-Pillars 確定性治理」與傳統的 IAM / OAuth 或 API Gateway 有何本質區別？
**A：物理層 C-ABI 帶內硬熔斷 vs. 網路層軟邊界。**
* **超低延遲**：傳統 API Gateway 運作在 Out-of-band HTTP 網路層 (4ms~50ms)，DROS-6P 在物理層 C-ABI / eBPF 直接運作，平均決策延遲僅 **26.1 μs** (p99 = 29.8 μs)，效能提升數千倍。
* **密碼學證明**：內建 SHA-256 Merkle 雜湊稽核鏈與 Ed25519 簽章，產出具備不可否認性的法務級憑證。

### Q1.3 企業部署 DROS 需要修改原有的 AI Agent 程式碼 (如 LangChain / AutoGen) 嗎？
**A：完全不需要！零程式碼修改 ‧ 零系統停機。**
* DROS 採用外部 C-ABI 帶內攔截與開箱即用的 `libdros-id` SDK。
* 管理者透過宣告式策略合約 (`vajra.yaml`) 或 VajraAgent Web 主控台調整權限後，DROS 控制平面便會在微秒內完成熱加載 (Hot Reloading)，AI 員工運作零中斷。

---

## 二、 核心安全與防禦能力 (Security & Defensive Invariants)

### Q2.1 攻擊者若發動未知「零日漏洞 (0-Day) 提示注入」，DROS 能擋住嗎？
**A：100% 能擋住。**
* DROS 採用 **Default Fail-Closed（預設關閉 / 白名單）** 哲學。
* 無論攻擊 Payload 多麼新穎、如何繞過 LLM 認知，只要該 Agent 試圖調用未被明確授權的 API/Tool（例如客服 Agent 試圖讀取 `/etc/shadow` 或發起資料庫刪除），在抵達作業系統前就會被 FFI 門閘以常數時間直接攔死！

### Q2.2 攻擊者若利用 Prompt Injection 誘騙 Agent 輸出客戶個資，DROS 如何防禦？
**A：Pillar 4 Policy Gate + PII 動態遮蔽。**
* 當 Agent 試圖調用敏感資料時，Policy Gate 會在二進位層級自動進行欄位動態遮蔽 (PII Redaction)；若涉及高風險資金轉帳或全域刪除，自動觸發 HITL (Human-In-The-Loop) 懸停等待人類雙簽核可，完全封殺語意越權。

### Q2.3 一般業務 Agent 偶爾因為 LLM 幻覺傳錯參數，會被直接殺掉嗎？
**A：不會。** DROS 具備「階梯式處置狀態機 (Graduated Eviction)」：
* **Tier 1 (Soft Deny)**：單次違規僅回傳 `DENY_PERMISSION_ERROR` 讓 Agent 重新自我修正，不中斷業務。
* **Tier 2 (Quarantine)**：滑動窗口超標（如 10 秒內違規 3 次）自動降級至唯讀沙箱並通報 SOC。
* **Tier 3 (Hard Kill)**：只有偵測到致命逃逸特徵（Direct Syscall 繞過、日誌篡改、偽造憑證）或隔離下持續攻擊時，才會發送 `SIGKILL` 物理終止行程。

### Q2.4 黑客如果想辦法直接「替換或覆寫」DROS 微核心 (.dll / .so)，系統會破工嗎？
**A：絕對不會破工。** DROS 具備四重不變量防線：
1. **更換操作本身即是受管轄的 Syscall**：黑客若要覆寫二進位檔，必須驅使 Agent 執行 `cp`、`mv`、`curl` 或檔案寫入操作。在抵達 OS 前已被 DROS 帶內攔截。
2. **內核級不可侵犯不變量 (Kernel Hard Invariants)**：DROS 編譯器強制將針對核心檔案與私鑰種子的寫入操作永久鎖定為 `HARD_BLOCKED`。
3. **OS 內核檔案鎖與 Ed25519 簽名**：運行中的動態庫受 OS 內核鎖定（Windows `FILE_SHARE_READ` / Linux `ETXTBUSY`），竄改後進程直接中斷拒絕加載。

---

## 三、 商業授權與收費邊界 (Licensing & Commercial Boundaries)

### Q3.1 個人版本已經免費，企業版的核心收費價值與邊界在哪裡？
**A：** DROS 遵循「個人非商業免費授權 (Free for Individuals)，企業商用與叢集治理收費」的標準三大層級憲法：
1. **個人/社群免費版**：提供單機進程內治理、輕量 Mock 評測與基礎 Tool 阻斷（最多 2 個 Agent 角色），滿足個人開發者與開源生態。
2. **企業商用付費版 (Enterprise SKU 1--4)**：
   * **多 Agent 蜂群與跨部門 IAM**：支援無上限 Agent 角色池，跨部門 Confused Deputy 權限隔離。
   * **長時間浸泡與生產級 SLA**：支援 24h/72h 浸泡評測（16 萬次無洩漏烘烤）、高可用 K8s DaemonSet 與專屬技術客服。
   * **三級階梯處置與硬熔斷狀態機**：支援滑動窗口違規隔離（Quarantine）與實體終止（SIGKILL）驅逐。
   * **司法級合規存證**：提供連續 SHA-256 Merkle 鏈、Ed25519 數位簽章與一鍵產出歐盟 AI 法案 (EU AI Act Article 12) 合規報告。
   * **跨企業 B2B PKI 聯邦**：支援 `🔑 ROOT-2026` 3-Tier 證書鏈與最大跳數約束。

### Q3.2 企業在內部私有雲 (Air-Gapped / VPC) 部署，需要向外連線驗證 License 嗎？
**A：完全不需要。** DROS 採用離線二進位授權與本機密碼學公鑰驗證機制（Zero-Phone-Home）：
* 企業只需在本地配置簽署之 `policy.bin` 與授權金鑰，微內核完全在記憶體內以純離線方式運作，保證 100% 企業數據與網路隱私不外洩。

---

## 四、 企業部署與運維實施 (Enterprise Operations & Deployment)

### Q4.1 企業如何透過 VajraAgent 主控頁進行「對內」與「對外」的雙向權限區隔與操作？
**A：VajraAgent 提供極致直觀的雙向治理控制台：**
1. **對外 API 門禁治理**：視覺化勾選與調整 Capability 位元圖矩陣，即時設定外部 Agent 的存取 Scope 與 PII 遮蔽門閥。
2. **對內 Agent 護照簽發**：一鍵為企業內部的 AI 員工簽發 3-Tier PKI DIT 護照 (BEC 憑證)，設定該 Agent 出門後的存取邊界與可攜帶資料標籤。
3. **一鍵 RCU 即時黑名單**：當發現異常 Agent，點擊撤銷按鈕，$<1\mu\text{s}$ 內以 RCU 原子指針切換將該 Agent 全網封鎖。

### Q4.2 如何在 CI/CD 流水線中自動防範「管理員失誤授予過大權限」？
**A：透過 `VajraCLI` 靜態掃描門禁（`cli.py lint`）。**
* 在 CI/CD 每次 PR 提交策略 YAML 時，自動執行 `python cli.py lint <policy.yaml>`。
* 若檢測到非 Admin 角色被分配 `admin.*` 或通配符 `*`，自動輸出 `[CRITICAL Dangerous Grant]` 並返回 Exit Code 1 阻斷發布！

---

## 五、 法規合規、專利與免責 (Legal, Patents & Compliance)

### Q5.1 DROS 有哪些情況下是「防止不了的」？（物理邊界宣告）
**A：DROS 誠實揭露以下 4 大防禦極限之外的範疇：**
1. **純文字語意輸出**：若 AI 被劫持後僅在對話框中輸出不當言論（未調用任何 Tool），由前端 Prompt Guard 防護。
2. **合規權限內的邏輯錯誤**：若策略允許寫入資料庫，AI 覆蓋合法資料需依靠 Level 3 異動率熔斷與 CoW 回滾。
3. **私鑰洩漏 (Key Compromise)**：私鑰保護依賴企業 HSM 硬體與冷儲存管理。
4. **宿主 OS Root 級入侵**：攻擊者取得 Root 權限篡改內存屬於 OS 內核安全範疇。

### Q5.2 DROS 的專利與開源授權邊界如何劃分？
**A：標準三大層級憲法（嚴禁混淆）：**
1. **核心執行期微內核** ➔ 美國臨時專利保護 (**U.S. PPA No. 64/111,973**，Patent Pending)。
2. **個人外掛套件** ➔ 個人非商業永久免費授權 (**Free License for Individuals**)。
3. **評測沙盒與重現套件** ➔ 開源授權 (**Apache-2.0**，評測開源 $\neq$ 專利技術開源)。

---
*DROS 官方全量技術與商業統一 FAQ 主庫 ── 單一信任源，權威透明。* 🌐💎⚖️🏢🛡️
