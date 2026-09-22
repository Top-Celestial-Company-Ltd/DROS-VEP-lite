# Agent CLI Execution Topology Matrix

研究 protocol：`PROTO-AGENT-CLI-COMPLETE-MEDIATION-2026-v1.0`

Round 1 狀態：`INSUFFICIENT_PUBLIC_EVIDENCE`

矩陣中的 `C` 只表示來源直接描述或約束該 topology；`U` 表示目前公開證據不足。`U` 不得轉寫為 `N`。`PARTIAL` 與 `TOPOLOGY_DEPENDENT` 不得簡化成安全性總評。

| solution | version | declared_boundary | execution_authority | ET-01 | ET-02 | ET-03 | ET-04 | ET-05 | ET-06 | ET-07 | ET-08 | ET-09 | ET-10 | ET-11 | ET-12 | ET-13 | ET-14 | evidence_level | source_count | live_test_status | complete_mediation_status | limitations | last_verified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OpenAI Codex CLI | rolling main / advisory fixed 0.39.0 | Linux sandbox helper / configured child-process surface | sandbox policy and OS substrate | U | U | C | C | C | C | U | C | C | C | U | U | C | U | E2/E3 | 3 | NOT_SELECTED | PARTIAL | Public sources describe a configured sandbox boundary and a version-scoped advisory; they do not establish general topology closure or DROS authority binding. |  |
| Claude Code | living documentation / advisory fixed 2.1.64 | Bash/PowerShell/Monitor command surface and child processes | permission layer plus optional sandbox | U | U | C | C | C | C | C | C | C | C | U | U | C | C | E1/E3 | 3 | NOT_SELECTED | PARTIAL | Documentation states fallback and bypass modes; coverage is command-surface scoped and does not establish host-wide mediation. |  |
| Gemini CLI | rolling main | Selected sandbox provider and tool-call policy engine | tool policy plus Docker/Podman/Seatbelt/gVisor/LXC provider | U | U | C | C | C | C | U | C | C | C | U | U | C | C | E1 | 2 | NOT_SELECTED | TOPOLOGY_DEPENDENT | Provider, platform, opt-in, mounts, network, expansion, and runtime configuration materially change the boundary. |  |
| Cursor | living documentation | Local shell sandbox or Cloud Agent VM | approval/run mode plus platform sandbox | U | U | C | C | C | C | C | C | U | C | U | U | U | C | E1 | 3 | NOT_SELECTED | TOPOLOGY_DEPENDENT | Local, SDK, and Cloud Agent boundaries are distinct; unsupported/full-system commands may run outside the local sandbox with approval. |  |
| OpenHands | living documentation / V0 legacy runtime | Docker action-execution runtime | deployment-configured container runtime | U | U | C | C | C | C | U | C | U | C | U | C | C | C | E1 | 2 | NOT_SELECTED | TOPOLOGY_DEPENDENT | Container boundary depends on operator configuration, image, mounts, network, runtime, and deployment topology. |  |
| Landlock | Linux kernel documentation | Self-applied inherited filesystem/network/IPC restrictions | kernel LSM rights | C | U | C | C | C | C | U | C | U | C | U | C | C | U | E1 | 2 | T: substrate only | PARTIAL | Mechanism-level restrictions do not establish identity/PDP binding, revocation, or host-wide complete mediation. |  |
| AppArmor/LSM | Linux kernel documentation | Loaded task-centered MAC profile | profile rules enforced by LSM | C | U | C | C | C | C | C | U | C | C | U | C | C | U | E1 | 2 | T: substrate only | PARTIAL | Module presence is not policy enforcement; loaded profile scope and alternate topology closure remain unproven. |  |
| BPF-LSM | Linux kernel documentation | Attached eBPF LSM hooks | privileged verifier-accepted BPF program | C | U | C | U | U | U | C | U | C | U | U | C | C | U | E1 | 1 | T: substrate only | PARTIAL | Hook attachment and a tested denial do not establish all execution hooks, identity binding, or topology closure. |  |
| Seccomp | Linux kernel documentation | Syscall filter inherited by eligible descendants | syscall number/argument filter | C | U | C | C | C | C | U | U | U | C | U | C | C | U | E1 | 1 | T: defense-in-depth only | PARTIAL | Kernel documentation explicitly distinguishes syscall filtering from a complete sandbox and provides no Agent identity/capability semantics. |  |
| OCI container runtime | rolling runtime-spec | Configured namespaces/cgroups/capabilities/LSM/filesystem jail | runtime and host kernel configuration | U | U | C | C | C | C | U | C | U | C | U | C | C | C | E1 | 1 | NOT_SELECTED | TOPOLOGY_DEPENDENT | Specification semantics are not evidence that a particular deployment mediates every process path or runtime API. |  |
| IPE | Linux kernel documentation | Integrity policy with configured integrity provider | kernel integrity policy | C | U | U | U | C | C | C | U | C | C | U | U | U | U | E1 | 1 | NOT_SELECTED | PARTIAL | IPE is integrity enforcement, not generic Agent authorization; interpreted execution requires interpreter cooperation. |  |

## Round 1 interpretation

- 沒有候選達到 `COMPLETE_MEDIATION_ESTABLISHED`。
- Agent CLI 方案主要是 `PARTIAL` 或 `TOPOLOGY_DEPENDENT`。
- Landlock、AppArmor、BPF-LSM、Seccomp、OCI 與 IPE 的來源只能證明 mechanism-level scope，不能單獨證明 DROS authority binding 或 host-wide topology closure。
- 詳細 source provenance 見 `../sources/sources.json` 與 `../research/public_source_scan_round1.md`。

