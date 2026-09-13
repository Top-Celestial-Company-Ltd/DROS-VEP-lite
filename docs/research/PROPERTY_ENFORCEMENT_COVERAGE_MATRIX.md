# Post-Compromise Property × Enforcement Layer × Semantic Coverage Matrix

<!-- dros_component: dros-vep-standards -->
<!-- dros_description: Comprehensive Cross-Substrate Property and Semantic Coverage Synthesis -->
<!-- dros_status: Active -->

## 1. The Core Scientific Premise

> **"Capability isolation, resource sandboxing, formal assurance, and Agent-level execution governance represent distinct security properties. They cannot be collapsed into a single security score, nor can one substitute for another."**

```text
                    VEP
                     │
          Same Post-Compromise Scenarios
                     │
             Same Canonical Requests
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    DROS          Capability      Formal
       │          Substrates      Assurance
       │             │             │
       │       ┌─────┴─────┐       │
       │       │           │       │
      WASI    seL4       CHERI    TLA+
       │       │           │       │
       └───────┴───────────┴───────┘
                     │
              Canonical Evidence
                     │
             Deterministic Replay
```

---

## 2. Comprehensive Semantic Coverage Synthesis

| Security Property | Threat Vector Evaluated | DROS (`E2_SANDBOX_RUNTIME`) | WASI (`E2_SANDBOX_RUNTIME`) | seL4 (`E3_OS_KERNEL`) | CHERI (`E4_HARDWARE`) | TLA+ (`E5_FORMAL_ASSURANCE`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Principal Attribution** | PC-010 (Cross-Principal Action) | **ENFORCED** (Native binding) | **UNSUPPORTED** (No Agent identity) | **UNSUPPORTED** (Address space $\neq$ Agent ID) | **UNSUPPORTED** (Memory tag $\neq$ Agent ID) | **ASSURANCE** (Model Invariant) |
| **Task-Level Authorization** | PC-003 (Privilege Escalation) | **ENFORCED** (Task-scoped bitmap) | **ALLOW** (No privilege model) | **ENFORCED\*** (Capability authority absent in execution domain) | **ENFORCED** (Sealing violation) | **ASSURANCE** (Model Invariant) |
| **Tool / Action Binding** | PC-004 (Tool Substitution) | **ENFORCED** (Action whitelist) | **UNSUPPORTED** (No Tool concept) | **ENFORCED\*\*** (When tools represented as distinct capability endpoints) | **UNSUPPORTED** (Memory ptr $\neq$ Tool ID) | **ASSURANCE** (Model Invariant) |
| **Argument Semantic Bounds** | PC-005 (Argument Substitution) | **ENFORCED** (Prefix & business rules) | **UNSUPPORTED** (Descriptor granularity) | **UNSUPPORTED** (Kernel ignores JSON args) | **UNSUPPORTED** (HW ignores string semantics) | **ASSURANCE** (Model Invariant) |
| **Execution Boundary** | PC-001 (Unauthorized File Write) | **ENFORCED** (Scope confinement) | **ENFORCED** (Preopen boundary) | **ENFORCED** (Resource capability absent) | **ENFORCED\*\*\*** (Bounded capability fault) | **ASSURANCE** (Model Invariant) |
| **Egress Restriction** | PC-002 (Unauthorized Network Egress) | **ENFORCED** (Gateway filter) | **ENFORCED** (Socket rights flag) | **ENFORCED** (IPC driver cap missing) | **ENFORCED\*\*\*** (MMIO bounds fault) | **ASSURANCE** (Model Invariant) |
| **Scope Expansion** | PC-006 (Root Scope Containment) | **ENFORCED** (Scope confinement) | **ENFORCED\*\*\*\* (Configured preopen boundary) | **ENFORCED** (Rights cannot escalate) | **ENFORCED** (Bounds monotonicity) | **ASSURANCE** (Model Invariant) |
| **Temporal Expiry (TTL)** | PC-007 (Expired Authorization) | **ENFORCED** (Dynamic timer check) | **UNSUPPORTED** (No temporal timer) | **UNSUPPORTED** (No token TTL) | **UNSUPPORTED** (No temporal timer) | **ASSURANCE** (Model Invariant) |
| **Hot Revocation** | PC-008 (Revoked Authorization) | **ENFORCED** (In-band state revoke) | **UNSUPPORTED** (No revocation model) | **ENFORCED\*\*\*\*\* (`seL4_CNode_Revoke`) | **UNSUPPORTED\*\*\*\*\*\* (No pure HW revoke) | **ASSURANCE** (Model Invariant) |
| **Replay / Nonce Defense** | PC-009 (Duplicate Nonce Execution) | **ENFORCED** (Nonce cache check) | **UNSUPPORTED** (No nonce tracking) | **UNSUPPORTED** (No nonce tracking) | **UNSUPPORTED** (No nonce tracking) | **ASSURANCE** (Model Invariant) |

*\* Modeled conditional on capability authority in the modeled execution domain; seL4 enforces capability authority, not abstract Agent task authorization.*  
*\*\* Modeled conditional on tools being explicitly represented as distinct capability endpoints in userspace architecture; seL4 possesses no native Agent tool binding concept.*  
*\*\*\* Modeled conditional on the target resource/device being represented as a bounded memory/MMIO capability object.*  
*\*\*\*\* Enforced strictly within the configured preopen directory descriptor boundary; WASI does not possess general Agent authorization scope concepts.*  
*\*\*\*\*\* Models revocation of derived capability copies via `seL4_CNode_Revoke()` in CSpace, not revocation of an abstract Agent authorization token.*  
*\*\*\*\*\*\* Under pure CHERI ISA architecture (`CHERI_PURE_ISA_CAPABILITY_MODEL`), reported as `UNSUPPORTED`. Under `CHERI_CHERIBSD_RUNTIME`, CheriBSD OS provides temporal heap sweep.*

---

## 3. Key Research Insights

### 3.1 What Each Layer Natively Understands
1. **Hardware (CHERI)**:
   - Understands: Pointer tags, linear spatial memory bounds, register sealing, memory read/write/execute permissions.
   - Does NOT understand: File paths, HTTP tools, API arguments, Agent principals, token TTLs.
2. **Microkernel (seL4)**:
   - Understands: Unforgeable capability tokens, capability tree derivations (`CNode`), IPC endpoints, thread control blocks (`TCB`).
   - Does NOT understand: Higher-order JSON payloads, temporal access token expiry, LLM session identities.
3. **Bytecode Sandbox (WASI)**:
   - Understands: Preopened directory descriptors, basic socket capability flags.
   - Does NOT understand: Fine-grained argument prefix rules within granted directories, tool binding, dynamic revocation.
4. **Formal Assurance (TLA+)**:
   - Understands: State-machine invariants, temporal logic specifications, counterexample state traces.
   - Does NOT understand: Real-time network packets or in-flight C-ABI function calls (Zero runtime enforcement).
5. **Agent-Aware Execution Governance (DROS)**:
   - Understands: LLM Agent identities, dynamic tasks, tool action bindings, JSON argument bounds, temporal TTL, hot revocation, transaction nonces.
   - Does NOT substitute for: OS-level kernel memory isolation or hardware CPU memory protection if untrusted native code executes outside the managed runtime.

---

## 4. Scientific Conclusion

> **"Security strength is property-relative, not substrate-absolute."**  
> *(安全能力是相對於具體安全性質而言，而不是一個 substrate 的絕對屬性。)*

```text
                Agent semantic layer
                         │
       Principal ─ Task ─ Tool ─ Args ─ TTL ─ Replay
                         │
                         ▼
                       DROS (Agent-Aware Governance)
                         │
                         ▼
                Execution boundary
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
             seL4                  CHERI
       (Kernel Isolation)    (Hardware Capability)
```

The VEP Post-Compromise benchmark demonstrates that:
1. **DROS addresses a semantic enforcement boundary that is not natively represented by lower-level capability and memory-isolation substrates.**
2. A system with **hardware memory protection (CHERI)** and **microkernel isolation (seL4)** remains vulnerable to **Post-Compromise semantic attacks** (Argument Substitution, Tool Substitution, Cross-Principal Action) if Agent-level execution governance is absent.
3. Conversely, **Agent-level execution governance (DROS)** relies on runtime/kernel/hardware capability boundaries to ensure its Policy Enforcement Point (PEP) cannot be bypassed by untrusted binary execution.

VEP serves as an open, implementation-independent laboratory for quantifying these exact boundaries.
