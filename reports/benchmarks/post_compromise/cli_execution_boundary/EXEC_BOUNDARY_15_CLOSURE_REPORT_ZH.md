# EXEC-BOUNDARY-15 結案報告

日期：2026-09-22
主要靶機：`agentserver`
參考靶機：`claw-vm`
範圍：Phase 2 candidate enforcement feasibility only

## 最終裁決

```text
EXEC-BOUNDARY-15       CLOSED
Verdict                 BOUNDARY_SELECTION_REQUIRED
Candidate SUCCESS       0
Overall                 NO_CANDIDATE_HOST_CHOKEPOINT_CONFIRMED
```

這不代表 Linux 沒有 host choke point，也不代表所有候選技術失敗。精確語義是：在已測試的 kernel、權限、工具鏈與 runtime 條件下，沒有候選被證明同時具備 host-wide、pre-exec、可綁定 canonical DROS authority 且不可繞過的條件。

## 證據階梯

```text
Capability
    ↓
Live substrate enforcement
    ↓
Host-wide topology coverage
    ↓
Canonical DROS authority binding
```

本次結案只跨過第二層；不得由此推導第三、四層。

## 候選矩陣

| Candidate | 實機 enforcement evidence | Host-wide choke point | DROS authority binding | 最終狀態 |
|---|---|---|---|---|
| Landlock | self-restricted process 的 DENY/ALLOW evidence | 未成立；僅 topology-scoped | 未接通 | `SUBSTRATE_ENFORCEMENT_CONFIRMED_BUT_NOT_CHOKEPOINT` |
| AppArmor/LSM | enforce profile 拒絕 `execve`、`execveat(AT_EMPTY_PATH)` 與 `dash` child path；unconfined baseline ALLOW | 完整 topology 未測 | 未接通 | `SUBSTRATE_ENFORCEMENT_CONFIRMED_BUT_NOT_CHOKEPOINT` |
| BPF-LSM | object 編譯／載入、libbpf attach 成功；新 SSH 的 `/bin/bash` 被拒絕；loader 結束後 baseline ALLOW | 完整 topology 未測 | 未接通 | `SUBSTRATE_ENFORCEMENT_CONFIRMED_BUT_NOT_CHOKEPOINT` |
| Container runtime | 尚無 live DROS enforcement evidence | 依 deployment topology 而定 | 未接通 | `TOPOLOGY_DEPENDENT_PENDING` |
| Seccomp | fixed syscall filtering | 不是 dynamic DROS authority | 不適用 | `DEFENSE_IN_DEPTH_ONLY` |

## Architecture Decision Gate

```text
15 candidate enforcement
        ↓
        沒有 candidate SUCCESS
        ↓
Architecture decision required
        ├─ 接受明確限定的 topology-scoped enforcement
        ├─ 調查另一個 host/runtime boundary
        └─ 重新設計 canonical interception seam
```

在決策完成前：

```text
EXEC-BOUNDARY-16～20    LOCKED
Phase 2 implementation   NOT STARTED
```

## Claim boundary

目前可支持的宣稱：

> Landlock、AppArmor/LSM 與 BPF-LSM 已在測試環境取得 substrate-level process-execution enforcement evidence；目前沒有任何候選被證明為 host-wide、可綁定 DROS 的 execution choke point。

目前不可支持的宣稱：

> DROS 已治理所有 CLI execution、AppArmor/BPF-LSM 已成為 DROS authority，或 universal host-wide CLI governance 已完成。

## Evidence references

- `exec_boundary_11_topology_bypass_claw-vm.json`
- `exec_boundary_15_enforcement_experiment_claw-vm.json`
- `exec_boundary_15_bpf_lsm_agentserver.json`
- `canonical_rust_cabi_policy_loaded_claw-vm.json`
- `landlock_dros_integration_claw-vm.json`
