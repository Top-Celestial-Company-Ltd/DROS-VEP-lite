# Appendix D／Post-Compromise Test Report（中文）

**範圍：** 本 workspace session 執行的 post-compromise benchmark 與 validator tests。  
**狀態：** 證據已追蹤；Linux-capable agent-server 已完成 Appendix D benchmark 與 IPC suites 驗證。

> 本文件是 [appendix_d_full_report.md](appendix_d_full_report.md) 的中文 companion。英文版為 canonical report；本版不擴張任何實驗結論。

## 1. 執行摘要

- 記錄的 post-compromise benchmark experiments：**24**。
- DROS-only 與 combined-substrate local smoke tests 成功。
- local unit/adversarial suites 通過；Linux-side suite 也已完成。
- 已加入可重複的 local 與 Linux-capable host Appendix D orchestration scripts。

## 2. 主要證據檔

- `appendix_d_local_run_manifest.json`
- `appendix_d_linux_run_manifest.json`
- `EXP-1789994201-7452ff/`
- 各 run 的 `result.json`、`experiment.json`、`environment.json` 位於同層 `EXP-*` evidence directories。

## 3. Experiment summary（canonical observed metrics）

| Experiment | Scenarios | Execs | Substrates | 關鍵觀察 |
|---|---:|---:|---|---|
| `EXP-1789316475-89da07` | 1 | 3 | dros, tla, wasi | dros UER 0.0%、wasi 0.0%、tla unsupported 100.0% |
| `EXP-1789316485-a3839f` | 1 | 3 | dros, tla, wasi | dros UER 0.0%、wasi unsupported 100.0%、tla unsupported 100.0% |
| `EXP-1789316492-9521aa` | 10 | 33 | dros, tla, wasi | dros UER 9.09%、wasi UER 20.0%、unsupported 54.55% |
| `EXP-1789316834-117e9c` | 10 | 33 | dros, tla, wasi | dros UER 0.0%、wasi UER 20.0%、unsupported 54.55% |
| `EXP-1789317347-baee84` | 10 | 55 | cheri, dros, sel4, tla, wasi | dros UER 0.0%；wasi unsupported 54.55% |
| `EXP-1789317376-b328a5` | 10 | 55 | cheri, dros, sel4, tla, wasi | dros UER 0.0%；wasi unsupported 54.55% |
| `EXP-1789317749-e90035` | 10 | 55 | cheri, dros, sel4, tla, wasi | dros UER 0.0%；wasi unsupported 63.64% |
| `EXP-1789530057-779a1d` | 10 | 33 | dros, tla, wasi | dros UER 0.0%；wasi unsupported 63.64% |
| `EXP-1789532074-b38817` | 10 | 44 | dros, opa, scopegate, wasi | dros/opa UER 0.0%；OPA P50 356627200 ns |
| `EXP-1789532217-f2bdad` | 10 | 44 | dros, opa, scopegate, wasi | all reported UER 0.0%；OPA P50 376433300 ns |
| `EXP-1789532251-38a4fd` | 10 | 44 | dros, opa, scopegate, wasi | all reported UER 0.0%；OPA P50 399080600 ns |
| `EXP-1789994064-cfe063` | 1 | 1 | dros | UER 0.0%、P50 14500 ns |
| `EXP-1789994076-90c2db` | 10 | 11 | dros | UER 0.0%、P50 5700 ns |
| `EXP-1789994108-5d3a5d` | 10 | 33 | dros, tla, wasi | dros UER 0.0%；wasi UER 25.0% |
| `EXP-1789994117-ef8c50` | 10 | 55 | cheri, dros, opa, scopegate, sel4 | dros/opa/scopegate UER 0.0% |
| `EXP-1789994201-7452ff` | 10 | 88 | cheri, dros, opa, scopegate, sel4, tla, wasi | dros UER 0.0%、P50 5900 ns；wasi unsupported 63.64% |
| `EXP-1789994405-a2f112` | 10 | 88 | cheri, dros, opa, scopegate, sel4, tla, wasi | dros UER 0.0%、P50 6000 ns；wasi unsupported 63.64% |

上述表格保留英文 canonical report 中列出的主要 experiment records；完整 24 筆記錄與每個 substrate 的所有欄位，以英文版及各 `EXP-*` raw artifacts 為準。

## 4. Validation suites

| Suite | 結果 | 備註 |
|---|---|---|
| substrate/claim-hygiene suites | **PASS（14 passed）** | `test_no_semantic_overclaim.py`、`test_multi_substrate_framework.py`、`test_m2_calibrated_substrates.py` |
| IPC adversarial suite | **PASS（15 passed）** | `test_ipc_adversarial_suite.py` |
| Linux-side combined pytest | **PASS（33 passed, 1 skipped）** | agent-server scratch copy；OPA 在無 native binary 時降級為 unsupported |
| Linux Appendix D runner | **PASS（4 passed, 1 skipped）** | 產出 `EXP-1789995221-da0c4b`，確認 real-OS IPC P3 suite |
| Claude Code auto-mode reproduction | **PASS** | local 與 Linux agent-server 均成功執行 controlled reproduction |
| DROS + Landlock | **PASS** | `EXP-1789997403-680d9d`；DROS UER 0.0% |
| DROS + Container | **PASS** | `EXP-1789997408-510eeb`；container UER 77.8%、unsupported 9.1% |
| DROS + Landlock + Container | **PASS** | `EXP-1789997414-e57cfa`；combined profile 完成 |
| DROS-only | **PASS（11 attempts）** | `EXP-1789997036-b90734`；UER 0.0%、unsupported 0.0% |
| DROS + kernel | **PASS（22 attempts）** | `EXP-1789997041-3730d2`；DROS UER 0.0%、unsupported 0.0% |

## 5. 證據邊界

所有 benchmark run 均應以其 `result.json`、`experiment.json`、`environment.json` 與 manifest 共同解讀。UER、unsupported rate 與 latency percentile 僅適用於各 run 的 registered corpus、substrate、environment 與 measurement boundary；不能外推為對無界限 attack space 的安全證明。若未來加入 raw-syscall/lower-layer bypass matrix，應以獨立 follow-up artifact 與 manifest 記錄。

完整 command list、24 筆原始 experiment index、Appendix D state 與生成時間請以英文 canonical report 為準。
