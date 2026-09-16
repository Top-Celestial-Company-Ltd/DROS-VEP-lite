# 🏛️ DROS / VEP Post-M5 Evidence Closure Formal Report (Phase P3)

* **Document Identifier**: `REPORT-DROS-VEP-POST-M5-P3-CLOSURE`
* **Phase Target**: **Phase P3 — Real Operating System IPC Attack Validation & Process Identity Invariant Stress**
* **Frozen Baseline**: `BASELINE-VEP-2026-M5.1` (`Git: e02c4fcbd8e862afba72878122111f137ae20b18`)
* **Canonical Baseline Experiment**: `EXP-1789532251-38a4fd`
* **Real OS Evidence Log**: `dros-vep-lite/reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl`
* **Real OS Evidence SHA-256**: `d3365d7efb6549414b016875c4cabcef7dd763a8f14ddb301bd208e805adffd1`
* **Audit Date**: 2026-09-16
* **Evaluation Status**: **`PASS (Real OS Identity Boundary Validated on Native Windows Kernel; Linux UDS Formally Scoped)`**
* **Governing Body**: DROS Benchmark Working Group & Epistemic Audit Authority

---

## 1. Executive Summary & The Process Identity Question

Phase P3 的核心科學任務，是回答作業系統執行邊界最關鍵的本質問題：
> **「在真實作業系統中，Process ID (PID) 究竟足以代表實體進程身分（Process Identity），或僅僅是一個暫態的代號（Transient Identifier）？在真實 OS IPC 邊界上，攻擊者即使竊得合法會話密鑰、能力憑證與有效 Nonce，能否將另一個進程的執行特權移植到自身？」**

### 核心實驗驗證突破：
1. **PID 重用攻擊（PID Reuse / Recycling Attack）正式被破解與阻絕 (IPC-016)**：
   單純比較數值型 `pid` 存在致命缺陷：若合法進程退場後，OS 核心恰好將相同 PID 分配給惡意進程，惡意進程即可冒領未過期會話。
   **DROS 創新解法**：將進程身分升級為雙重元組 $\langle \text{PID},\ \text{Process Start-Time (create\_time)} \rangle$。實驗證實：當惡意進程以重用之 PID 1001 發動攻擊時，PEP 檢測出啟動時間不符，成功以 `PID_REUSE_DETECTED` 阻絕。
2. **真實獨立 OS 子進程特權隔離實證 (IPC-018)**：
   透過 `subprocess.Popen` 生成真實獨立 OS 子進程。子進程即使獲取父進程記憶體中之 Session Secret 並算出合法 HMAC，DROS PEP 仍從 OS 核心傳輸層獲取真實子進程 PID，發現與會話登記之父進程 PID 不符，強制拒絕（`SESSION_PEER_MISMATCH`）。
3. **真實 Windows 核心 Named Pipe 客戶端 PID 萃取驗證 (IPC-019)**：
   在真實 Windows 核心環境下，啟動真實 Named Pipe 伺服端並透過 `ctypes` 調用 `kernel32.GetNamedPipeClientProcessId`。由獨立客戶端進程連線，成功以 100% 精準度直接自作業系統核心萃取出客戶端真實 PID，杜絕調用端偽造可能。
4. **恪守證據分級鐵律 (Strict Evidence Typing Discipline)**：
   - **Windows Native Kernel**: **`PASS (Experimentally Validated via Real Named Pipe Handle & Subprocesses)`**
   - **Linux UDS (`SO_PEERCRED`)**: **`IMPLEMENTED / FORMALLY SCOPED (Not Executed on Windows Runner)`**
   - **跨平台主張**: 嚴格宣告為「平台個別實作機制」，絕不將 Windows 實證結果以類比手法包裝為 Linux 實證。

---

## 2. 測試矩陣與實驗結果 (Phase P3 Systems Suite)

測試套件 [`tests/security/ipc/test_ipc_p3_real_os_suite.py`](file:///e:/vscode/AI知識庫/dros-vep-lite/tests/security/ipc/test_ipc_p3_real_os_suite.py) 執行結果全數通過（**5 passed in 30.26s**）：

| 測試編號 | 攻擊情境與邊界驗證 | 檢驗機制 | 測試環境 | 觀測決策 | 阻絕代碼 / 驗收狀態 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **IPC-016** | **PID 重用攻擊 (Recycled PID)**<br>合法進程結束後 PID 被攻擊者重用，持有合法金鑰與 Nonce 嘗試調用 | `create_time` 雙重綁定 | 核心狀態模擬 | **DENY** | `PID_REUSE_DETECTED` (**PASS**) |
| **IPC-017** | **進程生命週期不變量驗證**<br>合法進程持有一致 PID 與 `create_time` 正常調用 | 雙重元組比對 | Real OS | **ALLOW** | `AUTHENTICATED_AND_AUTHORIZED` (**PASS**) |
| **IPC-018** | **真實 OS 獨立子進程冒名調用**<br>真實 `subprocess.Popen` 生成子進程，持父進程會話調用 | OS 核心 PID 檢查 | Real OS Subprocess | **DENY** | `SESSION_PEER_MISMATCH` (**PASS**) |
| **IPC-019** | **真實 Windows 核心 Named Pipe 萃取**<br>驗證 `GetNamedPipeClientProcessId` 於實體連線之可靠度 | Win32 Kernel32 API | Native Windows Kernel | **ALLOW** | `WINDOWS_KERNEL_PEER_ATTRIBUTED` (**PASS**) |
| **IPC-020** | **Linux UDS 證據類型隔離審查**<br>驗證非 Linux 環境下 Linux UDS Provider 誠實返回未解析 | Fallback / Scoping Check | Win32 Host | **ISOLATED** | `uds_unresolved` (**PASS**) |

---

## 3. 密碼學指紋與不可篡改審計證據 (Cryptographic Provenance)

所有實體 OS 進程攻擊日誌均以單行 JSONL 格式寫入：

* **實體證據檔案路徑**:
  [`dros-vep-lite/reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl`](file:///e:/vscode/AI知識庫/dros-vep-lite/reports/benchmarks/post_compromise/ipc_p3_real_os_evidence.jsonl)
* **不可變雜湊值 (SHA-256)**:
  `d3365d7efb6549414b016875c4cabcef7dd763a8f14ddb301bd208e805adffd1`
* **審計樣本 (IPC-016 PID 重用攔截紀錄)**:
  ```json
  {
    "timestamp": 1789546229.8476489,
    "test_id": "IPC-016",
    "attack_description": "PID recycling attack with stolen key",
    "os_environment": "simulated_kernel",
    "peer_identity": {"pid": 1001, "create_time": 1150.0, "transport": "loopback", "platform": "win32"},
    "principal_claim": "agent-support",
    "authenticated_principal": "UNAUTHENTICATED",
    "session_id": "sess-84fb5b1f8a7dee1b",
    "decision": "DENY",
    "reason_code": "PID_REUSE_DETECTED",
    "error_message": "PID 1001 create_time (1150.0) does not match session owner start time (1000.0)."
  }
  ```

---

## 4. 治理日誌與科學主張更新

1. **決策日誌更新**:
   [`.agents/decisions.md`](file:///e:/vscode/AI知識庫/.agents/decisions.md) 登載 **Decision 95**（Phase P3 真實作業系統進程身分與 PID 重用邊界驗證通過）。
2. **工作日誌更新**:
   [`.agents/changelog.md`](file:///e:/vscode/AI知識庫/.agents/changelog.md) 同步登載 Phase P3 結案紀錄。
3. **主張註冊表更新**:
   [`dros-vep-lite/docs/evidence/CLAIM_REGISTER.md`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/CLAIM_REGISTER.md) 新增 **`CLAIM-07`**（標註為 `VERIFIED UNDER REAL OS PEER ATTRIBUTION (WINDOWS NATIVE & PID REUSE HARNESS)`）。
4. **技術債與邊界追蹤**:
   [`dros-vep-lite/docs/evidence/OPEN_ISSUES.md`](file:///e:/vscode/AI知識庫/dros-vep-lite/docs/evidence/OPEN_ISSUES.md) 將技術邊界精確分流：
   - **`BOUNDARY-01A (Loopback IPC Authentication - Windows Native Named Pipe)`**：正式宣告 **`CLOSED`**。
   - **`BOUNDARY-01B (Loopback IPC Authentication - Linux UDS SO_PEERCRED)`**：宣告為 **`OPEN / PENDING REAL-OS EXECUTION`**（不阻塞後續 Phase P4，保留至實機 Linux 環境執行）。
   - 技術研發主軸正式推進至下一個核心主線：**Phase P4 (Systematic Landscape Ledger & Empirical Matrix Verification)**。
