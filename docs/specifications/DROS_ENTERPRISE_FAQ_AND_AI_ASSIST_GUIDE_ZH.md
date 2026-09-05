# 🏢 DROS 企業級全量技術 FAQ、官網精選 Q&A 與 AI 協同實施指引
### (Enterprise Technical FAQ, Official Website Q&A & AI Copilot Guide)
<!-- dros_component: dros-enterprise-faq -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0_ZH.md, DROS_ENTERPRISE_OPERATIONS_AND_ARCHITECTURE_GUIDE_ZH.md] -->
<!-- dros_description: 100% 整合官網 FAQ、RFC-010 護照、6-Pillars 模型、商業收費邊界、技術疑難與 AI (Cursor/Claude) 落地 Prompt 示範之全量指南 -->
<!-- dros_status: Active -->

> **適用對象：** 企業資安長 (CISO)、DevOps / SecOps 工程師、AI 解決方案架構師、合規稽核員  
> **核心標準：** 對齊 IEEE 論文 6-Pillars、U.S. Patent 64/111,973、以及官網 (dr-os.io) 發布之標準問答。

---

## 🌐 一、 官網精選核心問答 (Official Website Featured FAQ)

### Q1. 什麼是「開放身份，在地治理 (Open Identity, Localized Governance)」？外部 Agent 持護照來訪會威脅企業嗎？
**A：完全不會！這正是 DROS 解決 Agentic Web 跨企業信任衝突的核心範式。**
* 外部 Agent 攜帶 RFC-010 護照 (`libdros-id`) 來訪時，僅提供其身分歸因 (Principal) 與發行簽章。
* **企業在地 GuardVM 網關保有 100% 的確定性執行裁量權**：企業在 VajraAgent 主控頁上，可直接為該外部護照設定在地 Capability Bitmaps (位元圖矩陣)。即使外部護照聲稱自己具備超級管理員權限，DROS 在 C-ABI 帶內層級 (26.1 μs) 依然僅允許其調用企業開通的特定 API。任何越權呼叫直接物理熔斷並返回 HTTP 403。

### Q2. 企業如何透過 VajraAgent 主控頁進行「對內」與「對外」的雙向權限區隔與操作？
**A：VajraAgent 提供極致直觀的雙向治理控制台：**
1. **對外 API 門禁治理**：視覺化勾選與調整 Capability 位元圖矩陣，即時設定外部 Agent 的存取 Scope 與 PII 遮蔽門閥。
2. **對內 Agent 護照簽發**：一鍵為企業內部的 AI 員工簽發 3-Tier PKI DIT 護照 (BEC 憑證)，設定該 Agent 出門後的存取邊界與可攜帶資料標籤。
3. **一鍵 RCU 即時黑名單**：當發現異常 Agent，點擊撤銷按鈕，$<1\mu\text{s}$ 內以 RCU 原子指針切換將該 Agent 全網封鎖。

### Q3. DROS 提出的「6-Pillars 確定性治理」與傳統的 IAM / OAuth 或 API Gateway 有何本質區別？
**A：物理層 C-ABI 帶內硬熔斷 vs. 網路層軟邊界。**
* **超低延遲**：傳統 API Gateway 運作在 Out-of-band HTTP 網路層 (4ms~50ms)，DROS-6P 在物理層 C-ABI / eBPF 直接運作，平均決策延遲僅 **26.1 μs** (p99 = 29.8 μs)，效能提升數千倍。
* **密碼學證明**：內建 SHA-256 Merkle 雜湊稽核鏈與 Ed25519 簽章，產出具備不可否認性的法務級憑證。

### Q4. 攻擊者若利用 Prompt Injection 誘騙 Agent 輸出客戶個資，DROS 如何防禦？
**A：Pillar 4 Policy Gate + PII 動態遮蔽。**
* 當 Agent 試圖調用敏感資料時，Policy Gate 會在二進位層級自動進行欄位動態遮蔽 (PII Redaction)；若涉及高風險資金轉帳或全域刪除，自動觸發 HITL (Human-In-The-Loop) 懸停等待人類雙簽核可，完全封殺語意越權。

### Q5. 企業部署 DROS 需要修改原有的 AI Agent 程式碼 (如 LangChain / AutoGen) 嗎？
**A：完全不需要！零程式碼修改 ‧ 零系統停機。**
* DROS 採用外部 C-ABI 帶內攔截與開箱即用的 `libdros-id` SDK。
* 管理者透過宣告式策略合約 (`vajra.yaml`) 或 VajraAgent Web 主控台調整權限後，DROS 控制平面便會在微秒內完成熱加載 (Hot Reloading)，AI 員工運作零中斷。

---

## 💼 二、 企業商業授權與收費邊界 FAQ (Commercial & Licensing)

### Q6. 個人版本已經免費，企業版的核心收費價值與邊界在哪裡？
**A：** DROS 遵循「個人非商業免費授權 (Free for Individuals)，企業商用與叢集治理收費」的標準三大層級憲法：
1. **個人/社群免費版**：提供單機進程內治理、輕量 Mock 評測與基礎 Tool 阻斷（最多 2 個 Agent 角色），滿足個人開發者與開源生態。
2. **企業商用付費版 (Enterprise SKU 1--4)**：
   * **多 Agent 蜂群與跨部門 IAM**：支援無上限 Agent 角色池，跨部門 Confused Deputy 權限隔離。
   * **長時間浸泡與生產級 SLA**：支援 24h/72h 浸泡評測（16 萬次無洩漏烘烤）、高可用 K8s DaemonSet 與專屬技術客服。
   * **三級階梯處置與硬熔斷狀態機**：支援滑動窗口違規隔離（Quarantine）與實體終止（SIGKILL）驅逐。
   * **司法級合規存證**：提供連續 SHA-256 Merkle 鏈、Ed25519 數位簽章與一鍵產出歐盟 AI 法案 (EU AI Act Article 12) 合規報告。
   * **跨企業 B2B PKI 聯邦**：支援 `🔑 ROOT-2026` 3-Tier 證書鏈與最大跳數約束。

### Q7. 企業在內部私有雲 (Air-Gapped / VPC) 部署，需要向外連線驗證 License 嗎？
**A：完全不需要。** DROS 採用離線二進位授權與本機密碼學公鑰驗證機制（Zero-Phone-Home）：
* 企業只需在本地配置簽署之 `policy.bin` 與授權金鑰，微內核完全在記憶體內以純離線方式運作，保證 100% 企業數據與網路隱私不外洩。

---

## 🛡️ 三、 核心安全與架構實施 FAQ (Architecture & Security)

### Q8. 黑客若發動未知「零日漏洞 (0-Day) 提示注入」，DROS 能擋住嗎？
**A：100% 能擋住。**
* DROS 採用 **Default Fail-Closed（預設關閉 / 白名單）** 哲學。
* 無論攻擊 Payload 多麼新穎、如何繞過 LLM 認知，只要該 Agent 試圖調用未被明確授權的 API/Tool（例如客服 Agent 試圖讀取 `/etc/shadow` 或發起資料庫刪除），在抵達作業系統前就會被 FFI 門閘以常數時間直接攔死！

### Q9. 一般業務 Agent 偶爾因為 LLM 幻覺傳錯參數，會被直接殺掉嗎？
**A：不會。** DROS 具備「階梯式處置狀態機 (Graduated Eviction)」：
* **Tier 1 (Soft Deny)**：單次違規僅回傳 `DENY_PERMISSION_ERROR` 讓 Agent 重新自我修正，不中斷業務。
* **Tier 2 (Quarantine)**：滑動窗口超標（如 10 秒內違規 3 次）自動降級至唯讀沙箱並通報 SOC。
* **Tier 3 (Hard Kill)**：只有偵測到致命逃逸特徵（Direct Syscall 繞過、日誌篡改、偽造憑證）或隔離下持續攻擊時，才會發送 `SIGKILL` 物理終止行程。

---

## 🤖 四、 AI 協同實施指引：如何引領 AI 助手快速落地 (AI Copilot Prompts)

企業工程師在導入 DROS 時，可直接將以下 **標準提示詞（Prompt 模板）** 複製給您的 AI 程式碼助手（如 Cursor、Claude Code、GitHub Copilot、ChatGPT），讓 AI 在幾秒鐘內為您完成策略撰寫與代碼整合：

### 🎯 示範 1：引領 AI 為企業現有 Agent 產生標準 `policy.yaml`
```text
【任務】：請為我們企業內部的 [客服 Agent / 財務審批 Agent] 生成 DROS Vajra 治理策略檔案 `policy.yaml`。
【規範約束】：
1. 遵守 DROS v1.0 規範，頂部宣告 `vajra_version: 1`。
2. 明確定義 agents、capabilities、tools 與 rules 四大區塊。
3. 嚴格遵循最小權限原則（Least Privilege）：
   - 客服 Agent 僅能讀取 CRM 資料 (crm.read.*)，嚴禁任何寫入與系統指令。
   - 財務 Agent 僅能執行單筆小於 1000 元之轉帳 (payment.transfer)。
4. 預設全域封鎖（Fail-Closed），嚴禁對非 Admin 角色使用通配符 `*`。
請輸出乾淨完整的 YAML 內容，並附帶執行 `python cli.py lint` 檢查的指令。
```

---

### 🎯 示範 2：引領 AI 在 Python Agent 中整合 `VajraClaw` FFI 攔截器
```text
【任務】：請在我們現有的 LangChain / AutoGen Python 專案中，整合 DROS VajraClaw 執行期治理攔截器。
【實作要求】：
1. 導入 `from integrations.vajraclaw.runtime import VajraClaw, Decision`。
2. 在應用程式初始化時載入編譯好的 `policy.bin`。
3. 在所有 Agent Tool 調用入口處封裝治理評估：
   ```python
   result = vc.evaluate(tool_name="execute_sql", payload=params, agent_id="support_agent")
   if not result:
       raise PermissionError(f"DROS Interception: {result.reason}")
   ```
4. 確保符合 Fail-Closed 原則，並記錄結構化審計日誌。請提供完整的 Python 封裝模組代碼。
```

---
*DROS 企業級全量技術 FAQ ── 官網問答、商業授權、技術邊界與 AI 協同全覆蓋。* 🏢🌐💎🤖⚡
