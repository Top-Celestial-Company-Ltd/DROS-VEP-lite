# VEP M6 Pilot — Pre-flight Report

**Document ID:** `VEP-M6-PREFLIGHT-2026-09-21`
**Specification:** `VEP-M6-PILOT-P0-4-v1.1`
**Status:** `BLOCKED — WASI / ORACLE FEASIBILITY INCOMPLETE`
**Execution boundary:** Pre-flight only; no formal Phase 0–4 execution
**Date:** 2026-09-21 (Asia/Taipei)

## 1. Decision summary

### READY

None. The pre-flight did not reach a state in which the DROS C ABI target and the external observation paths can be declared ready for formal freeze.

### BLOCKED

1. No standalone WASI runtime was found on the Ubuntu agent-server (`wasmtime`, `wasmer`, and `wasm3` are absent). Node.js 22.23.2 exposes an experimental `node:wasi` module, but its M6 version/profile and executable fixture have not been frozen.
2. S1/S2 oracle feasibility smoke tests passed, but the formal external-oracle contract is not yet configured or validated. Tool presence or a smoke observation is not equivalent to an independent oracle with documented coverage, timestamp/sequence evidence, blind spots, and failure modes.
3. The canonical Rust C ABI repository in the Windows workspace is dirty. A clean Linux build was completed from the recorded HEAD, but the relationship between that clean commit and the uncommitted Windows changes remains a human decision.
4. The canonical Linux release build succeeded, but the existing Rust library smoke test could not run with `cargo test --locked --lib`: Cargo reported that the lockfile version 4 requires `-Znext-lockfile-bump`. The lockfile was not modified.
5. The current Rust FFI implementation contains policy-loading TODOs and demonstration/mock decision logic. It is not evidence of a verified policy-enforcing boundary.

### NEEDS HUMAN DECISION

1. Select and freeze an approved WASI runtime/profile for the M6 Ubuntu environment. Node `node:wasi` is currently only a candidate because the runtime reports itself as experimental and no M6 fixture has been exercised.
2. Decide whether the current dirty Rust worktree is the intended M6 source, or whether M6 must use a clean commit/tag.
3. Decide whether the current `dros-core-rs` FFI implementation is only a boundary-inventory target or may later become the implementation target for formal Phase 0–4 testing after remediation.
4. Decide whether the lockfile/toolchain mismatch is resolved by pinning a compatible Cargo toolchain or by an explicitly reviewed lockfile/toolchain amendment. Do not change it result-driven during this pre-flight.

## 2. Frozen scope for this pre-flight

The following scope was used without modification:

- Substrates: DROS and WASI only.
- Properties: P1 Complete Mediation, P5 Attribution, P6 Revocation.
- Protected effects: S1 file read/write/delete and S2 outbound network connection/transmission.
- Execution host: Ubuntu agent-server (`node31` / `192.168.100.31`) for canonical execution; Windows is authoring and review only.
- Canonical DROS target: `dros-microkernels/dros-core-rs` Rust `extern "C"` FFI.
- `dros-vep-lite` Python `DrosAdapter` is a reference adapter and is not C ABI evidence.
- No formal Phase 0–4 test, Gate 0–4 result, preregistration tag, or security conclusion was produced.

## 3. Source and provenance

| Artifact | SHA-256 | Observation |
|---|---|---|
| User-provided execution specification | `11247CC2844FA6C2754298087DC9801061361838CEA0411064426A46FF82CD5C` | Read from the supplied attachment; pre-registration candidate, pending human freeze |
| `dros-vep-lite/spec/RFC-001-VEP-Execution-Governance-Spec.md` | `3CD6686A4F4EAFF1B50F25399D01D9A6A55B13F19DDAA2A5AA92E577321D547B` | Implementation-independent VEP protocol |
| `.agents/docs/agent-server-research-test-environment.md` | `351ACA1BF89B772F1F8169168D8448C29A3A5B3FA793F59767529480F11871CF` | Previously captured host facts; not a live observation in this run |

## 4. Canonical target inventory

### 4.1 Rust C ABI target

| Item | Value |
|---|---|
| Repository | `dros-microkernels/dros-core-rs` |
| Recorded HEAD | `754858d88ed36e8f27a26d6f92a6c00f87a32898` |
| Package version | `7.2.0` |
| Crate types | `cdylib`, `staticlib`, `rlib` |
| Worktree | Dirty: modified `README.md`, `src/ffi.rs`, `src/syscall_hardener.rs`; untracked `README_zh.md` |
| `Cargo.toml` SHA-256 | `B386EAD87CF3FCF95DF5E298B0BD8D0FDBB6F540348F75EB71B4EFF6AAB8DB17` |
| `src/ffi.rs` SHA-256 | `72BDD9B08F3D01CA5677E31CF0F4DB4859DFDD720988D6A019BF2772BF84643E` |
| `src/syscall_hardener.rs` SHA-256 | `E6D486193FA04E8CEBA9C0A5C299BC644652EFF9156120E841CAAAF9EBF70F64` |

Observed exported Rust symbols include:

- `dros_v2_init`
- `dros_v2_reload`
- `dros_v2_version`
- `dros_v2_health`
- `dros_v2_last_error`
- `dros_v2_free`
- `dros_v2_decide`
- `dros_v2_decide_explain`
- `dros_v2_audit_pop`
- `dros_v2_audit_loss_count`

### 4.1.1 Linux clean-build evidence

The canonical commit was cloned into `/home/ai_user/m6-preflight/dros-core-rs` on the Ubuntu agent-server and checked out detached at `754858d88ed36e8f27a26d6f92a6c00f87a32898`. Source files were clean before the build; the repository tracks some generated `target/` artifacts, which changed during the build in the disposable scratch checkout.

Live environment:

- Hostname: `agentserver`
- OS: Ubuntu 24.04.4 LTS
- Kernel: `6.8.0-139-generic`
- Architecture: `x86_64`
- Rust/Cargo: `1.97.1`
- GCC: `13.3.0`
- Docker: `29.1.3`
- Node.js: `22.23.2`
- Node `node:wasi`: module present; `WASI` export present; runtime reports experimental status
- Build command: `cargo build --locked --release`
- Build result: success in 14.36 seconds
- Build warnings: two unused imports (`AlignedBuf`, `Deserialize`)
- Library smoke: `cargo test --locked --lib` did not run because Cargo rejected lockfile version 4 and requested `-Znext-lockfile-bump`; no lockfile change was made

The resulting artifacts were:

- `libdros_core_rs.so`
- `libdros_core_rs.a`
- `libdros_core_rs.dll.a`

`ldd` resolved the shared object against `libgcc_s.so.1`, `libc.so.6`, and the standard x86_64 dynamic loader. `nm -D` confirmed these exported symbols:

- `dros_v2_init`
- `dros_v2_reload`
- `dros_v2_decide`
- `dros_v2_decide_explain`
- `dros_v2_free`
- `dros_v2_audit_pop`
- `dros_v2_audit_loss_count`

### 4.2 VajraClaw header surfaces

The following headers were inventoried as additional ABI surfaces, not assumed canonical:

- `DROS-VajraClaw/vajra_claw.h`
- `DROS-VajraClaw/core/vajra_claw.h`

They export initialization, dynamic-policy, ephemeral-rule, evaluation, audit, and license functions. Their relationship to the Rust canonical target was not verified in this pre-flight.

### 4.3 VEP Python adapter

`dros-vep-lite/vep.py` registers:

- `dros` → `DrosAdapter(deployment_mode="runtime")`
- `dros-kernel` → `DrosAdapter(deployment_mode="kernel")`

`dros-vep-lite/substrates/dros/adapter.py` selects profiles named `DROS_INBAND_RUNTIME_PEP` and `DROS_KERNEL_CABI_PEP`, but the adapter is Python implementation code and does not itself establish that the Rust C ABI shared library is loaded or exercised. It is therefore classified as `REFERENCE_ADAPTER`, not `CANONICAL_ACTIVE` C ABI evidence.

## 5. Interface and implementation findings

The Rust FFI source contains the following unresolved items relevant to M6:

- `dros_v2_init` has `TODO: 解析 policy_path 載入規則`.
- `dros_v2_reload` has `TODO: 解析 policy_path 載入新規則`.
- `dros_v2_decide_explain` contains `MOCK FOR DEMO` allow logic based on URI/tenant text.
- `rule_id` and `policy_version` are placeholder values.
- `trace_id` is a zero-filled placeholder with a TODO.
- Audit overflow is counted as loss; no pre-flight evidence yet establishes whether this satisfies the M6 audit requirements.

These are inventory findings only. No implementation change was made.

## 6. Environment and build feasibility

### Windows authoring host

Observed:

- Rust: `rustc 1.96.0 (ac68faa20 2026-05-25)`
- Cargo: `cargo 1.96.0 (30a34c682 2026-05-25)`
- Python: `3.12.0`
- Docker executable present
- GCC not available
- MSVC `link.exe` not available

`cargo check --locked` was attempted in the dirty Rust worktree. It failed because the MSVC target could not find `link.exe`. This is a local tooling observation only and is not a Linux build result.

### Ubuntu agent-server

The configured agent-server is `agentserver` / `node31` at `192.168.100.31`, with Ubuntu Linux and a clean research/test role. Live access was subsequently established and the environment and clean canonical build were observed. The following remain unverified:

- WASI runtime/profile and executable fixture
- S1/S2 external oracle feasibility as an independent observation path
- complete runtime path enumeration

Previously captured host facts are retained as historical provenance only; they are not promoted to current live evidence.

## 7. Trust-boundary and path inventory status

The intended seam is:

```text
Caller / adapter
    -> Rust C ABI
    -> DROS policy decision implementation
    -> execution adapter / host boundary
    -> S1 filesystem or S2 network effect
```

The following paths require live Linux enumeration before Gate 1 can be considered:

- exported C ABI and dynamic-library loading
- Go/Python/SDK adapters
- alternate FFI and alternate runtime
- subprocess and privileged service paths
- IPC paths
- filesystem path
- network path
- raw syscall and Seccomp path
- replay/stale authorization path
- authorization/execution race path

Additional implementation finding: the Rust C ABI source exposes decision, explanation, lifecycle, and audit functions, but no direct S1 filesystem or S2 network effect executor was found in the canonical `src` tree. The handoff from an ABI decision to an actual protected effect therefore remains an external adapter/path that must be identified and pinned before the C ABI can be treated as the complete execution seam. The `syscall_hardener` module also contains raw syscall wrappers and Seccomp installation logic, which must be classified separately from the semantic C ABI seam.

Current status: `BLOCKED — live path enumeration and decision-to-effect handoff not completed`.

## 8. External oracle status

No formal external-oracle validation was run. A pre-flight smoke test was run outside the DROS target:

- S1 `inotifywait` observed `CREATE`, `MODIFY`, and `DELETE` for a temporary probe file.
- S2 an independent Python listener observed a 19-byte loopback payload `VEP-M6-ORACLE-SMOKE`.
- The smoke test did not exercise DROS authorization, WASI, policy decisions, or any formal N=100 gate.
- The S1 observer emitted the literal `%N` when asked for nanosecond formatting; timestamp precision is therefore not yet accepted as a final oracle property. Event order was visible, but the formal sequence/timestamp contract remains open.
- The temporary smoke directory was under `/home/ai_user/m6-preflight` and was configured for cleanup; its console output is supporting observation, not a retained raw experimental artifact.

Available tool inventory on Ubuntu was:

| Tool | Status | Possible use |
|---|---|---|
| `inotifywait` | present | S1 filesystem observation candidate |
| `tcpdump` | present | S2 packet observation candidate |
| `strace` | present | syscall/path diagnostics, not independent ground truth by itself |
| `bpftrace` | present | kernel observation candidate, subject to privilege and program validation |
| `ss` | present | socket-state diagnostics |
| `unshare` | present | namespace feasibility |
| `auditctl` | missing | audit-subsystem option unavailable in current image |
| `tshark` | missing | packet-analysis option unavailable in current image |
| `socat` | missing | simple independent endpoint helper unavailable in current image |

Tool presence alone does not satisfy the oracle requirement. An observation point, coverage statement, timestamp/sequence method, blind spots, failure modes, and substrate-log isolation check remain to be designed and validated.

Required but unverified:

- S1 observer outside the DROS trust boundary
- S2 listener/packet observation outside the DROS trust boundary
- timestamp and sequence evidence
- blind spots and failure modes
- substrate-log isolation comparison

Current status: `PARTIAL — smoke passed; independent oracle contract not yet validated`.

## 9. Negative-control feasibility status

The specification-defined classes are understood but not accepted as feasible until the target can be executed on Ubuntu and the external oracles can observe effects:

- P1: explicit path not passing through the C ABI PEP
- P5: missing or incorrect principal mapping
- P6: stale capability or disabled revocation propagation

Current status: `NEEDS HUMAN DECISION` for final path selection, and `BLOCKED` for execution validation.

## 10. Claim boundary

This report does **not** establish:

- complete mediation
- absence of bypass
- security or complete security
- DROS superiority over WASI
- P1/P5/P6 pass status
- any latency, coverage, or blocking-rate result

The strongest supported statement is:

> The canonical DROS Rust C ABI target and several related ABI/documentation surfaces were located, but the M6 pre-flight cannot be completed until authenticated Ubuntu execution access, a clean canonical build, and independent S1/S2 observation paths are available.

## 11. Stop condition

Per the execution specification, stop after pre-flight reporting.

No `vep-prereg-v1` tag was created. No formal Phase 0–4 artifact or result was generated. Human review is required before any remediation, freeze, or formal experiment begins.
