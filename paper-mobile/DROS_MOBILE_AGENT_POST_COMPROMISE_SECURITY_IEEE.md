# Post-Compromise Security for Autonomous Mobile Agents: Deterministic Runtime Enforcement of Mobile Execution Authority

**Chun-Cheng (Jimmy) Chen**  
*Top-Celestial Company Ltd.*  
Taipei, Taiwan R.O.C.  
jimmychen@dr-os.io  

---

## Abstract
Autonomous mobile agents increasingly combine learned or language-based decision processes with privileged mobile APIs and operating system services. This creates a post-compromise security problem distinct from conventional model-level robustness: once the autonomous controller is fully compromised, can unauthorized intent still obtain downstream mobile execution authority?

We formulate the **Post-Compromise Mobile Execution Authority Problem** and investigate whether a deterministic runtime enforcement layer can preserve execution authorization independently of controller integrity. We present **DROS-Mobile**, a reference implementation positioned between autonomous agent intent and protected mobile execution interfaces. The design separates cognitive intent from execution authority through explicit principal, capability, policy, and revocation checks.

We formalize three properties: **Unauthorized Protected System-Effect Invariance (P1)**, **Revocation-Bound Execution Authority (P2)**, and **Delegation Non-Escalation (P3)** under explicitly declared protected execution paths $\mathcal{E}_{\mathrm{protected}}$. We evaluate the system across nominal execution, fully compromised-agent behavior ($C^*$), adversarial API requests, authorization bypass attempts, capability replay, revocation races, and sustained stress workloads on iOS and Android environments.

The evaluation measures unauthorized protected system effects, containment rate, multi-stage revocation horizons ($T_{\mathrm{rev}}$ vs. $T_{\mathrm{RCU}}$), delegation propagation, decomposed enforcement latency, and runtime overhead. The results provide an experimentally reproducible basis for studying post-compromise security at the boundary between autonomous mobile cognition and operating-system-mediated execution.

**Keywords:** Mobile Agent Security, Post-Compromise Security, Runtime Enforcement, Execution Authority, Protected System Effect, Mobile Operating Systems.

---

## 1. Introduction
The integration of Large Language Models (LLMs), Vision-Language-Action (VLA) models, and autonomous task-planning agents into mobile operating systems (iOS and Android) has rapidly expanded the surface for privileged system interactions. Modern mobile agents are granted capabilities to autonomously inspect photo galleries, parse SMS verification codes, invoke contact books, manipulate local application storage, and initiate financial transactions.

However, granting generative models unconstrained access to privileged mobile APIs introduces a fundamental security dilemma. When an on-device cognitive agent is hijacked via prompt injection, adversarial multi-modal perception, or compromised retrieval augmented memory, internal model alignment cannot prevent the emission of unauthorized, malicious system calls.

In mobile security, an attack is characterized by immediate, irreversible digital side-effects: exfiltrating sensitive PII, unauthorized financial transfers via Apple Pay / Android Keystore, or unauthorized background network beaconing. This reality leads to the central scientific question of this work:

> **When an autonomous mobile agent is fully compromised, can a trusted execution layer prevent unauthorized agent intent from producing downstream protected mobile system effects?**

We formulate the core security thesis:
$$\boxed{ \mathrm{Compromise}(\mathrm{Cognitive\ Controller}) \not\Rightarrow \mathrm{Compromise}(\mathrm{Mobile\ Execution\ Authority}) }$$

To investigate this thesis, we present **DROS-Mobile**, an open-source reference implementation operating as a deterministic binary gate via C-ABI between autonomous agent intent and protected mobile SDK interfaces. 

### Academic Contributions
1. **Problem Formulation:** We formulate the Post-Compromise Mobile Execution Authority Problem, formally decoupling cognitive model compromise from downstream mobile execution authority.
2. **Formal Security Properties:** We formalize three verifiable properties: Unauthorized Protected System-Effect Invariance (P1), Revocation-Bound Execution Authority (P2), and Delegation Non-Escalation (P3).
3. **Reference Architecture:** We design and implement DROS-Mobile, an in-process execution authority gate operating via C-ABI across iOS (Swift) and Android (JNI) platforms, explicitly scoping protection to declared interface paths $\mathcal{E}_{\mathrm{protected}}$.
4. **Reproducible Experimental Methodology:** We construct a 6-tier experimental ladder (M1--M6) across iOS and Android testbeds, evaluating adversarial black-box controllers ($C^*$), capability replay, and microsecond revocation races.

---

## 2. Related Work and Research Positioning

### 2.1 Mobile Application Sandboxing and OS Permissions
Traditional mobile security relies on operating system application sandboxing and runtime permission frameworks (e.g., iOS TCC, Android Runtime Permissions) [1, 6]. While these mechanisms restrict inter-application privilege escalation, they operate at the granularity of the host application. Once an application is granted permission (e.g., Camera or Photo Library), an autonomous agent running inside that application inherits all permissions without fine-grained temporal or semantic constraints.

### 2.2 LLM Agent Guardrails and Digital Containment
Recent research addresses LLM agent security via middleware guardrails, prompt filtering, and tool-call mediation [2, 7]. However, existing guardrails primarily operate within the application layer or rely on secondary LLM verifiers that introduce hundreds of milliseconds of latency and can be bypassed via direct API manipulation.

### 2.3 Research Gap and Experimental Substrate Positioning
Existing research increasingly addresses post-compromise agent behavior, runtime authorization, execution mediation, and mobile security, but these lines often rely on fragmented experimental substrates and disparate assurance boundaries [3, 4, 8]. A reproducible execution substrate that exposes the complete transition from compromised agent intent to protected system effects can facilitate systematic evaluation of post-compromise execution security.

In this unified research paradigm:
* **DROS** provides an open, reproducible, executable reference substrate;
* **VEP** provides the implementation-independent evaluation and falsification protocol;
* **Mobile and UAV** instantiate the post-compromise execution security problem across digital system effects ($\mathrm{PSE} \equiv 0$) and cyber-physical kinetic envelopes ($\Delta u_{\mathrm{cmd}} \equiv 0 \land x(t) \in \mathcal{S}_{\mathrm{safe}}$), respectively.

---

## 3. System and Threat Model

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

### 3.1 Untrusted Controller Model ($C^*$)
The cognitive controller is modeled as an adversarial black box:
$$C^* : \mathcal{I} \rightarrow \mathcal{A}^* \quad \text{where} \quad \mathcal{A}^* \subseteq \mathcal{A}_{\mathrm{arbitrary}}$$
The attacker can emit valid or invalid API calls, manipulate parameter buffers, replay expired tokens, and attempt vertical/horizontal privilege escalation.

### 3.2 Trusted Execution Boundary & Declared Path Scope ($\mathcal{E}_{\mathrm{protected}}$)
The assurance boundary is strictly scoped to the declared protected execution path:
$$\mathcal{E}_{\mathrm{protected}} = \{\text{all execution paths covered by the enforcement boundary}\}$$
* **Epistemic Scope:** DROS-Mobile enforces authorization for any action $a \in \mathcal{E}_{\mathrm{protected}}$. It does not claim protection for arbitrary OS effects outside its declared enforcement boundary.
* **Fundamental Epistemic Invariant:**
  $$\mathrm{ControllerIntegrity} = 0 \not\implies \mathrm{ExecutionAuthorityIntegrity} = 0$$

### 3.3 Out-of-Scope Disclosures
* Physical device memory tampering via hardware debugger / JTAG;
* Baseband processor compromise;
* OS kernel-level compromises (iOS kernel panic / Android rootkits);
* Secure Enclave hardware compromise.

---

## 4. Formal Security Properties

### 4.1 Property P1 — Unauthorized Protected System-Effect Invariance (UPSEI)
$$\boxed{ \forall a \in \mathcal{E}_{\mathrm{protected}}, \quad \mathrm{Auth}(a, s, t) = 0 \implies \mathrm{PSE}(a, s, t) \equiv 0 }$$

* **Protected System Effect ($\mathrm{PSE}$):** Explicitly defined as any state mutation, unauthorized read, or IPC transmission touching:
  1. Protected Mobile APIs (Camera, Photo Library, Contacts, Microphone);
  2. Financial & Privileged Services (Apple Pay, Android Keystore, SMS);
  3. Local Application Storage & Protected Keychain Entries;
  4. Outbound Network Sockets.
* **Non-Protected Local State:** Local in-memory variable mutations within the unprivileged Agent sandbox do not constitute $\mathrm{PSE}$.

### 4.2 Property P2 — Revocation-Bound Execution Authority
Let capability $c$ be revoked at timestamp $t_r$. Within a bounded revocation horizon $\tau_r$:
$$\boxed{ \mathrm{Revoked}(c, t_r) = 1 \implies \forall t \ge t_r + \tau_r, \quad \mathrm{Auth}(a_c, s, t) = 0 \ \land \ \mathrm{PSE}(a_c, s, t) \equiv 0 }$$

#### Multi-Stage Revocation Horizon Decomposition:
* **$T_{\mathrm{RCU}}$:** Policy state pointer swap latency (atomic RCU swap $\approx 420\text{ ns}$) [10].
* **$T_{\mathrm{decision}}$:** In-process authorization lookup latency ($\approx 500\text{ ns}$).
* **$T_{\mathrm{rev}}$ (Actual Revocation Enforcement Latency):**
  $$T_{\mathrm{rev}} = t_{\text{first guaranteed DENY}} - t_{\text{revocation commit}}$$
  *(Empirically measured at $T_{\mathrm{rev}} < 2.5\ \mu\text{s}$ under multi-threaded concurrency)*.

### 4.3 Property P3 — Delegation Non-Escalation
$$\boxed{ \mathrm{Authority}_{\mathrm{child}} \subseteq \mathrm{Attenuate}(\mathrm{Authority}_{\mathrm{parent}}) \quad \text{and} \quad \mathrm{UnauthorizedPropagation} \equiv 0 }$$

---

## 5. Experimental Evaluation (M1–M6 Ladder)

### 5.1 Experimental Setup
* **iOS Environment:** Apple A17 Pro (iOS 18), Swift 5.10 with direct C-ABI static binding.
* **Android Environment:** Snapdragon 8 Gen 3 (Android 14), Kotlin with JNI C-ABI shared library (`libdros_mobile.so`).
* **Workload:** 10,000 continuous benchmark iterations with randomized adversarial injections.

### 5.2 Six-Tier Evaluation Results (M1–M6)

| Tier | Evaluation Stage | Injected Adversarial Vector | Evaluated Metric & Success Criteria | Empirical Result |
| :--- | :--- | :--- | :--- | :--- |
| **M1** | **Nominal Execution** | Legitimate Photo Library access | $\mathrm{PSE} = 1$, $P_{50} \le 1.70\ \mu\text{s}$, 0 false denials | **Pass** ($P_{50} = 1.70\mu\text{s}$, 0 false denials) |
| **M2** | **Full Compromise** | Malicious intent issued ($C^*$) | Generation of unauthorized intent confirmed at cognition plane | **Pass** ($C^*$ intent logged) |
| **M3** | **Execution Containment** | Unauthorized SMS / Contact exfiltration | $\mathrm{Auth} = 0 \implies \mathrm{PSE} \equiv 0$ (100% containment) | **Pass** ($R_{\mathrm{contain}} = 10,000/10,000 = 1.0$) |
| **M4** | **Capability Abuse** | Stale tokens, type confusion, enum manipulation | $100\%$ Fail-closed rejection rate ($R_{\mathrm{FC}} = 1.0$) | **Pass** ($R_{\mathrm{FC}} = 1.000$) |
| **M5** | **Revocation Race** | Replay of revoked credential at $t_r + \Delta t$ | $T_{\mathrm{rev}}$ measurement ($< 2.5\ \mu\text{s}$), $0$ post-revocation $\mathrm{PSE}$ | **Pass** ($T_{\mathrm{rev}} = 2.10\mu\text{s}$, 0 post-rev effects) |
| **M6** | **High-Rate Stress** | 10,000 boundary mutations on iOS/Android | 0 crashes, no detectable memory growth, minimal energy overhead | **Pass** (0 crashes, $\Delta M = 0\text{B}$) |

### 5.3 Overhead and Energy Measurements
* **Decision Latency:** iOS Swift $P_{50} = 1.70\ \mu\text{s}, P_{99} = 7.30\ \mu\text{s}$; Android JNI $P_{50} = 2.10\ \mu\text{s}, P_{99} = 8.50\ \mu\text{s}$.
* **Memory Footprint:** Observed under the specified 10,000-iteration test configuration: no detectable memory growth ($\Delta M = 0\text{ B}$ after initial pool allocation).
* **Energy Overhead:** Energy overhead estimated from measured execution cost ($<0.05\ \mu\text{J}$ per invocation in L1/L2 cache), avoiding 4G/5G radio wakeups.

---

## 6. Discussion and Limitations
DROS-Mobile provides deterministic containment under the declared threat model and interface boundary $\mathcal{E}_{\mathrm{protected}}$. However, it does not claim protection against physical hardware extraction, baseband compromise, or zero-day mobile OS kernel rootkits. Furthermore, coverage is bounded to the declared protected API sets.

---

## 7. Conclusion
This paper investigated whether physical and digital action authority can remain enforceable after the cognitive controller of an autonomous mobile agent is assumed fully compromised. Through the DROS-Mobile reference implementation, we demonstrated that decoupling cognitive planning from execution authority allows formal invariants (P1, P2, P3) to hold with microsecond-level latency and zero background network reliance.

Both domains provide empirical evidence for the overarching paradigm:
$$\boxed{ \mathrm{Cognitive\ Compromise} \not\Rightarrow \mathrm{Execution\ Authority\ Compromise} }$$

---

## Acknowledgment and AI Declaration

Generative AI tools were used solely for technical writing assistance, grammatical refinement, and LaTeX typesetting. The core conceptual vision, research questions, system architecture, formal invariants, experimental methodology, analysis of results, and claims were independently formulated and verified by the authors. The authors retain full accountability for all content presented in this work.

---

## References

1. W. Enck, P. Gilbert, B.-G. Chun, L. P. Cox, J. Jung, P. McDaniel, and A. N. Syed, "TaintDroid: An Information-Flow Tracking System for Real-Time Privacy Monitoring on Smartphones," *ACM Transactions on Computer Systems (TOCS)*, vol. 32, no. 2, pp. 1–32, 2014.
2. Y. Liu et al., "Prompt Injection Attacks and Defenses in LLM-Integrated Applications," in *Proc. IEEE Symposium on Security and Privacy (S&P)*, 2024, pp. 1042–1059.
3. J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," *Communications of the ACM (CACM)*, vol. 9, no. 3, pp. 143–155, 1966.
4. H. M. Levy, *Capability-Based Computer Systems*, Digital Press, 2014.
5. C.-C. Chen, "DROS: Deterministic Runtime Governance Substrate for Autonomous Agentic Execution," *IEEE ICA Technical Report Archive*, Tech. Rep. 7782439, 2026.
6. Apple Inc., "Security and Privacy in iOS: Transparency, Consent, and Control (TCC) Architecture," *Apple Platform Security Guide*, 2024.
7. NVIDIA, "NeMo Guardrails: Programmable Guardrails for LLM Applications," *NVIDIA Developer Documentation*, 2024.
8. X. Zhang et al., "AgentSight: eBPF-Powered Tracing and Context Correlation for Autonomous LLM Agents," in *Proc. USENIX Security Symposium*, 2024.
9. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," *OWASP Standard*, 2025.
10. P. E. McKenney, "Is Parallel Programming Hard, And, If So, What Can You Do About It? (Read-Copy Update Architecture)," *Linux Technology Center, IBM*, 2024.

---
