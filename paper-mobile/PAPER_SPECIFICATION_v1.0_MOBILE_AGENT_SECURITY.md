# 📑 Formal Paper Specification (v1.0 - Submission Baseline Frozen)
# 《Post-Compromise Security for Autonomous Mobile Agents: Deterministic Runtime Enforcement of Mobile Execution Authority》
<!-- dros_component: dros-mobile-agent-paper-spec-v1.0 -->
<!-- dros_depends: [DROS_SYSTEM_OVERHEAD_BENCHMARK_REPORT_ZH.md, RFC-001-VEP-Execution-Governance-Spec.md] -->
<!-- dros_description: 官方最終凍結版 Mobile Agent Paper Specification v1.0 (融入 5 大學術手術刀修剪：PSE 精確化、撤銷時序解耦、受保護路徑邊界) -->
<!-- dros_status: Active / Submission Baseline (Frozen v1.0) -->

> **Target Venues:** ACM MobiSys / USENIX Security / IEEE S&P / ACM SenSys  
> **Research Object:** Post-Compromise Mobile Execution Authority  
> **Reference Implementation:** DROS-Mobile  
> **Controlled Platform:** iOS (Swift/C-ABI) / Android (Kotlin/JNI/C-ABI) Mobile Execution Environment

---

## 🧭 Core Scientific Questions

> **Primary:**  
> **When an autonomous mobile Agent is fully compromised, can a trusted execution layer prevent unauthorized Agent intent from producing downstream protected mobile system effects?**

> **Secondary / Investigatory:**  
> **We investigate whether mobile execution authority can remain independently bounded, revocable, and auditable even when the cognitive controller is assumed to be fully compromised.**

### 🏛️ Central Security Thesis
$$\boxed{ \mathrm{Compromise}(\mathrm{Cognitive\ Controller}) \not\Rightarrow \mathrm{Compromise}(\mathrm{Mobile\ Execution\ Authority}) }$$

*The paper separates cognitive intent from execution authority and experimentally evaluates whether an untrusted, compromised AI process can be prevented from obtaining unauthorized access to protected mobile interfaces under the declared threat model and enforcement boundary.*

---

# 1. Abstract

Autonomous mobile agents increasingly combine learned or language-based decision processes with privileged mobile APIs and system services. This creates a post-compromise security problem distinct from conventional model-level robustness: once the autonomous controller is fully compromised, can unauthorized intent still obtain downstream mobile execution authority?

We formulate the **Post-Compromise Mobile Execution Authority Problem** and investigate whether a deterministic runtime enforcement layer can preserve execution authorization independently of controller integrity. We present **DROS-Mobile**, a reference implementation positioned between autonomous agent intent and protected mobile execution interfaces. The design separates cognitive intent from execution authority through explicit principal, capability, policy, and revocation checks.

We formalize three properties: **Unauthorized Protected System-Effect Invariance (P1)**, **Revocation-Bound Execution Authority (P2)**, and **Delegation Non-Escalation (P3)** under explicitly defined enforcement paths $\mathcal{E}_{\mathrm{protected}}$. We evaluate the system across nominal execution, fully compromised-agent behavior ($C^*$), adversarial API requests, authorization bypass attempts, capability replay, revocation races, and sustained stress workloads on iOS and Android environments.

The evaluation measures unauthorized protected system effects, containment rate, multi-stage revocation horizons ($T_{\mathrm{rev}}$ vs. $T_{\mathrm{RCU}}$), delegation propagation, decomposed enforcement latency, and runtime overhead. The results provide an experimentally reproducible basis for studying post-compromise security at the boundary between autonomous mobile cognition and operating-system-mediated execution.

---

# 2. Academic Contributions & Research Positioning

## 2.1 Contributions
* **C1 — Problem Formulation:**  
  We formulate the **Post-Compromise Mobile Execution Authority Problem**, establishing the formal decoupling between cognitive model compromise and mobile execution authority.
* **C2 — Formal Mobile Security Properties:**  
  We formalize three verifiable properties:
  1. **Unauthorized Protected System-Effect Invariance (P1)** ($\mathrm{Auth}(a)=0 \implies \mathrm{PSE}(a) \equiv 0$);
  2. **Revocation-Bound Execution Authority (P2)** ($t \ge t_r + \tau_r \implies \mathrm{Auth}=0 \ \land \ \mathrm{PSE} \equiv 0$);
  3. **Delegation Non-Escalation (P3)** ($\mathrm{Authority}_{\mathrm{child}} \subseteq \mathrm{Attenuate}(\mathrm{Authority}_{\mathrm{parent}})$).
* **C3 — Reference Architecture (DROS-Mobile):**  
  We design and implement DROS-Mobile, an in-process execution authority gate operating via C-ABI across iOS (Swift) and Android (JNI) platforms, explicitly scoping protection to declared interface paths $\mathcal{E}_{\mathrm{protected}}$.
* **C4 — Cross-Platform Empirical Evaluation (M1–M6):**  
  We construct a comprehensive evaluation matrix covering nominal execution, adversarial Black-box compromise ($C^*$), capability abuse, microsecond revocation races, and stress benchmarks.

## 2.2 Research Gap and Experimental Substrate Positioning
Existing research increasingly addresses post-compromise agent behavior, runtime authorization, execution mediation, and physical safety, but these lines often rely on fragmented experimental substrates and disparate assurance boundaries. A reproducible execution substrate that exposes the complete transition from compromised agent intent to protected system or physical effects can facilitate systematic evaluation of post-compromise execution security.

In this unified research paradigm:
* **DROS** provides an open, reproducible, executable reference substrate;
* **VEP** provides the implementation-independent evaluation and falsification protocol;
* **Mobile and UAV** instantiate the post-compromise execution security problem across digital system effects ($\mathrm{PSE} \equiv 0$) and cyber-physical kinetic envelopes ($\Delta u_{\mathrm{cmd}} \equiv 0 \land x(t) \in \mathcal{S}_{\mathrm{safe}}$), respectively.

---

# 3. System and Threat Model

```text
                Cognitive Plane
        ┌──────────────────────────┐
        │ LLM / Agent / Controller  │
        │          C*              │
        └────────────┬─────────────┘
                     │
              Arbitrary Intent
                     │
                     ▼
        ┌──────────────────────────┐
        │     DROS-Mobile          │
        │                          │
        │ Principal Resolution     │
        │ Capability Validation    │
        │ Policy Bitmask           │
        │ Revocation / Epoch Check │
        │ Argument Sanitization    │
        │ Cryptographic Provenance │
        └────────────┬─────────────┘
                     │
              ┌──────┴──────┐
              │             │
            DENY           ALLOW
              │             │
              X             ▼
                    Protected Execution
                      Boundary (E_prot)
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
             Storage         IPC         Network
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                 Protected System Effect (PSE)
```

## 3.1 Untrusted Controller Model ($C^*$)
The cognitive controller is modeled as an **adversarial black box**:
$$C^* : \mathcal{I} \rightarrow \mathcal{A}^* \quad \text{where} \quad \mathcal{A}^* \subseteq \mathcal{A}_{\mathrm{arbitrary}}$$
The attacker can generate arbitrary API requests, manipulate parameter buffers, replay expired tokens, and attempt vertical/horizontal privilege escalation.

## 3.2 Trusted Execution Boundary & Declared Path Scope ($\mathcal{E}_{\mathrm{protected}}$)
The assurance boundary is strictly scoped to the declared protected execution path:
$$\mathcal{E}_{\mathrm{protected}} = \{\text{all execution paths covered by the enforcement boundary}\}$$
* **Epistemic Scope:** DROS-Mobile enforces authorization for any action $a \in \mathcal{E}_{\mathrm{protected}}$. It does not claim protection for arbitrary OS effects outside its declared enforcement boundary.
* **Fundamental Epistemic Invariant:**
  $$\mathrm{ControllerIntegrity} = 0 \not\implies \mathrm{ExecutionAuthorityIntegrity} = 0$$

## 3.3 Out-of-Scope Disclosures
* Physical device memory tampering via hardware debugger / JTAG;
* Baseband processor compromise;
* OS kernel-level compromises (iOS kernel panic / Android rootkits);
* Secure Enclave hardware compromise.

---

# 4. Formal Security Properties

## 4.1 Property P1 — Unauthorized Protected System-Effect Invariance (UPSEI)
$$\boxed{ \forall a \in \mathcal{E}_{\mathrm{protected}}, \quad \mathrm{Auth}(a, s, t) = 0 \implies \mathrm{PSE}(a, s, t) \equiv 0 }$$

* **Protected System Effect ($\mathrm{PSE}$):** Explicitly defined as any state mutation, unauthorized read, or IPC transmission touching:
  1. Protected Mobile APIs (Camera, Photo Library, Contacts, Microphone);
  2. Financial & Privileged Services (Apple Pay, Android Keystore, SMS);
  3. Local Application Storage & Protected Keychain Entries;
  4. Outbound Network Sockets.
* **Non-Protected Local State:** Local in-memory variable mutations within the unprivileged Agent sandbox do not constitute $\mathrm{PSE}$.

---

## 4.2 Property P2 — Revocation-Bound Execution Authority
Let capability $c$ be revoked at timestamp $t_r$. Within a bounded revocation horizon $\tau_r$:
$$\boxed{ \mathrm{Revoked}(c, t_r) = 1 \implies \forall t \ge t_r + \tau_r, \quad \mathrm{Auth}(a_c, s, t) = 0 \ \land \ \mathrm{PSE}(a_c, s, t) \equiv 0 }$$

### Multi-Stage Revocation Horizon Decomposition:
* **$T_{\mathrm{RCU}}$:** Policy state pointer swap latency (atomic RCU swap $\approx 420\text{ ns}$).
* **$T_{\mathrm{decision}}$:** In-process authorization lookup latency ($\approx 500\text{ ns}$).
* **$T_{\mathrm{rev}}$ (Actual Revocation Enforcement Latency):**
  $$T_{\mathrm{rev}} = t_{\text{first guaranteed DENY}} - t_{\text{revocation commit}}$$
  *(Empirically measured at $T_{\mathrm{rev}} < 2.5\ \mu\text{s}$ under multi-threaded concurrency)*.

---

## 4.3 Property P3 — Delegation Non-Escalation
$$\boxed{ \mathrm{Authority}_{\mathrm{child}} \subseteq \mathrm{Attenuate}(\mathrm{Authority}_{\mathrm{parent}}) \quad \text{and} \quad \mathrm{UnauthorizedPropagation} \equiv 0 }$$

---

# 5. Experimental Evaluation Protocol (M1–M6 Ladder)

| Tier | Stage | Injected Adversarial Vector | Evaluated Metric & Success Criteria |
| :--- | :--- | :--- | :--- |
| **M1** | **Nominal Execution** | Legitimate Photo Library access | $\mathrm{PSE} = 1$, $P_{50} \le 1.70\ \mu\text{s}$, 0 false denials |
| **M2** | **Full Compromise** | Malicious intent issued ($C^*$) | Generation of unauthorized intent confirmed at cognition plane |
| **M3** | **Execution Containment** | Unauthorized SMS / Contact exfiltration | $\mathrm{Auth} = 0 \implies \mathrm{PSE} \equiv 0$ (100% containment) |
| **M4** | **Capability Abuse** | Stale tokens, type confusion, enum manipulation | $100\%$ Fail-closed rejection rate ($R_{\mathrm{FC}} = 1.0$) |
| **M5** | **Revocation Race** | Replay of revoked credential at $t_r + \Delta t$ | $T_{\mathrm{rev}}$ measurement ($< 2.5\ \mu\text{s}$), $0$ post-revocation $\mathrm{PSE}$ |
| **M6** | **High-Rate Stress** | 10,000 boundary mutations on iOS/Android | 0 crashes, no detectable memory growth, minimal energy overhead |

---

# 6. Overhead and Energy Disclosures (Observed Empirical Boundary)

* **Memory Footprint:** Observed under the specified 10,000-iteration test configuration: no detectable memory growth ($\Delta M = 0\text{ B}$ after initial pool allocation).
* **Energy Overhead:** Energy overhead estimated from measured execution cost ($<0.05\ \mu\text{J}$ per invocation in L1/L2 cache), avoiding 4G/5G radio wakeups.

---

# 7. Final Research Positioning

$$\boxed{ \text{Mobile Domain: Post-Compromise System Security } (\mathrm{PSE} \equiv 0) }$$
$$\Updownarrow$$
$$\boxed{ \text{UAV Domain: Post-Compromise Physical Security } (\Delta u_{\mathrm{cmd}} \equiv 0 \ \land \ x(t) \in \mathcal{S}_{\mathrm{safe}}) }$$

Both domains provide empirical evidence for the overarching paradigm:
$$\boxed{ \mathrm{Cognitive\ Compromise} \not\Rightarrow \mathrm{Execution\ Authority\ Compromise} }$$

---
*DROS-Mobile Formal Paper Specification v1.0 — Submission Baseline Frozen.* 📱💎⚖️🛡️⚙️
