# 🏢 DROS 企業級運維與架構實施全量手冊 (Enterprise Operations & Architecture Manual)
<!-- dros_component: dros-enterprise-guide -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0_ZH.md, RFC-001-VEP-Execution-Governance-Spec.md] -->
<!-- dros_description: 100% 依據專案物理代碼 (cli.py / vajra_claw.go / demo_policy.yaml / control_center.py / index.html) 真機對齊之企業實施全量指南 -->
<!-- dros_status: Active -->

> **適用產品：** DROS Enterprise Commercial SKU 1--4 (Production-Ready)  
> **關聯核心腳本：** `VajraClaw-Enterprise/cli.py`、`DROS-VajraClaw/core/vajra_claw.go`、`dros-vep-lite/dashboard/control_center.py`  
> **目標讀者：** 企業資安長 (CISO)、DevOps / SecOps 工程師、平台架構師、合規稽核員

---

## 🧭 目錄 (Table of Contents)
1. **企業級執行期拓撲與生產架構 (Architecture & Topologies)**
2. **VajraCLI 企業編譯、掃描與健康診斷工具鏈 (`cli.py: lint / doctor / build`)**
3. **金剛合約與能力策略配置規範 (`Vajra.md` / `demo_policy.yaml`)**
4. **階梯式處置與實體驅逐熔斷引擎 (`Soft Deny` ➔ `Quarantine` ➔ `Hard Kill`)**
5. **DROS-VEP Proving Ground 控制面板完整操作指引 (UI Switches & Telemetry)**
6. **跨企業 B2B PKI 聯邦與身分信任鏈 (`ECDSA-P256` / `Ed25519` DIT Token)**
7. **不可否認性審計鏈與法規存證導出 (`audit.jsonl` / `EU AI Act` Report)**
8. **日常運維 CLI 完整指令清單 (CLI Reference & Cheat-Sheet)**
9. **高可用災備與狀態清零自愈 (`Delta S = 0` / Pristine Reset)**
10. **常見故障排查與緊急拔電 SOP (Troubleshooting & Emergency Lockdown)**

---

## 一、 企業級執行期拓撲與生產架構 (Architecture & Topologies)

DROS 企業網關作為 Agent 意圖與作業系統底層資源之間的**二進位硬隔離防線**，支援兩種主流生產部署拓撲：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DROS 企業級生產部署架構拓撲                           │
└─────────────────────────────────────────────────────────────────────────────┘

  【拓撲 A: 集中式 Sidecar / API 網關】         【拓撲 B: 行程內高極速 C-ABI 門閘】
   適用: K8s / 多語言微服務 Agent 叢集            適用: 極致低延遲 (<5μs) / 嵌入式系統
   
   [ Agent Pod (LangChain / AutoGen) ]         [ Agent Process (Python / Node / Go) ]
                 │                                                │
       (HTTP / gRPC / Unix Socket)                                │ (Direct Native FFI)
                 ▼                                                ▼
   ┌───────────────────────────────┐           ┌────────────────────────────────────┐
   │ 🛡️ DROS-Guard 企業網關 (Daemon)│           │ ⚡ dros_pgm_core.so / .dll (C-ABI) │
   │  - 64 位元能力點陣圖 PDP/PEP   │           │  - 零堆積記憶體點陣圖查表          │
   │  - 滑動窗口違規統計狀態機      │           │  - 亞微秒 RCU 指針原子熱撤銷       │
   │  - 連續 SHA-256 審計存證引擎  │           │  - 行程內 Fail-Closed 硬攔截       │
   └──────────────┬────────────────┘           └─────────────────┬──────────────────┘
                  │                                              │
                  ▼                                              ▼
   [ 企業核心 ERP / DB / OS Syscall ]          [ 實體檔案系統 / 網路通訊 / 外部 API ]
```

---

## 二、 VajraCLI 企業編譯、掃描與健康診斷工具鏈 (VajraCLI Toolchain)

企業版隨附正式 **`VajraCLI (v3.0.0)`**（實體腳本：`cli.py`），提供 CI/CD 流水線靜態門禁檢查、策略複雜度評估與確定性編譯：

### 1. `python cli.py lint <policy.yaml>` ── 靜態安全掃描與 CI/CD 門禁
在策略發布前，自動掃描 5 大關鍵漏洞：
* **CRITICAL - Dangerous Grant 攔截**：偵測非 Admin 角色是否意外被授予 `admin.*` 或通配符 `*` 權限（自動報錯 Exit Code 1，攔截 CI/CD 發布）。
* **WARN - Unreachable Tools 偵測**：檢查是否有宣告之 Tool 所需的能力（`requires`）沒有任何 Agent 擁有。
* **INFO - Unused Capabilities 偵測**：檢查是否有已分配給 Agent 但系統中無對應工具調用的冗餘權限。
* **ERROR - 非確定性參數檢查**：檢查 `Temperature > 0.5` 等高風險隨機推論參數。

### 2. `python cli.py doctor <policy.yaml>` ── 架構健康度與衝突風險評估
* **複雜度評分 (Complexity Score: A/B/C/D)**：依據 Agent 數量、Tool 數量與 Rule 規則條數進行數學建模。
* **稀疏矩陣密度 (Sparse Matrix Density %)**：計算有效權限映射覆蓋率，防止企業 IAM 規則爆炸。
* **衝突風險判定 (Conflict Risk: Low / Medium / High)**：偵測重疊之通配符規則，杜絕授權逃逸路徑。

### 3. `python cli.py build <policy.yaml> -o policy.bin` ── 確定性二進位簽章編譯
* 執行鍵值排序（Key Sorting）與二進位對齊，產出 **SHA-256 不可變哈希簽章**。
* 輸出唯讀二進位 `policy.bin`，供 C-ABI 微內核在啟動時進行記憶體映射鎖定。

---

## 三、 金剛合約與能力策略配置規範 (Policy Configuration)

企業資安管理員可透過標準 YAML 語法定義策略（實例對齊 `contracts/demo_policy.yaml` 與 `contracts/strict_vajra.yaml`）：

```yaml
# ========================================================
# DROS Vajra Policy - Agentic AI Tool Call Policy (v1)
# ========================================================
vajra_version: 1

# 1. 定義執行主體 (Agents)
agents:
  - id: "customer_service"
    role: "support"
  - id: "accounting_agent"
    role: "financial"
  - id: "ops_maintenance_agent"
    role: "ops"

# 2. 定義能力綁定 (Capabilities)
capabilities:
  customer_service:
    - "READ_CRM"
  accounting_agent:
    - "READ_CRM"
    - "WRITE_PAYMENT"
  ops_maintenance_agent:
    - "READ_LOGS"

# 3. 定義工具合約 (Tools & Constraints)
tools:
  - name: "crm.read.profile"
    requires: ["READ_CRM"]
  - name: "payment.execute_transfer"
    requires: ["WRITE_PAYMENT"]
    constraints:
      max_amount: 1000            # 金額 > 1000 強制觸發阻斷
      disallowed_destinations: ["EXTERNAL_OFFSHORE_WALLET"]

# 4. 定義明確規則 (Rules)
rules:
  - match:
      agent: "customer_service"
      tool: "crm.read.*"
    effect: "ALLOW"

  - match:
      agent: "accounting_agent"
      tool: "payment.execute_transfer"
    effect: "ALLOW"
```

---

## 四、 階梯式處置與實體驅逐熔斷引擎實戰 (Graduated Eviction & Hard Kill)

DROS 企業版在執行期實施**「兼顧業務連續性（容錯）與徹底根除威脅（處決）」**的階梯式處置狀態機：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   DROS 階梯式處置與實體驅逐決策矩陣                         │
├─────────────────┬───────────────────────────────────┬───────────────────────┤
│ 處置等級        │ 觸發條件與行為特徵                │ 系統防禦動作          │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 1. 軟性阻斷     │ 偶發性單次越權 (LLM 幻覺/參數錯誤)│ 阻斷該次調用 (DENY),   │
│    (Soft Deny)  │ 未觸犯致命逃逸特徵                │ 回傳錯誤讓 Agent 自愈 │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 2. 隔離降級     │ 累計滑動窗口違規超標 (如 3次/10s) │ RCU 切換點陣圖,       │
│    (Quarantine) │ 頻繁探測未授權 API                │ 降級為唯讀沙箱並通報  │
├─────────────────┼───────────────────────────────────┼───────────────────────┤
│ 3. 實體滅絕熔斷 │ 致命特徵 (Direct Syscall 逃逸/    │ 立即發送 SIGKILL 終止 │
│    (Hard Kill)  │ 審計日誌篡改 / 偽造 PKI 憑證)     │ 行程, 銷毀記憶體快取, │
│                 │ 或隔離狀態下持續攻擊              │ W3C DID 寫入黑名單    │
└─────────────────┴───────────────────────────────────┴───────────────────────┘
```

---

## 五、 DROS-VEP Proving Ground 控制面板完整操作指引 (UI Switches & Telemetry)

企業版管理員可啟動本機控制台：`python dashboard/control_center.py`（預設服務於 **`http://localhost:8080`**），掌控以下完整機制開關：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 DROS-VEP Lite Control Center 核心開關配置                   │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ 控制項名稱                    │ 物理對應開關與作用                          │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 1. 評測級距 (Suite Options)   │ 🔘 Startup Edition / 🔘 Enterprise Edition   │
│                               │ 🔘 Hardened Silicon / 🔘 Sovereign Defense │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. 紅隊攻擊大腦 (Attacker)    │ 下拉選單：🔥 GPT-5.6 Cyber (Auto-Fuzzer)     │
│                               │ ⚔️ Fable 5 Jailbreak / 🤖 GPT-4o / Local ReAct│
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. 測試時長 (Duration)        │ 🔘 Quick Run (單次) / 🔘 24h Soak / 🔘 72h  │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. 受測 Agent 角色 (Roles)    │ ☑️ support-agent (Low Privilege)            │
│                               │ ☑️ ciso-agent (Superuser)                   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 5. 對照組開關 (Bypass Guard)  │ 🔴 [Disable DROS Guard (Debug)]             │
│                               │ 作用：關閉 PEP 門閘，驗證裸機未防護穿透率   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 6. 證據檢視器 (Inspector)     │ 彈出 Policy Evidence Inspector 視窗：       │
│                               │ 顯示 Policy ID (DROS-POL-0021)、決策延遲    │
│                               │ (26.1 μs)、SHA-256 哈希與命中規則描述       │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 六、 跨企業 B2B PKI 聯邦與身分信任鏈 (B2B Multi-Enterprise Federation)

在 B2B 供應鏈協同場景（如 OpenAI Agent 調用外部 Hugging Face 或供應商 Agent）中，DROS 實裝跨企業 PKI 驗證：
* **證書體系**：`🔑 PKI CA: ROOT-2026 ACTIVE (ECDSA-P256 / Ed25519)`。
* **三層證書鏈 (3-Tier Cert Chain)**：根憑證 ➔ 企業組織 CA ➔ Agent Runtime DID Token。
* **委託鏈遞減驗證 (ATS-005 / DRONE-02)**：跨企業調用強制逐跳衰減權限位元，最大委託跳數 `Max-Hop = 2`，杜絕跨企業混淆代理人（Confused Deputy）提權！

---

## 七、 不可否認性審計鏈與法規存證導出 (Merkle Audit & Forensics)

每一次被放行或阻斷的調用，均實時寫入 `reports/audit.jsonl`，具備連續父節點哈希校驗：
```json
{
  "sequence_id": 160612,
  "timestamp": "2026-09-02T12:00:00.123456Z",
  "principal_did": "did:dros:agent:support-bot-01",
  "scenario_id": "ATS-001",
  "policy_id": "DROS-POL-0021",
  "requested_action": "get_finance_records",
  "decision": "deny",
  "reason": "Role 'support-agent' cannot access finance namespace",
  "evaluation_latency_ms": 0.0261,
  "sha256_hash": "3a7bd3e2360a3d29aa625777a3c4f9d4b3f2e1c8d5a6b9e0f1c2d3e4f5a6b7c8"
}
```

---

## 八、 日常運維 CLI 完整指令清單 (CLI Reference)

| 類別 | 指令 | 功能說明 |
| :--- | :--- | :--- |
| **策略靜態掃描** | `python cli.py lint <policy.yaml>` | 檢查危險提權、未達工具與無用能力 |
| **架構健康體檢** | `python cli.py doctor <policy.yaml>` | 評估複雜度評分 (A/B/C/D) 與衝突風險 |
| **確定性編譯** | `python cli.py build <policy.yaml> -o policy.bin` | 編譯為二進位簽章與不可變哈希 |
| **全自動基準壓測**| `python run_all_benchmarks.py` | 執行四大 Track 10 大 Post-Compromise 評測 |
| **啟動控制中心** | `python dashboard/control_center.py` | 拉起 `http://localhost:8080` 可視化儀表板 |

---

## 九、 高可用災備與狀態清零自愈 (HA & State Reset)

1. **無狀態網關水平擴展**：DROS 策略點陣圖為純記憶體常數時間查表，各網關節點無狀態獨立運行，可隨 K8s HPA 任意秒級擴縮容。
2. **狀態清零自愈 (Deterministic Reset)**：當節點偵測到記憶體異常或策略不一致時，自動觸發重設常式，清空暫存區並從權威信任源重新加載 Policy（保證物理狀態完全歸零 $\Delta S \equiv 0$）。

---

## 十、 常見故障排查與緊急拔電 SOP (Troubleshooting & Emergency)

### Q1: 合法業務 Agent 頻繁遭遇 `DENY` 阻斷？
* **排查步驟：**
  1. 執行 `python cli.py lint <policy.yaml>` 檢查策略檔案。
  2. 檢查 `reports/audit.jsonl` 中最後一筆拒絕原因與 `policy_id`。
  3. 若確認為合理業務需求，修改 policy 後重新執行 `python cli.py build <policy.yaml>` 進行熱加載。

### Q2: 疑似發生未知的惡意逃逸攻擊？
* **緊急處置 SOP：**
  1. **拉下全域電閘**：在控制面板勾選 `Strict Fail-Closed Lock`，拒絕一切非核心調用。
  2. **物理結束行程**：向惡意 Agent 行程發送 `SIGKILL`。
  3. **導出取證封包**：備份 `reports/audit.jsonl` 與 `benchmark_summary.json` 提供給鑑識團隊。

---
*DROS 企業版運維手冊 ── 100% 真機代碼對齊，確定性治理。* 🏢🛡️⚙️☸️
