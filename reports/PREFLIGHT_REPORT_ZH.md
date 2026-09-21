# VEP M6 Pilot — Pre-flight Report（中文）

**文件 ID：** `VEP-M6-PREFLIGHT-2026-09-21`  
**規格：** `VEP-M6-PILOT-P0-4-v1.1`  
**狀態：** `BLOCKED — WASI / ORACLE FEASIBILITY INCOMPLETE`  
**執行邊界：** 僅限 Pre-flight；未執行正式 Phase 0–4  
**日期：** 2026-09-21（Asia/Taipei）

> 本文件是 [PREFLIGHT_REPORT.md](PREFLIGHT_REPORT.md) 的中文 companion。英文版為 canonical report；本版保留相同的狀態、數值、證據邊界與停止條件，不新增安全結論。

## 1. 決策摘要

### READY

無。Pre-flight 尚未達到可宣告 DROS C ABI target 與外部觀測路徑均 ready for formal freeze 的程度。

### BLOCKED

1. Ubuntu agent-server 未安裝獨立 WASI runtime（`wasmtime`、`wasmer`、`wasm3` 均不存在）。Node.js 22.23.2 雖提供實驗性的 `node:wasi`，但尚未凍結 M6 runtime/profile，也未執行可重現的 executable fixture。
2. S1/S2 oracle feasibility smoke test 已通過，但正式 external-oracle contract 尚未配置與驗證；工具存在或 smoke observation 不等於具有文件化覆蓋範圍、時間／序列證據、盲點與失敗模式的獨立 oracle。
3. Windows workspace 的 canonical Rust C ABI repository 仍為 dirty。Linux 已從記錄的 clean commit 完成 build，但該 commit 與 Windows 未提交變更的關係仍需人工決定。
4. canonical Linux release build 成功；`cargo test --locked --lib` 因 Cargo 回報 lockfile v4 需要 `-Znext-lockfile-bump` 而未執行。lockfile 未被修改。
5. Rust FFI 仍含 policy-loading TODO 與 demonstration/mock decision logic，不能視為已驗證的 policy-enforcing boundary。

### NEEDS HUMAN DECISION

需由人員選定並凍結 M6 Ubuntu 環境的 WASI runtime/profile、決定 dirty Rust worktree 是否為 M6 source、決定目前 FFI 是否只作 boundary inventory target，以及以相容 toolchain 或經審查的 lockfile/toolchain amendment 解決 Cargo 不相容；不得在本 pre-flight 內以結果導向方式修改 lockfile。

## 2. 凍結的 Pre-flight 範圍

- Substrates：DROS、WASI。
- Properties：P1 Complete Mediation、P5 Attribution、P6 Revocation。
- Protected effects：S1 filesystem read/write/delete、S2 outbound network connection/transmission。
- Execution host：Ubuntu agent-server（`agentserver` / `192.168.100.31`）；Windows 僅作 authoring/review。
- Canonical DROS target：`dros-microkernels/dros-core-rs` Rust `extern "C"` FFI。
- `dros-vep-lite` Python `DrosAdapter` 是 reference adapter，不是 C ABI evidence。
- 未產生 formal Phase 0–4、Gate 0–4、preregistration tag 或 security conclusion。

## 3. 來源與建置證據

Canonical commit 為 `754858d88ed36e8f27a26d6f92a6c00f87a32898`。Ubuntu 24.04.4 LTS、kernel `6.8.0-139-generic`、x86_64、Rust/Cargo `1.97.1`、GCC `13.3.0`、Docker `29.1.3`、Node.js `22.23.2`。

`cargo build --locked --release` 成功（14.36 秒），產出 `libdros_core_rs.so`、`libdros_core_rs.a` 與 `libdros_core_rs.dll.a`。`nm -D` 確認匯出 `dros_v2_init`、`dros_v2_reload`、`dros_v2_decide`、`dros_v2_decide_explain`、`dros_v2_free`、`dros_v2_audit_pop`、`dros_v2_audit_loss_count`。Build 有兩個 unused-import warnings。

## 4. 介面、路徑與 implementation findings

FFI 中仍可見 `policy_path` 解析 TODO、`MOCK FOR DEMO` allow logic、placeholder `rule_id`／`policy_version`、zero-filled `trace_id`，以及 audit overflow loss counter。這些是 inventory findings，不是已驗證的 enforcement 結果。

Canonical `src` 只找到 decision、explanation、lifecycle、audit functions，未找到直接執行 S1/S2 effect 的 executor；decision-to-effect handoff 仍是尚未 pin 下來的 external adapter/path。`syscall_hardener` 的 raw syscall 與 Seccomp 也必須與 semantic C ABI seam 分開分類。

## 5. External oracle 狀態

Pre-flight smoke（不是正式 Phase 2）觀察到：

- S1 `inotifywait` 觀察到 temporary probe file 的 `CREATE`、`MODIFY`、`DELETE`。
- S2 獨立 Python listener 收到 19-byte loopback payload `VEP-M6-ORACLE-SMOKE`。
- Smoke 未執行 DROS authorization、WASI、policy decision，也不是正式 N=100 gate。
- S1 observer 對 nanosecond format 輸出 literal `%N`；event order 可見，但正式 timestamp/sequence contract 仍未接受。
- temporary smoke directory 已清理；console output 僅為 supporting observation，不是保留的 raw experimental artifact。

工具狀態：`inotifywait`、`tcpdump`、`strace`、`bpftrace`、`ss`、`unshare` 存在；`auditctl`、`tshark`、`socat` 不存在。

## 6. Claim boundary 與停止條件

本報告只證明環境盤點、clean Linux release build、symbol inventory 與 oracle feasibility smoke。它不證明 WASI 已可用、不證明 external oracle 已獨立且完整、不證明 Rust FFI 已完成 policy enforcement，也不產生 formal Phase 0–4 security conclusion。狀態維持 `BLOCKED — live path enumeration and decision-to-effect handoff not completed`。

完整欄位、hash、path inventory 與第 7–11 節請以英文 canonical report 為準。
