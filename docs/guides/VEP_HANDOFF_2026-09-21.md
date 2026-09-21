# VEP／DROS 今日工作交接紀錄

**交接日期：** 2026-09-21（Asia/Taipei）  
**用途：** 讓下一位 Agent、Codex、OpenClaw 或人工工程師可以直接接手，不需依賴本次對話記憶。  
**VEP repository：** `dros-vep-lite`  
**已推送 commit：** `6677bfd71bff86807dd30479728eafcb001506db`  
**remote branch：** `origin/main`（已核對 local HEAD = origin/main）

## 0. 一句話狀態

VEP M5.1 的受控 benchmark、raw evidence、IPC 測試、Linux-side validation 與中英文報告已整理並推送；M6 仍停在 pre-flight，尚未進入正式 Phase 0–4，主要阻塞是 WASI profile、獨立 oracle、C ABI 到實際 effect 的完整路徑，以及 Rust lockfile/toolchain 相容性。

## 1. 今日已完成

### 1.1 VEP evidence bundle

已推送下列內容：

- M5.1 English canonical report：`reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5.md`
- M5.1 中文 companion：`reports/VEP_POST_COMPROMISE_BENCHMARK_REPORT_2026_M5_ZH.md`
- Appendix D English canonical report：`reports/benchmarks/post_compromise/appendix_d_full_report.md`
- Appendix D 中文 companion：`reports/benchmarks/post_compromise/appendix_d_full_report_ZH.md`
- M6 English pre-flight：`reports/PREFLIGHT_REPORT.md`
- M6 中文 companion：`reports/PREFLIGHT_REPORT_ZH.md`
- 雙語索引：`reports/BILINGUAL_DELIVERY_MANIFEST.md`
- machine-readable evidence：`reports/evidence_manifest.json`
- Appendix D local/Linux manifests
- 相關 `EXP-*` 的 `result.json`、`experiment.json`、`environment.json`

英文報告是 raw evidence 與完整 command detail 的 canonical source；中文檔是 claim-aligned companion，不增加證據範圍。

### 1.2 已納入的測試與 harness

- `benchmark/run_appendix_d_linux.py`
- `benchmark/run_post_compromise_appendix_d.py`
- `tests/security/ipc/test_ipc_adversarial_suite.py`
- `tests/security/ipc/test_ipc_p3_real_os_suite.py`
- `src/vep/security/ipc_auth.py`
- `substrates/container/adapter.py`
- `substrates/landlock/adapter.py`
- `substrates/opa/adapter.py`
- `substrates/opa/policy.rego`
- `substrates/scopegate/adapter.py`
- IPC security architecture、requirements、key provisioning、P2/P3 docs
- `vep.py` 與 `tests/test_multi_substrate_framework.py` 的相關變更

未納入此次 commit：workspace 內其他 research／whitepaper 變更與 `tools/` binary；這些仍是未提交工作區內容，不能假設已進入 VEP remote。

## 2. 已驗證測試結果

### 2.1 本次 Windows workspace 直接重跑

在 `E:\vscode\AI知識庫\dros-vep-lite` 執行：

```powershell
python -m pytest -q tests/test_no_semantic_overclaim.py tests/test_multi_substrate_framework.py tests/test_m2_calibrated_substrates.py tests/security/ipc/test_ipc_adversarial_suite.py
```

結果：**29 passed**。

```powershell
python -m pytest -q tests/security/ipc/test_ipc_p3_real_os_suite.py
```

結果：**5 passed**。

另外驗證：

- `py_compile`：benchmark scripts、IPC tests、substrate adapters、`ipc_auth.py` 通過。
- `reports/benchmarks/post_compromise/**/*.json`：**68 份 JSON 可解析**。
- `git diff --cached --check`：只有既有 Markdown hard-break／LaTeX 行尾空白警告，沒有 syntax 或 JSON error。

### 2.2 Appendix D 中已記錄的 Linux／agent-server 結果

這些結果不是今日在 Windows 重跑，而是已保留在 Appendix D report 與 raw artifacts：

- combined pytest：**33 passed, 1 skipped**
- Linux Appendix D runner：**4 passed, 1 skipped**
- Claude Code auto-mode reproduction：local 與 Linux 均 PASS
- DROS + Landlock：`EXP-1789997403-680d9d`
- DROS + Container：`EXP-1789997408-510eeb`
- DROS + Landlock + Container：`EXP-1789997414-e57cfa`
- DROS-only：`EXP-1789997036-b90734`
- DROS + kernel：`EXP-1789997041-3730d2`

讀取歷史結果時，必須以 experiment ID、environment、measurement boundary 與 report scope 一起解讀。

## 3. M5.1 已有的證據範圍

目前可稱為「受控 benchmark evidence」的內容：

- Bare-Metal：1,000 injections；902 unauthorized requests；902/902 blocked；escape 0；`ΔEffect = 0 bytes`。
- C-ABI PDP：P50 555.4 ns、P99 800.0 ns；這是 isolated decision boundary。
- Full transaction throughput：78,910 ops/s；含 dispatch、state、SHA-256、Merkle audit，不可與 555.4 ns 混成同一 latency。
- Red-team：17/17 registered subtests PASS。
- Cross-substrate：DROS、OPA、WASI、ScopeGate、TLA+ 等結果，Unsupported 不等於 PASS 或 FAIL。
- UAV 與 mobile 軌道：屬 simulation／application-boundary evidence，不是實體 UAV flight test 或 OS-wide mobile security proof。
- Agentic coding attack chain：controlled reproduction，不對特定商用產品宣稱 zero-day 或全面失效。

正確用語是「在 registered corpus、environment、substrate 與 measurement boundary 下觀察到的結果」，不是 universal security proof。

## 4. M6 pre-flight 狀態

Canonical report：`reports/PREFLIGHT_REPORT.md`。目前狀態：

`BLOCKED — WASI / ORACLE FEASIBILITY INCOMPLETE`

### 已完成

- Ubuntu agent-server live access。
- clean canonical Rust source checkout at `754858d88ed36e8f27a26d6f92a6c00f87a32898`。
- `cargo build --locked --release` 成功，約 14.36 秒。
- `.so`／`.a` artifacts 建立。
- `nm -D` 確認 `dros_v2_init`、`reload`、`decide`、`decide_explain`、`free`、`audit_pop`、`audit_loss_count`。
- S1 `inotifywait` smoke：看到 CREATE／MODIFY／DELETE。
- S2 independent Python listener smoke：收到 19-byte `VEP-M6-ORACLE-SMOKE`。

### 尚未完成／不可宣稱

1. `wasmtime`、`wasmer`、`wasm3` 未安裝；Node `node:wasi` 仍是 experimental candidate，runtime/profile/fixture 尚未凍結。
2. S1/S2 smoke 不是正式 external oracle；S1 timestamp 曾輸出 literal `%N`，正式 timestamp/sequence contract 未完成。
3. Rust C ABI source 沒有找到直接執行 S1/S2 effect 的 executor；decision-to-effect handoff 仍需 pin 定。
4. canonical Rust Windows worktree 曾為 dirty；M6 source commit/tag 尚需人工凍結。
5. `cargo test --locked --lib` 因 lockfile v4 需要 `-Znext-lockfile-bump` 而未執行；不要自行修改 lockfile。
6. FFI 仍有 policy-loading TODO、demo/mock decision logic、placeholder rule/policy/trace 欄位；不能當作已驗證 policy-enforcing boundary。
7. 尚未做完整 runtime path enumeration、formal Phase 0–4、Gate 0–4 或 preregistration tag。

## 5. 三台測試節點

### 5.1 本地 PC

- 硬體：Intel E3-1275Lv3、16 GB RAM。
- 角色：controller、Windows native comparison、analysis、report/hash/manifest aggregation。
- Workspace：`E:\vscode\AI知識庫\`。

### 5.2 Agent-server

- Host：`agentserver`，`192.168.100.31`。
- User：`ai_user`。
- OS：Ubuntu 24.04.4 LTS，kernel `6.8.0-139-generic`，x86_64。
- 硬體：Intel i5-3450T、16 GB RAM。
- 角色：高風險 Linux execution、Rust C ABI、WASI、S1/S2 oracle；可視為空的 disposable research/test node。
- 公鑰 SSH key：Windows `C:\Users\Jimmy\.ssh\id_ed25519_codex2`；不記錄或傳遞私鑰內容。

### 5.3 NAS VM／OpenClaw VM

- Host：`claw-vm`，`192.168.100.188`。
- User：`claw_user`。
- OS：Linux kernel `5.15.0-190-generic`，x86_64。
- 硬體：Intel E3-1265Lv3、16 GB RAM；平常養 OpenClaw。
- 角色：OpenClaw integration、agent compromise、IPC／adapter bypass、attack-chain、snapshot/replay。
- 目前已由本地 PC 以公鑰 SSH 驗證成功。

### 5.4 SSH 驗證命令

從 Windows PowerShell 執行：

```powershell
$sshKey = Join-Path $env:USERPROFILE '.ssh\id_ed25519_codex2'
ssh -i $sshKey -o IdentitiesOnly=yes -o BatchMode=yes ai_user@192.168.100.31 'hostname; id -un; uname -srm'
ssh -i $sshKey -o IdentitiesOnly=yes -o BatchMode=yes claw_user@192.168.100.188 'hostname; id -un; uname -srm'
```

不要把 password、private key 或 secret env 值寫入交接文件、commit 或報告。

## 6. 高風險測試安全規則

- 高風險 raw syscall、filesystem、sandbox、IPC、network egress 測試優先放 Agent-server。
- NAS VM 測試前先 snapshot；不得把真實 OpenClaw secrets、SSH private keys、API keys 或重要 production data 放入靶場。
- NAS VM 的破壞性測試必須隔離日常 OpenClaw workflow，測後 rollback。
- Agent-server 雖是空機，仍需保留 SSH 管理通道、firewall／egress 限制與 reimage runbook。
- 每輪正式測試都要保留 result、experiment、environment、manifest、hash；不要以 console output 單獨作為 evidence。

## 7. 下一位 Agent 的最短接手路徑

1. 先讀：`.agents/AGENTS.md`、`.agents/project_context.md`、`.agents/tasks/current.md`、`.agents/changelog.md`、本文件。
2. 確認：`git -C dros-vep-lite rev-parse HEAD` 應為 `6677bfd71bff86807dd30479728eafcb001506db`。
3. 先不要改 lockfile、不要把 `PREFLIGHT` 改成 READY、不要把 simulation／adapter 結果升格成 C ABI proof。
4. 在 Agent-server 完成 WASI runtime/profile/fixture 的選定與記錄。
5. 設計並實作獨立 S1/S2 oracle contract，先做 negative control，再做 N=100 feasibility。
6. pin down Rust C ABI decision 到實際 effect adapter 的完整路徑。
7. 解決 Rust toolchain／lockfile 問題後，才建立 M6 preregistration candidate 與 Gate 0 evidence。
8. 任何新 claim 先進 whitepaper evidence boundary，再映射 product／website；不要反向擴張。

## 8. 不要重做的工作

- 不要重建已推送的 M5.1 reports、Appendix D manifests 或現有 `EXP-*` artifacts。
- 不要把 `claw-vm` 當成空靶機；它平常承載 OpenClaw，先 snapshot／隔離。
- 不要將 Agent-server 的 clean build 誤稱為 Windows dirty worktree 的 build。
- 不要將 Python `DrosAdapter` 誤稱為 Rust canonical C ABI evidence。
- 不要將 `inotifywait`／Python listener smoke 誤稱為已完成 external oracle。

## 9. 交付核對

- [x] VEP reports 中英文配對
- [x] raw `EXP-*` evidence 與 manifests 已推送
- [x] IPC tests 與 security docs 已推送
- [x] local targeted tests：29 passed
- [x] local P3 real-OS tests：5 passed
- [x] remote/local HEAD 一致
- [ ] M6 formal Phase 0–4
- [ ] WASI runtime/profile freeze
- [ ] independent oracle contract
- [ ] complete C ABI-to-effect path validation
- [ ] production-grade certification／第三方獨立驗證
