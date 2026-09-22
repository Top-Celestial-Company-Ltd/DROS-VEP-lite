# EXEC-BOUNDARY-15 Closure Report

Date: 2026-09-22
Primary host: `agentserver`
Reference host: `claw-vm`
Scope: Phase 2 candidate enforcement feasibility only

## Final verdict

```text
EXEC-BOUNDARY-15       CLOSED
Verdict                 BOUNDARY_SELECTION_REQUIRED
Candidate SUCCESS       0
Overall                 NO_CANDIDATE_HOST_CHOKEPOINT_CONFIRMED
```

This does not mean that Linux has no host choke point, and it does not mean that every candidate failed. It means that, under the tested kernel, privilege, toolchain, and runtime conditions, no candidate was proven to be simultaneously host-wide, pre-exec, bindable to canonical DROS authority, and non-bypassable.

## Evidence ladder

```text
Capability
    ↓
Live substrate enforcement
    ↓
Host-wide topology coverage
    ↓
Canonical DROS authority binding
```

This closure crosses only the second layer. The third and fourth layers must not be inferred from it.

## Candidate matrix

| Candidate | Live enforcement evidence | Host-wide choke point | DROS authority binding | Final status |
|---|---|---|---|---|
| Landlock | DENY/ALLOW evidence on a self-restricted process | Not established; topology-scoped | Not connected | `SUBSTRATE_ENFORCEMENT_CONFIRMED_BUT_NOT_CHOKEPOINT` |
| AppArmor/LSM | Enforce profile denied `execve`, `execveat(AT_EMPTY_PATH)`, and a `dash` child path; unconfined baseline allowed | Full topology not tested | Not connected | `SUBSTRATE_ENFORCEMENT_CONFIRMED_BUT_NOT_CHOKEPOINT` |
| BPF-LSM | Object compiled/loaded; libbpf attached; new SSH `/bin/bash` was denied; baseline allowed after loader termination | Full topology not tested | Not connected | `SUBSTRATE_ENFORCEMENT_CONFIRMED_BUT_NOT_CHOKEPOINT` |
| Container runtime | No live DROS enforcement evidence | Deployment-topology dependent | Not connected | `TOPOLOGY_DEPENDENT_PENDING` |
| Seccomp | Fixed syscall filtering | Not a dynamic DROS authority | Not applicable | `DEFENSE_IN_DEPTH_ONLY` |

## Architecture decision gate

```text
15 candidate enforcement
        ↓
        No candidate SUCCESS
        ↓
Architecture decision required
        ├─ accept explicitly topology-scoped enforcement
        ├─ investigate another host/runtime boundary
        └─ redesign the canonical interception seam
```

Until this decision is made:

```text
EXEC-BOUNDARY-16..20    LOCKED
Phase 2 implementation   NOT STARTED
```

## Claim boundary

Supported claim:

> Landlock, AppArmor/LSM, and BPF-LSM have substrate-level process-execution enforcement evidence in the tested environments. No candidate has been proven to be a host-wide, DROS-bindable execution choke point.

Not supported:

> DROS governs all CLI execution; AppArmor/BPF-LSM is the DROS authority; or universal host-wide CLI governance is complete.

## Evidence references

- `exec_boundary_11_topology_bypass_claw-vm.json`
- `exec_boundary_15_enforcement_experiment_claw-vm.json`
- `exec_boundary_15_bpf_lsm_agentserver.json`
- `canonical_rust_cabi_policy_loaded_claw-vm.json`
- `landlock_dros_integration_claw-vm.json`
