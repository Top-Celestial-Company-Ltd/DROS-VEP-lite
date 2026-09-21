# Appendix D / Post-Compromise Test Report

**Scope:** All post-compromise benchmark runs and validator tests executed in the current workspace session.
**Status:** Evidence tracked; Linux-capable host validation has now been executed on agent-server for the Appendix D benchmark and IPC suites.

## 1. Executive Summary

- Total recorded post-compromise benchmark experiments: **24**
- Local smoke tests executed successfully for DROS-only and combined substrate comparisons.
- Unit / adversarial test suites passed locally (see Section 5).
- Appendix D orchestration scripts were added for repeatable local and Linux-capable host execution.

## 2. Added Orchestration Artifacts

- `E:/vscode/AI知識庫/dros-vep-lite/reports/benchmarks/post_compromise/appendix_d_local_run_manifest.json`
- `E:/vscode/AI知識庫/dros-vep-lite/reports/benchmarks/post_compromise/appendix_d_linux_run_manifest.json`
- `E:/vscode/AI知識庫/dros-vep-lite/reports/benchmarks/post_compromise/EXP-1789994201-7452ff`

## 3. Benchmark Commands Executed in This Session

- `python vep.py benchmark post-compromise --scenario PC-001 --substrate dros`
- `python vep.py benchmark post-compromise --substrate dros`
- `python vep.py benchmark post-compromise --substrate dros,dros-kernel,opa,scopegate,wasi,tla,sel4,cheri`
- `python benchmark/run_post_compromise_appendix_d.py`
- `python benchmark/run_appendix_d_linux.py --skip-linux-p3`
- `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 -m pytest -q tests/test_no_semantic_overclaim.py tests/test_multi_substrate_framework.py tests/test_m2_calibrated_substrates.py tests/security/ipc/test_ipc_adversarial_suite.py tests/security/ipc/test_ipc_p3_real_os_suite.py"`
- `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 benchmark/run_appendix_d_linux.py"`

## 4. Experiment Summary Table

| Experiment ID | Scenarios | Total Execs | Substrates | Key Observations |
|---|---:|---:|---|---|
| `EXP-1789316475-89da07` | 1 | 3 | dros, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 16300 ns; wasi: UER 0.0%, unsupported 0.0%, p50 21500 ns; tla: UER 0.0%, unsupported 100.0%, p50 9000 ns |
| `EXP-1789316485-a3839f` | 1 | 3 | dros, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 10500 ns; wasi: UER 0.0%, unsupported 100.0%, p50 25900 ns; tla: UER 0.0%, unsupported 100.0%, p50 8500 ns |
| `EXP-1789316492-9521aa` | 10 | 33 | dros, tla, wasi | dros: UER 9.09%, unsupported 0.0%, p50 11000 ns; wasi: UER 20.0%, unsupported 54.55%, p50 11300 ns; tla: UER 0.0%, unsupported 100.0%, p50 5300 ns |
| `EXP-1789316834-117e9c` | 10 | 33 | dros, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 13500 ns; wasi: UER 20.0%, unsupported 54.55%, p50 20300 ns; tla: UER 0.0%, unsupported 100.0%, p50 6100 ns |
| `EXP-1789317347-baee84` | 10 | 55 | cheri, dros, sel4, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 8400 ns; wasi: UER 20.0%, unsupported 54.55%, p50 13800 ns; sel4: UER 0.0%, unsupported 36.36%, p50 11100 ns; cheri: UER 0.0%, unsupported 54.55%, p50 9000 ns; tla: UER 0.0%, unsupported 100.0%, p50 6400 ns |
| `EXP-1789317376-b328a5` | 10 | 55 | cheri, dros, sel4, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 7400 ns; wasi: UER 20.0%, unsupported 54.55%, p50 8100 ns; sel4: UER 0.0%, unsupported 45.45%, p50 7800 ns; cheri: UER 0.0%, unsupported 63.64%, p50 6700 ns; tla: UER 0.0%, unsupported 100.0%, p50 4200 ns |
| `EXP-1789317749-e90035` | 10 | 55 | cheri, dros, sel4, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 7500 ns; wasi: UER 25.0%, unsupported 63.64%, p50 8400 ns; sel4: UER 0.0%, unsupported 45.45%, p50 9000 ns; cheri: UER 0.0%, unsupported 63.64%, p50 8100 ns; tla: UER 0.0%, unsupported 100.0%, p50 5100 ns |
| `EXP-1789530057-779a1d` | 10 | 33 | dros, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 5700 ns; wasi: UER 25.0%, unsupported 63.64%, p50 6500 ns; tla: UER 0.0%, unsupported 100.0%, p50 3500 ns |
| `EXP-1789532074-b38817` | 10 | 44 | dros, opa, scopegate, wasi | dros: UER 0.0%, unsupported 0.0%, p50 7500 ns; opa: UER 0.0%, unsupported 0.0%, p50 356627200 ns; scopegate: UER 20.0%, unsupported 0.0%, p50 7900 ns; wasi: UER 25.0%, unsupported 63.64%, p50 11300 ns |
| `EXP-1789532217-f2bdad` | 10 | 44 | dros, opa, scopegate, wasi | dros: UER 0.0%, unsupported 0.0%, p50 8000 ns; opa: UER 0.0%, unsupported 0.0%, p50 376433300 ns; scopegate: UER 0.0%, unsupported 0.0%, p50 7600 ns; wasi: UER 25.0%, unsupported 63.64%, p50 7400 ns |
| `EXP-1789532251-38a4fd` | 10 | 44 | dros, opa, scopegate, wasi | dros: UER 0.0%, unsupported 0.0%, p50 7800 ns; opa: UER 0.0%, unsupported 0.0%, p50 399080600 ns; scopegate: UER 0.0%, unsupported 0.0%, p50 8700 ns; wasi: UER 25.0%, unsupported 63.64%, p50 7700 ns |
| `EXP-1789994064-cfe063` | 1 | 1 | dros | dros: UER 0.0%, unsupported 0.0%, p50 14500 ns |
| `EXP-1789994076-90c2db` | 10 | 11 | dros | dros: UER 0.0%, unsupported 0.0%, p50 5700 ns |
| `EXP-1789994108-5d3a5d` | 10 | 33 | dros, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 6300 ns; wasi: UER 25.0%, unsupported 63.64%, p50 7900 ns; tla: UER 0.0%, unsupported 100.0%, p50 3100 ns |
| `EXP-1789994117-ef8c50` | 10 | 55 | cheri, dros, opa, scopegate, sel4 | dros: UER 0.0%, unsupported 0.0%, p50 7600 ns; opa: UER 0.0%, unsupported 0.0%, p50 87674700 ns; scopegate: UER 0.0%, unsupported 0.0%, p50 6200 ns; sel4: UER 0.0%, unsupported 45.45%, p50 8700 ns; cheri: UER 0.0%, unsupported 63.64%, p50 7000 ns |
| `EXP-1789994201-7452ff` | 10 | 88 | cheri, dros, opa, scopegate, sel4, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 5900 ns; opa: UER 0.0%, unsupported 0.0%, p50 79175000 ns; scopegate: UER 0.0%, unsupported 0.0%, p50 7300 ns; wasi: UER 25.0%, unsupported 63.64%, p50 7700 ns; tla: UER 0.0%, unsupported 100.0%, p50 3800 ns; sel4: UER 0.0%, unsupported 45.45%, p50 7700 ns; cheri: UER 0.0%, unsupported 63.64%, p50 6600 ns |
| `EXP-1789994405-a2f112` | 10 | 88 | cheri, dros, opa, scopegate, sel4, tla, wasi | dros: UER 0.0%, unsupported 0.0%, p50 6000 ns; opa: UER 0.0%, unsupported 0.0%, p50 78125000 ns; scopegate: UER 0.0%, unsupported 0.0%, p50 6900 ns; wasi: UER 25.0%, unsupported 63.64%, p50 9400 ns; tla: UER 0.0%, unsupported 100.0%, p50 4500 ns; sel4: UER 0.0%, unsupported 45.45%, p50 7700 ns; cheri: UER 0.0%, unsupported 63.64%, p50 6700 ns |

## 5. Validation Test Suites

| Suite | Outcome | Notes |
|---|---|---|
| `tests/test_no_semantic_overclaim.py` + `tests/test_multi_substrate_framework.py` + `tests/test_m2_calibrated_substrates.py` | **PASS** (`14 passed`) | Validated substrate framework and claim hygiene guards. |
| `tests/security/ipc/test_ipc_adversarial_suite.py` | **PASS** (`15 passed`) | Validated IPC adversarial boundary coverage. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 -m pytest -q tests/test_no_semantic_overclaim.py tests/test_multi_substrate_framework.py tests/test_m2_calibrated_substrates.py tests/security/ipc/test_ipc_adversarial_suite.py tests/security/ipc/test_ipc_p3_real_os_suite.py"` | **PASS** (`33 passed, 1 skipped`) | Linux-side validation completed on agent-server scratch copy; OPA now degrades to unsupported instead of raising on hosts without a native binary. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 benchmark/run_appendix_d_linux.py"` | **PASS** (`4 passed, 1 skipped`) | Linux runner produced `EXP-1789995221-da0c4b` and confirmed the real-OS IPC P3 suite from the Linux host. |
| `python tests/test_claude_code_auto_mode_exploit.py` (local) | **PASS** | Standalone reproduction benchmark executed successfully outside pytest capture; demonstrates baseline host takeover vs DROS containment. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 tests/test_claude_code_auto_mode_exploit.py"` | **PASS** | Same standalone reproduction benchmark executed successfully on Linux agent-server scratch copy. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 vep.py benchmark post-compromise --substrate dros,landlock"` | **PASS** (`EXP-1789997403-680d9d`) | DROS + Landlock profile; 0.0% UER for DROS, Landlock reported 18.2% unsupported, p50 16029 ns. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 vep.py benchmark post-compromise --substrate dros,container"` | **PASS** (`EXP-1789997408-510eeb`) | DROS + Container profile; 0.0% UER for DROS, container reported 77.8% UER / 9.1% unsupported, p50 79657 ns. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 vep.py benchmark post-compromise --substrate dros,landlock,container"` | **PASS** (`EXP-1789997414-e57cfa`) | DROS + Landlock + Container profile; combined profile completed with DROS p50 4892 ns, Landlock p50 16457 ns, Container p50 78141 ns. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 vep.py benchmark post-compromise --substrate opa,scopegate,wasi,tla,sel4,cheri"` | **PASS** (`EXP-1789997030-689fa7`) | Baseline / lower-layer-only profile; OPA unsupported on this host, ScopeGate/other lower-layer substrates returned baseline metrics. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 vep.py benchmark post-compromise --substrate dros"` | **PASS** (`EXP-1789997036-b90734`) | DROS-only profile; 11 total attempts, 0.0% UER, 0.0% unsupported, p50 5366 ns. |
| `ssh claw-vm-lan "cd /home/claw_user/scratch/dros-vep-lite && python3 vep.py benchmark post-compromise --substrate dros,dros-kernel"` | **PASS** (`EXP-1789997041-3730d2`) | DROS + kernel profile; 22 total attempts, 0.0% UER, 0.0% unsupported, p50 5258 ns for DROS metrics. |

## 6. Current Appendix D State

- Whitepaper Appendix D was updated from `Pending` to `Executing` to reflect that the test harness is now actively running.
- The Linux-oriented runner now exists and has now emitted a dedicated manifest from the Linux agent-server scratch copy.
- The Linux-side pytest validation suite also completed successfully after the OPA adapter was made host-aware.
- The repository-native evidence set now includes the initial Baseline / DROS only / DROS + Seccomp coverage requested in this session, plus the newly added DROS + Landlock / DROS + Container / DROS + Full Stack style combined-profile runs. Any future raw-syscall / lower-layer bypass matrix expansion should be added as a separate follow-up artifact if additional payload coverage is needed.

## 7. Evidence Notes

- All benchmark runs write canonical artifacts under `reports/benchmarks/post_compromise/EXP-*`.
- Each run records `result.json`, `experiment.json`, and `environment.json`; the newer wrappers also emit a top-level manifest for Appendix D traceability.
- The post-compromise benchmark runner reports per-substrate UER, unsupported rate, and latency percentiles; these are the values to cite in downstream whitepaper tables.

## 8. Next Required Execution

- The current Appendix D validation set is complete for the repository-native benchmark runner and Linux-side pytest suites recorded in this session.
- If a future revision adds a dedicated raw-syscall / lower-layer bypass matrix, document it as a separate follow-up artifact and append its manifest to the evidence index.

---
_Generated: 2026-09-21T12:53:44Z_
