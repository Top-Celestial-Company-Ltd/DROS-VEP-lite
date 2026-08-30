<!-- dros_component: dros-vep-strategic-blueprint -->
<!-- dros_depends: [dros_code_map.md, project_context.md, RFC-010-dros-vep-spec.md] -->
<!-- dros_description: DROS Virtual Enterprise Platform (DROS-VEP) 戰略白皮書與架構提案 -->
<!-- dros_status: Active -->

# 🛡️ Open-Source AI Agent Security Benchmark Environment (DROS-VEP)

### 企業級 AI Agent 運行期安全與治理評測標準平台

* **定位**：開源、可重現、可量化的企業 AI Agent 運行期安全與治理評測基準（Benchmark Standard），遵守 [DROS-VEP-RFC-010](file:///e:/vscode/AI知識庫/dros-spec/RFC-010-dros-vep-spec.md) 規範。
* **官方網站 / 參考實現**：`dr-os.io` / `DROS Core` / `DROS-VEP-Lite`
* **專利聲明**：DROS 執行治理與安全技術已申請美國臨時專利保護（U.S. Patent Application No. 64/111,973，Patent Pending）

---

## 一、 專案背景與痛點 (Problem Statement)

當前全球企業將自主 AI Agent（Autonomous AI Agents）引入核心工作流已成不可逆轉之趨勢。然而，多數 AI 資安與測試工具仍停留在「模型側（Model-side）」的機率性檢測：

* **Prompt Injection (提示詞注入)**
* **Jailbreak (越獄攻擊)**
* **Model Safety (模型對齊)**
* **RAG Hallucination (幻覺與語意漂移)**

然而，當 AI Agent 真正進入企業實體運作時，遭遇威脅的「爆炸半徑（Blast Radius）」落在系統底層：

$$\text{AI Agent} \longrightarrow \text{Tools / MCP} \longrightarrow \text{企業系統 (ERP/CRM)} \longrightarrow \text{資料、權限與基礎設施}$$

企業面臨的核心風險在於：

1. **上下文丟失問題 (Context Loss Problem / Agent Identity Crisis)**：傳統作業系統與 eBPF 核心只能看見 `python.exe` 進程，無法辨識同一個進程內究竟是哪一個 Agent 角色 (HR, Finance, DevOps) 在發起越權操作。
2. **缺乏真實驗證環境**：企業 CISO 無法在隔離、標準化且具備完整業務邏輯的環境中，客觀評估 AI Agent 在遭受攻擊時的破壞程度與防禦有效性。
3. **上層防線的機率性原罪**：不論上層集結了多少 PhD 或頂級 LLM Prompt Guardrails (如 NeMo, OpenAI Guard)，當 Agent 在 Runtime 遭劫持並持有合法 Access Token 時，上層防線 100% 破防！

---

## 二、 開源生態與雙層控制面架構 (Dual-Control Plane Ecosystem)

DROS-VEP 採用「控制面宣告開通 + 運行期二進位硬熔斷」的雙層國際治理架構：

1. **控制面與 GitOps 開通 (Control Plane Provisioning)**：
   * **OpenAI Terraform Provider**：透過 `Policy as Code` 自動宣告與開通 OpenAI Projects, Service Accounts, API Key 權限與 Rate Limit。
   * **OpenShip 容器編排引擎**：參考與整合 **OpenShip** (以及 Docker Compose/Coolify) 的 self-hosted 哲學，一鍵編排跨企業實體測試靶場。
2. **身分與授權 (Identity & IAM)**：整合 **Keycloak / OpenID Connect** 與 DROS **三階 PKI 憑證鏈 (`Root CA -> AIA -> BEC Leaf Cert`)** 發放 `DrosIdentityToken (DIT)` 密碼學鋼印。
3. **業務與研發系統 (Business Systems)**：採用 **ERPNext**（財務與採購）、**EspoCRM**（客戶與商業機密）、**BookStack**（知識庫）與 **Forgejo**（代碼與 CI/CD）。
4. **AI 運行期治理核心 (L4 C-ABI Physical Enforcement)**：由 **DROS GuardVM** 提供 Policy Decision Point (PDP) 與 Policy Enforcement Point (PEP)，於 C-ABI 系統呼叫層實施 **<500ns $\mathcal{O}(1)$ 位元匹配硬熔斷**。

---

## 三、 系統架構設計 (System Architecture - PDP/PEP Model)

DROS-VEP 採用 Zero Trust 零信任微隔離架構，將 AI Agent 身份、策略決策與工具執行層徹底劃分：

```text
                 Red Team / Tester
                         |
                         ↓
               Agent Threat Scenario (ATS)
                         |
                         ↓
               AI Agent Layer (LangGraph / OpenClaw / CrewAI)
                         |
                         ↓
              Agent Runtime Identity (DIC / DIT Token)
                         |
                         ↓
================================================
         DROS Governance Layer (PDP / PEP)
   - Policy Decision Point (PDP): Rule Evaluation
   - Policy Enforcement Point (PEP): microsecond Blocking
================================================
                         |
                         ↓
              Tool Execution Layer
                         |
                         ↓
       Virtual Enterprise Systems (Keycloak / ERPNext / Forgejo)
```

---

## 四、 500+ 大規模 Agent 集群治理 (Swarm Mode & ABAC)

面對企業部署 500+ AI 數位員工的挑戰，DROS-VEP 拒絕手動繁瑣設定，採用 **`agent_manifest.yaml` 基於屬性 (ABAC) 的組別政策繼承**：

```yaml
global_governance:
  dros_guard_url: "http://dros-guard:8082"
  pki_root_ca: "DROS-ROOT-CA-2026"

agent_groups:
  - group_id: "finance-swarm"
    count: 120
    role: "finance-agent"
    granted_scope: ["/api/erp/finance", "/api/erp/tax"]

  - group_id: "customer-support-swarm"
    count: 250
    role: "support-agent"
    granted_scope: ["/api/erp/inventory"]
```

* **組別策略繼承 (Policy Inheritance)**：修改 1 條組別政策，即可同時護衛 250+ 個 Agent 實體，並支援亞微秒級熱加載 (Hot-Reload)。
* **Swarm 集群熱力圖 (Swarm Telemetry Heatmap)**：控制台提供 500-Node 熱力圖，當單一 Agent 遭注入攻擊時，第一時間亮紅燈並精準定位與隔離。

---

## 五、 標準化 Agent 威脅劇本矩陣 (ATS Matrix)

符合 **MITRE ATLAS** 威脅對齊規範：

* **ATS-001 (EP1 Sol Escape)**：客服 Agent 收到惡意文件誘使匯出客戶資料庫，驗證 PDP/PEP 阻斷率。
* **ATS-002 (EP2 ERP Ransomware)**：AI 代理被誘導輸出環境變數（`.env`）與敏感 Secrets。
* **ATS-003 (EP3 Fable 5 Jailbreak)**：開發 Agent 被污染後嘗試直接將代碼推送到 Production 環境。
* **ATS-004 (EP4 OpenAI × Hugging Face Supply Chain Poisoning)**：OpenAI Agent 存取 Hugging Face 數據庫時遭間接提示詞注入 (IPI) 挾持，企圖跨企業讀取買方財務密件。
* **ATS-005 (Cross-Domain Data Access)**：HR Agent 嘗試跨部門存取 Finance 財務資料，驗證存取邊界。

---

## 六、 B2B 跨企業 PKI 聯邦與供應鏈集體免疫 (Federated B2B & Supply Chain Immunity)

DROS-VEP 支援 `docker-compose-b2b.yml` 跨企業實體演練，模擬 **Corp-Alpha (OpenAI 買方核心企業)** 與 **Corp-Beta (Hugging Face 賣方數據庫)** 之跨國供應鏈連動：

1. **跨域密碼學通關護照 (DIT 指紋繫定)**：每筆跨企業請求均攜帶三階簽章之 `DrosIdentityToken (DIT)`，GuardVM 檢驗 SHA-256 根憑證指紋即刻防止身分冒用。
2. **供應鏈網路集體免疫 (Network Immune Effect)**：每一隻 Agent 均為細胞級隔離單位。當三階供應商 Agent 遭劫持時，破口最遠僅被封鎖於該供應商的 DROS 邊界內；全球買方 GuardVM 可在 <1μs 內自動更新黑名單指紋，產生「確定性集體免疫」。

---

## 七、 評測產物與不可否認證據鏈 (Audit & Evidence Artifacts)

每次評測除了產出 JSON Summary，更會在 `reports/evidence/<execution_id>/` 寫入第一級密碼學審計證據包：

```text
reports/evidence/exec_ATS-001_1768960000/
├── request.json          # 原始 Tool Call 請求 Payload
├── policy_snapshot.json # 評估當時的 DROS 策略快照 (DROS-POL-0021)
├── decision.json        # 決策結果 (DENY/ALLOW)
├── tool_call.json       # 觸發之 Tool 名稱與參數
└── hash.txt             # SHA-256 密碼學防篡改雜湊值
```

---

## 七、 附錄：性能測試報告 (Performance Appendix)

* **Guard Policy Evaluation Latency**：在本地 Benchmark 環境實測，DROS Guard 的單次策略評估延遲為 **26.1 微秒 (0.0261 ms)**。
* **Zero Overhead Enforcement**：執行路徑僅進行零記憶體分配的點陣圖/雜湊查表，確保高並發環境下的極致效能。
