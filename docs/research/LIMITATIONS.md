# Scientific Limitations & Architectural Boundaries

<!-- dros_component: dros-vep-standards -->
<!-- dros_description: Scientific Limitations and Substrate Abstraction Mismatches -->
<!-- dros_status: Active -->

## 1. Substrate Abstraction Mismatches

The fundamental research inquiry of VEP Post-Compromise is:
> *Does execution isolation remain sufficient when the Agent itself is compromised?*

In answering this, evaluating different security substrates under identical execution requests exposes inherent differences in abstraction level:

### 1.1 WASI (WebAssembly System Interface)
- **Native Level:** Bytecode sandbox operating via capability handles (preopened directories, socket descriptors).
- **Limitation:** WASI has no awareness of Agent cognition, LLM prompts, task lifecycle, or higher-order argument business logic. When an agent crafts `/workspace/legit_dir/../../etc/shadow` or executes `write()` within a preopened directory targeting unapproved file contents, WASI grants capability access because the directory descriptor is valid.
- **Reporting:** Marked as `WASI_NATIVE_SEMANTICS_UNSUPPORTED` rather than simulating pass/fail.

### 1.2 Microkernel & Hardware Capabilities (seL4, CHERI)
- **Native Level:** CSpaces / IPC endpoints (seL4) and CPU hardware capability-bounded registers (CHERI).
- **Limitation:** These substrates enforce memory safety and capability propagation at CPU/OS privilege boundaries. They are not authorization PDPs (Policy Decision Points) for multi-tenant LLM agents.

### 1.3 Formal Assurance (TLA+)
- **Native Level:** Mathematical state-machine specification and model checking.
- **Limitation:** Formal verification proves whether an abstract specification satisfies temporal logic invariants (e.g. `NoExecutionWhenRevoked`). It does not run in-band and cannot intercept an in-flight HTTP/C-ABI call. Thus, `execution` is strictly `NOT_APPLICABLE`.

### 1.4 Agent-Aware Execution Governance (DROS)
- **Native Level:** In-band Policy Enforcement Point (PEP) binding Principal, Task, Tool, Argument bounds, and Expiry.
- **Limitation:** Relies on accurate in-band interception hooks. Does not replace OS kernel memory isolation if untrusted native binaries execute outside the managed runtime.

---

## 2. Benchmark Design Principles

1. **Zero Fabrication**: No substrate is artificially modified to appear better or worse.
2. **Deterministic Replay**: Every decision must be 100% reproducible via fixed canonical requests and recorded hashes.
3. **Open Extensibility**: Adding new substrates requires only implementing `BaseSubstrateAdapter`.
