# Substrate Capability Matrix

<!-- dros_component: dros-vep-standards -->
<!-- dros_description: Multi-Substrate Post-Compromise Capability and Semantic Matrix -->
<!-- dros_status: Active -->

This matrix documents the native capabilities, enforcement layers, execution profiles, and limitation boundaries across execution and assurance substrates evaluated in the VEP Post-Compromise benchmark.

| Property / Semantics | DROS (Runtime PEP) | DROS (Kernel C-ABI) | WASI (Preview1) | seL4 (Microkernel) | CHERI (Pure ISA) | CHERI (CheriBSD) | TLA+ (Assurance) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Execution Profile** | `DROS_INBAND_RUNTIME_PEP` | `DROS_KERNEL_CABI_PEP` | `WASI_PREVIEW1_DESCRIPTOR_SANDBOX` | `SEL4_SIM_CAPABILITY_MODEL` | `CHERI_PURE_ISA_CAPABILITY_MODEL` | `CHERI_CHERIBSD_RUNTIME` | `TLA_FORMAL_SPEC_MODEL_CHECKER` |
| **Substrate Type** | `RUNTIME` | `RUNTIME` | `RUNTIME` | `RUNTIME` | `RUNTIME` | `RUNTIME` | `ASSURANCE` |
| **Enforcement Layer** | `E2_SANDBOX_RUNTIME` | `E3_OS_KERNEL` | `E2_SANDBOX_RUNTIME` | `E3_OS_KERNEL` | `E4_HARDWARE` | `E2_SANDBOX_RUNTIME` / `E4` | `E5_FORMAL_ASSURANCE` |
| **Principal Attribution (PC-010)** | ✅ Native (DENY) | ✅ Native (DENY) | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | 📐 Model Invariant |
| **Task Authorization** | ✅ Native (DENY) | ✅ Native (DENY) | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | 📐 Model Invariant |
| **Tool / Action Binding (PC-004)** | ✅ Native (DENY) | ✅ Native (DENY) | ⚪ N/A: Out of Scope | ⚠️ Endpoint missing (DENY) | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | 📐 Model Invariant |
| **Argument Semantic Bounds (PC-005)** | ✅ Native (DENY) | ✅ Native (DENY) | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | 📐 Model Invariant |
| **Filesystem / Object Access (PC-001)** | ✅ Scope prefix (DENY) | ✅ Kernel filter (DENY) | ✅ Preopen missing (DENY) | ⚠️ Endpoint missing (DENY) | ⚠️ Tag/Bounds fault (DENY)* | ⚠️ Tag/Bounds fault (DENY)* | 📐 Model Invariant |
| **Network Egress (PC-002)** | ✅ Scope / Gateway (DENY) | ✅ Kernel filter (DENY) | ✅ Socket flag denied (DENY) | ⚠️ IPC Endpoint missing (DENY) | ⚠️ MMIO Bounds fault (DENY)* | ⚠️ MMIO Bounds fault (DENY)* | 📐 Model Invariant |
| **Privilege Escalation (PC-003)** | ✅ Scope check (DENY) | ✅ Kernel filter (DENY) | ❌ Allow (WASI lacks priv model) | ⚠️ TCB capability missing (DENY) | ⚠️ Sealing violation (DENY) | ⚠️ Sealing violation (DENY) | 📐 Model Invariant |
| **Scope Expansion (PC-006)** | ✅ Scope check (DENY) | ✅ Kernel filter (DENY) | ✅ Preopen boundary (DENY) | ⚠️ Rights cannot escalate (DENY) | ⚠️ Bounds Monotonicity (DENY) | ⚠️ Bounds Monotonicity (DENY) | 📐 Model Invariant |
| **Temporal Expiry [TTL] (PC-007)** | ✅ Dynamic timer (DENY) | ✅ Dynamic timer (DENY) | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | 📐 Model Invariant |
| **Hot Revocation (PC-008)** | ✅ In-band state (DENY) | ✅ In-band state (DENY) | ⚪ N/A: Out of Scope | ⚠️ seL4_CNode_Revoke (DENY)** | ⚪ N/A: Out of Scope (Pure HW) | ⚠️ CheriBSD temporal sweep (DENY) | 📐 Model Invariant |
| **Replay / Nonce Protection (PC-009)** | ✅ Nonce cache (DENY) | ✅ Nonce cache (DENY) | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | ⚪ N/A: Out of Scope | 📐 Model Invariant |
| **Deterministic Evidence** | ✅ SHA256 Audit log | ✅ SHA256 Audit log | ✅ Audit trace | ✅ Kernel trace | ✅ Trap evidence | ✅ Sweep log | 📐 Counterexample trace |

*\* Modeled conditional on the target resource/device being represented as a bounded memory/MMIO capability object.*  
*\*\* Models revocation of derived capability copies in CSpace, not an abstract Agent authorization token.*

---

### Scientific Grounding & Interpretation Rules

1. **`N/A: Out of Scope` is Not a Security Failure**:
   - Marking `WASI`, `seL4`, or `CHERI` as `⚪ N/A: Out of Scope` for argument-level semantics (PC-005) or temporal token expiry (PC-007) reflects their true architectural abstraction (operating on descriptors, capabilities, and memory bounds, rather than LLM application JSON structures). Microkernels and hardware architectures are deliberately decoupled from application-level semantic parsing.
2. **Capability Revocation $\neq$ Agent Authorization Revocation**:
   - `seL4_CNode_Revoke()` removes derived capability copies from a CSpace tree. It is an operating system capability mechanism, fundamentally distinct from an application-level Agent policy revocation.
3. **Hardware Architecture vs. Runtime OS (CHERI vs. CheriBSD)**:
   - Pure CHERI ISA architecture possesses no concept of temporal token revocation (PC-008 = `N/A: Out of Scope`). When paired with CheriBSD's temporal safety runtime (Cornucopia), heap revocation is performed via memory sweeps.
4. **Transparent Execution Accounting**:
   - Total executions evaluated across all 5 substrates:
     $$(\text{10 Scenarios} \times \text{5 Substrates}) + (\text{1 Replay Phase [PC-009]} \times \text{5 Substrates}) = 50 + 5 = 55\text{ Execution Records}$$
