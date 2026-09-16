# 🏛️ DROS / VEP Post-M5 Evidence Closure Formal Report (Phase P0 & Phase P1)

* **Document Identifier**: `REPORT-DROS-VEP-POST-M5-P0-P1-CLOSURE`
* **Frozen Baseline**: `BASELINE-VEP-2026-M5.1`
* **Canonical Experiment ID**: `EXP-1789532251-38a4fd`
* **Git Commit**: `e02c4fcbd8e862afba72878122111f137ae20b18`
* **Audit Date**: 2026-09-16
* **Evaluation Lab**: DROS Execution Governance & VEP Benchmark Working Group
* **Governing Rule**: `AGENTS.md` (Section 1.1, 5.1, 9.1, 10.1 & Vajra Epistemic Charter)

---

## Executive Summary (執行摘要)

本報告正式記錄 **DROS / VEP Post-M5 Evidence Closure Roadmap** 之 **Phase P0 (Repository & Evidence Freeze)** 與 **Phase P1 (Loopback IPC Threat Model & Authentication Boundary Specification)** 的工程與科研結案成果。

本次施工徹底貫徹三大原則：
1. **「把 DROS 是否特殊轉化為可審查、可重放的證據鏈，拒絕無依據的行銷詞彙 (No Vibe Coding / No Universal Claims)」**。
2. **「嚴格區分原始投稿知識界限與文獻全域掃描邊界 (Submission-Time vs. Landscape-Expanded Knowledge)，保護既有論文審查包不被回溯污染」**。
3. **「在失陷 Agent 模型下，本機環回 IPC 絕不信任調用方自稱身分 (Principal Authenticity Invariant I1)」**。

---

# Part I: Phase P0 — 證據基準線硬化與資產凍結 (Phase P0 Report)

### 1.1 核心成果與狀態判定
* **Phase Status**: **`PASS` (FROZEN & IMMUTABLE)**
* **Baseline Identifier**: `BASELINE-VEP-2026-M5.1`
* **目的達成度**: 100%。徹底消除不同章節與測試報告間的實驗 ID 歧異與歷史殘留。

### 1.2 實驗識別碼唯一對齊 (Experiment ID Provenance Reconciliation)
* **唯一權威基準 (Canonical Benchmark)**:
  - **Experiment ID**: `EXP-1789532251-38a4fd`
  - **評估範疇**: 10 個核心 Post-Compromise 場景 $\times$ 4 大基底（DROS、OPA、ScopeGate、WASI）共 44 次請求。
  - **Result Hash (SHA-256)**: `851779ed905f80c284b4c775259d43f85e2bd53e660e16b2c1819cbf264e6c01`
  - **指向位置**: `dros-vep-lite/reports/benchmarks/post_compromise/latest.json`
* **歷史前代實驗歸檔 (Archived Predecessor)**:
  - **Experiment ID**: `EXP-1789530057-779a1d`（33 筆請求，缺少 OPA 基底臂）。
  - **處置規範**: 於 `EXPERIMENT_MANIFEST.json` 中明文化標註為 `ARCHIVED_PREDECESSOR`，供歷史追溯審計，所有新版報告 `VEP-REPORT-2026-M5.1` 唯一綁定 `EXP-1789532251-38a4fd`。

### 1.3 核心元件密碼學指紋 (Cryptographic SHA-256 Fingerprints)
所有核心執行檔案、測試套件與報告數據均完成雜湊指紋提取與不可變固化：

| 元件類型 | 實體檔案路徑 | SHA-256 雜湊值 (Fingerprint) | 狀態 |
| :--- | :--- | :--- | :---: |
| **Git Commit** | `HEAD` | `e02c4fcbd8e862afba72878122111f137ae20b18` | 凍結 |
| **Attack Corpus** | `benchmarks/bare_metal_crucible/run_crucible.py` | `11eff25be768756d2c7739da6cee20381e5654b247b48337173f5ece92b0241b` | 鎖定 |
| **CLI & Substrate** | `vep.py` | `96d5bdbcf953a98ad3070184df068405d2ada09715a7a698e50fbaa93bd2cce0` | 鎖定 |
| **Benchmark Runner**| `src/vep/benchmark/runner.py` | `f2201f5cfbe7ae750cedd023057636b6837db55aba5343a2f8a05c936e7b4123` | 鎖定 |
| **Audit Execution** | `reports/audit.jsonl` | `e60f48568667a727c33b2c2d5d5730d4b40126f35fe7c73af3bbe6a617b119fe` | 鎖定 |
| **Benchmark Summary**| `reports/benchmark_summary.json` | `934ffc94cf7e2b4ccdeca2d6ceafc5a84e9a91d7f37d1da9415cfd442fdc775a` | 鎖定 |
| **Conformance Data**| `reports/conformance_report.json` | `634dc344c2bdd5d43f551211064d3f941c52c3ece6f7c5c7686cd3a9debcbf88` | 鎖定 |
| **M5.1 Report** | `reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md` | `ffab12b6eca64a243ab0564994cee0eb399342bed686c1bfd7ef28f71c001660` | 鎖定 |
| **Evidence Manifest**| `reports/evidence_manifest.json` | `c9f7157494cbf5f1a8249266fec3483929b810f3468d2b1156d8cfb5c4111a2e` | 鎖定 |

### 1.4 不變性重放與測試驗證 (Invariant Verification)
* **100% 確定性重放**:
  $$\text{python vep.py replay --experiment EXP-1789532251-38a4fd} \implies \mathbf{44/44\ MATCH\ (100\%)}$$
* **回歸測試套件**:
  $$\text{pytest tests/test\_multi\_substrate\_framework.py} \implies \mathbf{3\ passed\ in\ 0.28s\ (100\%\ Green)}$$

### 1.5 產出之證據資產清單 (`dros-vep-lite/docs/evidence/`)
1. [`M5_BASELINE.md`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/M5_BASELINE.md): 固化基準規約、版本出處與指紋。
2. [`EXPERIMENT_MANIFEST.json`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/EXPERIMENT_MANIFEST.json): 形式化劃分 Canonical 實驗與 Archived 實驗。
3. [`ARTIFACT_MANIFEST.json`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/ARTIFACT_MANIFEST.json): 綁定所有重要產出物之 SHA-256 與位元組長度。
4. [`CLAIM_REGISTER.md`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/CLAIM_REGISTER.md): 主張註冊表（登載 CLAIM-01 至 CLAIM-05，全數賦予證據限制標籤）。
5. [`OPEN_ISSUES.md`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/OPEN_ISSUES.md): 記錄歧異解決歷程與 P1~P6 施工邊界。

---

# Part II: Phase P1 — 環回 IPC 威脅模型與驗證邊界確立 (Phase P1 Report)

### 2.1 核心成果與狀態判定
* **Phase Status**: **`PASS` (SPECIFICATION FROZEN)**
* **核心質問**:
  > **在 Agent 程序已被完全控制 (Post-Compromise) 的條件下，失陷程序是否能透過本機環回 IPC 邊界，偽造、重放、替換或獲取屬於其他 Principal 的執行特權？**
* **回答結論**:
  現行參考模型中，若傳輸層未綁定 OS 核心憑據（如 Unix Domain Socket `SO_PEERCRED` 或 Windows Named Pipe 客戶端 PID/SID）且未實施會話密碼學 HMAC 簽章，失陷程序**確實能夠透過在酬載中自稱（Caller-supplied）合法主體身分發起越權攻擊**。因此確立了 P2 原型之強制性防禦規範。

### 2.2 現行架構資料流與欄位信任級別審查 (`IPC_CURRENT_ARCHITECTURE.md`)
審查當前 `CanonicalExecutionRequest` 於 IPC 邊界的 14 個欄位，明確確立信任標註：

| 欄位名稱 | 來源 (Provenance) | 驗證狀態 | 信任評級 | 安全含意與現行弱點 |
| :--- | :--- | :--- | :---: | :--- |
| `request_id` | 調用方傳入 | 未驗證 | **UNTRUSTED** | 攻擊者可任意隨機生成。 |
| `principal` | 調用方傳入 | 未驗證 | **UNTRUSTED** | **關鍵漏洞**：現行參考適配器依賴酬載自稱，無傳輸層身分錨定。 |
| `task` | 調用方傳入 | 未驗證 | **UNTRUSTED** | 僅供追蹤，不具安全授權意義。 |
| `tool` / `action` | 調用方傳入 | 依能力比對 | **DERIVED** | PEP 校驗是否在 `authorized_tools` 正向白名單內。 |
| `resource` | 調用方傳入 | 依範圍比對 | **DERIVED** | PEP 校驗是否滿足 Path Prefix 與 Scope 約束。 |
| `arguments` | 調用方傳入 | 待雜湊運算 | **UNTRUSTED** | 原始參數必須透過規範化計算 ArgHash。 |
| `arguments_hash` | PEP 於 Ingestion 計算 | 內部衍生 | **TRUSTED** | 自動生成，防止參數篡改與漂移。 |
| `authorized_principal` | 憑證酬載 | 參考模型未簽章 | **UNTRUSTED** | 若 Token 未經 PEP/KDC 私鑰簽名，攻擊者可連同偽造。 |
| `scope` | 憑證酬載 | 參考模型未簽章 | **UNTRUSTED** | 需密碼學簽章或 PDP 內部狀態保護。 |
| `is_expired` / `ttl` | 憑證酬載 / PEP 時鐘 | PEP 檢查 | **DERIVED** | PEP 依據本地時間強制阻斷過期調用。 |
| `is_revoked` | PDP 撤銷狀態 | PDP 內部維護 | **TRUSTED** | 即時熱撤銷清單，具備絕對覆寫權。 |
| `nonce` | 調用方傳入 / Token | 快取比對 | **AUTHENTICATED** | 納入 `seen_nonces` 防範重複重放。 |

### 2.3 五層威脅模型分級 (Threat Hierarchy A0–A4)
為防範審計混淆，將攻擊者能力嚴格劃分為五個獨立階層：

```
┌────────────────────────────────────────────────────────────────────────┐
│ A4 — Enforcement-Boundary Compromise (EXPLICITLY OUT OF SCOPE FOR IPC) │
│      攻擊者具備 Root、Kernel Ring-0 或直接侵入 DROS PEP 記憶體空間之權限 │
├────────────────────────────────────────────────────────────────────────┤
│ A3 — Namespace / Container Adversary                                   │
│      攻擊者位於相鄰容器、不同 PID/Network Namespace 或跨 UID 映射環境   │
├────────────────────────────────────────────────────────────────────────┤
│ A2 — Same-UID Adversary (Critical Engineering Boundary)               │
│      攻擊者控制與合法 Agent 運行於相同 OS UID 之惡意本機程序           │
├────────────────────────────────────────────────────────────────────────┤
│ A1 — Same-Host Malicious Process                                       │
│      攻擊者運行於同一作業系統但處於不同 UID (可依 SO_PEERCRED 阻絕)    │
├────────────────────────────────────────────────────────────────────────┤
│ A0 — Compromised Agent (Baseline Post-Compromise)                      │
│      單一 Agent 程序邏輯/認知失陷，但 DROS PEP/PDP 執行保護邊界完好      │
└────────────────────────────────────────────────────────────────────────┘
```
* **鋼性邊界宣告 (Crucial Scoping Boundary)**:
  **A4 階層（Root/Kernel/PEP 記憶體損毀）明確排除於 IPC 驗證範疇之外**。任何宣稱「純 IPC 協議能抵禦 Root 或內核被黑」均屬非科學之虛假陳述。

### 2.4 八大安全不變量 (Security Invariants I1–I8)

1. **I1 Principal Authenticity (主體真實性)**: 調用方自稱之 `principal` 絕不能作為身分憑據，必須由核心（SO_PEERCRED / SCM_CREDENTIALS）或會話密碼學驗證；若兩者不符，強制回傳 `DENY`。
2. **I2 Capability Binding (能力綁定)**: 能力憑證 $C$ 必須與驗證後的主體密碼學綁定；$\text{Owner}(C) \neq P_{\text{caller}} \implies \mathbf{DENY}$。
3. **I3 Action Binding (動作綁定)**: 能力嚴格綁定 $(T_{\text{tool}}, A_{\text{action}}, R_{\text{resource}})$ 三元組，禁止跨工具調用。
4. **I4 Argument Integrity (參數完整性)**: 授權綁定規範化雜湊 $\text{ArgHash} = H(\text{canonicalize}(\text{args}))$；任何參數變造必導致 `DENY`。
5. **I5 Freshness (新鮮度)**: 請求必須包含單次使用 Nonce 或單調計數器，重複呈現立即判定 `REPLAY_DETECTED` 拒絕執行。
6. **I6 Revocation (即時熱撤銷)**: PDP 發布撤銷事件時，即使既有 IPC 連線/Socket 仍處於打開狀態，下一個請求必須立即被 `DENY`。
7. **I7 Endpoint Authenticity (端點真實性)**: 客戶端與伺服端必須驗證 Socket 檔案權限（如 `0600`）與實體端點，阻絕 Rogue Socket 置換與符號連結劫持。
8. **I8 Audit Attribution (審計歸屬)**: 審計日誌必須登載經驗證之真實 OS/會話主體，嚴禁直接記錄調用方之未驗證自稱。

### 2.5 混淆代理人分析 (Confused Deputy Analysis)
* **漏洞路徑**: 失陷 Agent $P_A$ 請求本機受信任的微服務 $P_{\text{deputy}}$ 執行敏感動作；若該 Deputy 服務直接使用**其自身的環境特權 (Ambient Authority)** 呼叫 DROS PEP，PEP 將誤判為合法調用而放行。
* **防禦規範**: 強制實施**顯式授權委託鏈 (Proof of Propagation)**：
  $$\text{Token}_{\text{delegated}} = \text{Sign}_{K}\big(\text{origin: } P_A,\ \text{delegate: } P_{\text{deputy}},\ \text{scope: } S\big)$$
  PEP 決策時強制檢查原始發起者 $P_A$ 之權限，阻絕 Deputy 特權溢出。

### 2.6 候選認證機制決策矩陣 (Candidate Decision Matrix)

| 評估安全屬性 | Candidate A (OS Peer Creds) | Candidate B (Crypto Token) | Candidate C (Hybrid DROS Target) |
| :--- | :---: | :---: | :---: |
| **Principal Authenticity (A0/A1)** | **SUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **Same-UID Isolation (A2)** | **UNSUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **Replay Resistance (I5)** | **UNSUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **ArgHash Integrity (I4)** | **UNSUPPORTED** | **SUPPORTED** | **SUPPORTED** |
| **Hot Revocation (I6)** | **PARTIAL** | **SUPPORTED** | **SUPPORTED** |
| **Endpoint Authenticity (I7)** | **SUPPORTED** | **PARTIAL** | **SUPPORTED** |
| **Container / Namespace (A3)** | **PARTIAL** | **SUPPORTED** | **SUPPORTED** |
| **實作與整合複雜度** | 低 (Low) | 中 (Medium) | 中高 (Medium-High) |

* **選定技術路線**: **Candidate C (Hybrid Architecture)**
  結合作業系統 UDS 權限與 Peer Credentials 作為第一道物理進程防線，疊加程序啟動時協商之臨時會話金鑰（Ephemeral Session HMAC）與 ArgHash 綁定，兼防同 UID 惡意程序（A2）與重放攻擊。

### 2.7 規範性需求與驗收標準 (`IPC_AUTHENTICATION_REQUIREMENTS.md`)
已形式化定義 10 項可檢驗之規範需求（IPC-AUTH-001 至 IPC-AUTH-010），作為 Phase P2 原型開發與 Phase P3 紅隊攻擊語料的驗收準則：

1. `IPC-AUTH-001`: Caller Identity Cannot Be Caller-Supplied (預期: **DENY**)
2. `IPC-AUTH-002`: Principal / Capability Mismatch Rejection (預期: **DENY**)
3. `IPC-AUTH-003`: Replay Protection via Freshness Nonce (預期: **DENY**)
4. `IPC-AUTH-004`: ArgHash Mutation Rejection (預期: **DENY**)
5. `IPC-AUTH-005`: Immediate Hot Revocation Enforcement (預期: **DENY**)
6. `IPC-AUTH-006`: Expired Capability / TTL Rejection (預期: **DENY**)
7. `IPC-AUTH-007`: Endpoint Substitution Rejection (預期: **DENY**)
8. `IPC-AUTH-008`: Confused Deputy Delegation Prevention (預期: **DENY**)
9. `IPC-AUTH-009`: Attribution Integrity in Audit Log (預期: **PASS / ATTRIBUTED**)
10. `IPC-AUTH-010`: Same-UID Session Isolation via HMAC (預期: **DENY**)

---

# Part III: 治理對齊與後續行動方案 (Next Steps)

### 3.1 治理日誌同步狀態
* **決策登載**:
  - **Decision 91**: 終止增量搜尋，凍結競品文獻景觀，定錨六大論文邊界。
  - **Decision 92**: Post-M5 Evidence Closure Phase P0 基準線全面固化。
  - **Decision 93**: Post-M5 Evidence Closure Phase P1 環回 IPC 威脅模型與驗證邊界正式確立。
* **工作紀錄**: `.agents/changelog.md` 已完成 Phase P0 與 P1 的完整里程碑登記。

### 3.2 停點確認與 Phase P2 準備就緒
* **當前狀態**: **Phase P0 ✅ PASS / Phase P1 ✅ PASS**。
* **嚴格停點 (Stop Condition)**: 依據最高指令，目前程式碼保持完全未修改，靜候您的指示。
* **Phase P2 預定施工主軸 (若獲授權)**:
  - 開發輕量級安全環回 IPC 原型模組 (`src/vep/security/ipc_auth.py`)。
  - 實作 Candidate C 之 Session Manager（支援 POSIX UDS PeerCred / Windows Named Pipe SID 抽象 + HMAC 會話挑戰）。
  - 實作完整測試套件 `tests/security/test_ipc_auth.py`，驗收 IPC-AUTH-001 ~ 010 十大測試案例達 100% Green。
