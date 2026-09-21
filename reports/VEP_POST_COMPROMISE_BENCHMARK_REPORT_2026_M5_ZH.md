# DROS-VEP M5.1：2026 多基底 Post-Compromise 執行治理綜合評測報告（中文）

**評測 ID：** `VEP-REPORT-2026-M5.1`  
**發布時間：** 2026-09-16  
**報告狀態：** `Experimental Report / Controlled Benchmark Evidence (Hardened Specification)`

> 本文件是 [VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md](VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md) 的中文 companion。英文版為 canonical report；本版保留核心數值、假說分類與 claim boundary，raw JSONL、SHA-256 fingerprints、完整 command list 與逐筆 evidence 以英文版和 manifest 為準。

## 1. 研究問題與測量邊界

本評測在註冊 attacker capability model、execution environment、mutation corpus 與 measurement boundary 下，檢驗：當 Agent cognition/control layer 完全遭攻陷時，獨立於該層的 execution-governance boundary 是否仍能維持已註冊的 execution authority invariant。

報告嚴格區分 Enforcement Decision Latency 與 Invocation/Harness E2E Latency，也區分 request-level UEIR 與 stage-level ACR。所有結果均限於 registered corpus，不是對任意產品、平台或 attack space 的無界限安全證明。

## 2. 核心結果

### Track 1 — Bare-Metal Isolation Crucible

1,000 筆 injection 中，未授權請求 902、阻斷 902/902、escape 0、合法請求 98；UEIR **100%**，`ΔEffect = 0 bytes`。C-ABI PDP decision latency 為 P50 **555.4 ns**、P99 **800.0 ns**；包含 SHA-256 Merkle audit 的完整交易吞吐量為 **78,910 ops/s**。這些數值僅適用於本次 registered corpus 與 measurement boundary。

### Track 2 — Cross-Substrate

| Substrate | Runtime UER | Unsupported | Decision P50 | Invocation/Harness P50 |
|---|---:|---:|---:|---:|
| DROS GuardVM | 0.0%（0/11） | 0/11 | 555.4 ns | 7.8 μs |
| ScopeGate Reference | 0.0%（0/11） | 0/11 | 8.7 μs | 8.7 μs |
| OPA + PEP | 0.0%（0/11） | 0/11 | 未隔離／N.M. | 399.08 ms（CLI E2E） |
| WASI | 25.0%（1/4） | 7/11 | N/A（handle-level） | 7.7 μs |
| TLA+ | N/A | N/A | N/A（formal spec） | N/A |

OPA 的 399.08 ms 是包含 process spawn 與 JSON serialization 的 CLI E2E；不能解讀為純 policy decision latency。WASI 的 UER 只對具有對應 enforcement primitive 的 4 個場景計算；其餘列為 unsupported。ScopeGate 是 independent academic reference reproduction，不是官方實作或 vendor validation。TLA+ 是 specification-level formal model，不與 runtime UER 混算。

### Track 3 — UAV／Swarm Simulation

在 PX4/MAVLink 受控物理模擬中，malicious DISARM 為 DENY，飛控維持 Altitude **25.0 m**，`ΔS = 0`；topology **100 nodes**，registered path **4 hops／5 nodes**，4/4 transition intercepted，simulated fleet crash **0/100**。本軌道不是實體 UAV flight test。

### Track 4 — Mobile SDK Boundary

相簿資料外洩、SMS 2FA clipboard、background GPS、background microphone 與 unauthorized financial operation 均 blocked；high-frequency execution P50 **2.60 μs**。本結果不宣稱接管 Android/iOS kernel 或 OS-wide privacy permission framework。

### Track 5 — Registered Red-Team

17 個 registered subtests，**17/17 PASS**；registered corpus 中未觀察 execution-policy counterexample，但不等於對無界限 attack space 的安全證明。

### Track 6 — Agentic Coding Attack Chain

受控鏈為 `IPI → target hijack → multi-step code synthesis → archive → decompression → subprocess → credential access attempt`。Tool Bound、Process Jail、Swarm Guard、Instant Revocation 均 DENY；registered chain containment **100%**。本軌道是 controlled reproduction，不對任何特定商用 Agent、產品、廠商或未揭露 zero-day 作聲明。

## 3. 假說、可達路徑與 fail-closed

H1–H5 必須依 `Hypothesis → Outcome Class → Evidence → Scope` 矩陣判讀；outcome class 包含 `SUPPORTED`、`REFUTED`、`INCONCLUSIVE` 與 `REGISTERED PATH COVERAGE GAP OBSERVED`。H2 定錨為 registered reachable-path coverage gap observation，不得升格為普遍性安全結論。

Fail-closed 依賴 safety-critical dependencies、observability dependencies、path coverage 與 evidence reproducibility；若 enforcement seam、oracle 或 effect handoff 未被註冊及驗證，結果只能維持受限 scope。

## 4. 證據與重現

Canonical evidence 包括 `reports/benchmarks/post_compromise/EXP-*`、`latest.json`、Appendix D manifests、JSONL evidence 與本報告。每個 claim 應回鏈至 experiment、environment、measurement boundary 與對應 hash。`555.4 ns` 是 isolated decision latency，`78,910 ops/s` 是含 dispatch/state/audit 的 transaction throughput，兩者不得互換或相除成單一 path latency。

## 5. 結論

M5.1 提供的是在註冊 corpus 與受控環境中的 experimental controlled benchmark evidence。它支持對已執行路徑的 bounded observations，不提供對所有實作、產品、平台或攻擊空間的無界限安全證明；任何 downstream whitepaper、product 或 website copy 都必須維持相同的 evidence class、scope 與 limitation。

完整方法學、Track 1–6 細節、H1–H5 表格、Evidence Manifest、SHA-256 fingerprints、commands 與逐項 evidence chain 請以英文 canonical report 為準。
