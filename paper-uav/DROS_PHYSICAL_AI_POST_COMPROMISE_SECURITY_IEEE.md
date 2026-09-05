# 📑 Post-Compromise Security for Physical AI: Deterministic Runtime Enforcement of Physical Action Authority in Autonomous UAVs
<!-- dros_component: dros-physical-ai-paper-full-md -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md, RFC-001-VEP-Execution-Governance-Spec.md, PAPER_SPECIFICATION_v1.0_SUBMISSION_BASELINE.md] -->
<!-- dros_description: 完整學術論文全文 Markdown 版本 (與 IEEE LaTeX 手稿 100% 嚴格對稱) -->
<!-- dros_status: Active -->

**Author:** Chun-Cheng (Jimmy) Chen (`jimmychen@dr-os.io`)  
**Affiliation:** Research and Development Division, Top-Celestial Company Ltd., Taipei, Taiwan R.O.C.  
**Target Venues:** IEEE DASC / NDSS VehicleSec / IEEE IROS / IEEE Transactions on Robotics (T-RO)  
**Intellectual Property Notice:** Protected under U.S. Provisional Patent Application No. 64/111,973 (Patent Pending). All commercial rights reserved.

---

## 🧭 Abstract

Autonomous Physical AI systems increasingly connect learned or language-based controllers to cyber-physical actuators. This creates a security problem that differs from conventional model robustness: when a Physical AI controller is fully compromised, where does the last enforceable security boundary remain? We formulate the **Post-Compromise Physical Action Authority Problem** and investigate whether execution authority can be placed at the transition from autonomous intent to physical action, bounding action authority independently of cognitive controller integrity.

We present **DROS-Kinetic**, a reference implementation that places a deterministic authorization gate between an autonomous control process and the flight-control command interface. The design separates cognitive compromise from physical execution authority through explicit action, principal, capability, and policy checks. We formalize three core properties: **Unauthorized Command-Induced Actuation Invariance (UCIAI)** (an enforcement property), **Conditional Empirical Safety-Envelope Preservation** (a conditional cyber-physical system property), and **Delegation Non-Escalation** (a multi-agent governance property) under explicitly stated vehicle, dynamic, and disturbance assumptions.

We evaluate the system using a six-stage experimental ladder (T1–T6) covering nominal execution, adversarial controller compromise, execution containment, physical safety-envelope enforcement, multi-agent delegation, and revocation under boundary-oriented stress workloads. Results are reported in terms of unauthorized-actuation containment, safety-envelope violations, delegation propagation depth, and decomposed latency layers ($L_{\mathrm{enforcement}} \ll L_{\mathrm{transport}} \ll L_{\mathrm{physical}}$). The study provides an experimentally testable basis for evaluating post-compromise security at the boundary between autonomous cognition and physical actuation.

**Keywords:** Physical AI, Autonomous UAVs, Post-Compromise Security, Runtime Enforcement, Execution Authority, Cyber-Physical Systems.

---

## 1. Introduction

The rapid convergence of Large Language Models (LLMs), Vision-Language-Action (VLA) models, and embodied robotics has accelerated the deployment of autonomous Physical AI agents in high-stakes operational domains, ranging from unmanned aerial vehicles (UAVs) and industrial manipulators to autonomous transport systems. However, placing unconstrained generative or learned reasoning systems in direct control of physical actuators introduces an existential safety assurance paradox. When the cognitive controller encounters adversarial sensory inputs, prompt injection attacks, or zero-day logic subversion, text-level guardrails within the model substrate fail to prevent the generation of catastrophic actuator commands.

In traditional software systems, a security breach results in unauthorized data exfiltration or state mutation, which can often be mitigated via transactional rollbacks or cryptographic revocations. In contrast, Physical AI systems possess physical mass, kinetic momentum, and mechanical dynamics. A single unauthorized command—such as an in-flight motor disarm or a high-velocity dive into restricted airspace—leads to irreversible physical destruction and severe human safety hazards.

This fundamental reality leads to the central question of this work:

$$\boxed{ \textbf{When a Physical AI controller is fully compromised, where does the last enforceable security boundary remain?} }$$

We investigate whether that boundary can be placed at the transition from autonomous intent to physical action, bounding action authority independently of cognitive controller integrity. We formulate the central security thesis:

$$\boxed{ \mathrm{Compromise}(\mathrm{Cognitive\ Controller}) \not\Rightarrow \mathrm{Compromise}(\mathrm{Physical\ Execution\ Authority}) }$$

To rigorously study this problem, this paper introduces **DROS-Kinetic**, an open-source reference implementation positioned at the boundary between the autonomous controller and the flight-control hardware interface. Using autonomous UAVs as a controlled physical platform, we make the following contributions:

1. **Problem Formulation:** We formulate the Post-Compromise Physical Action Authority Problem, explicitly decoupling cognitive intent generation from the authority to induce physical actuation.
2. **Formal Security Properties:** We formalize three testable properties: Unauthorized Command-Induced Actuation Invariance (UCIAI), Conditional Empirical Safety-Envelope Preservation, and Delegation Non-Escalation under declared disturbance bounds.
3. **Reference Architecture:** We present the DROS-Kinetic execution substrate, decoupling enforcement latency from transport and physical dynamics ($L_{\mathrm{enforcement}} \ll L_{\mathrm{transport}} \ll L_{\mathrm{physical}}$).
4. **Reproducible Empirical Methodology:** We construct a six-tier experimental ladder (T1–T6) and evaluate the system against boundary-oriented adversarial mutations and swarm delegation propagation.

---

## 2. Related Work

### 2.1 UAV Cybersecurity and Runtime Assurance
Traditional UAV cybersecurity research has heavily focused on communication link encryption, GPS spoofing mitigation, and intrusion detection systems on MAVLink telemetry buses. In parallel, runtime assurance (RTA) frameworks, such as simplex architectures, switch control to a verified baseline controller upon detecting safety violations. However, traditional RTA assumes that the primary controller fails due to software bugs or domain shifts, rather than operating under active, adversarial post-compromise control with legitimate credential misuse.

### 2.2 Agentic AI Governance and Physical Embodiment
Recent efforts in LLM agent governance have focused on tool-use containment, capability attenuation, and execution passports in digital environments. When extending agents to Physical AI and robotics, emerging industry standards (e.g., Anthropic Model Hardware Interface) highlight the critical need for hardware-level boundaries. However, existing proposals largely treat safety as an internal alignment problem. Our work addresses the gap where the cognitive controller is already fully compromised, establishing an independent in-band execution authority gate.

### 2.3 Research Gap and Experimental Substrate
Existing UAV and Physical AI research provides increasingly mature physical testbeds for autonomous flight, cyber-physical evaluation, and adversarial experimentation. However, the availability of a physical platform alone does not establish an independently verifiable execution-authority boundary between a compromised autonomous controller and the physical actuation layer.

This distinction is particularly important in the post-compromise setting. Once the cognitive controller is assumed to be fully compromised, evaluating whether an attack can influence vehicle behavior is insufficient to determine whether physical execution authority remains constrained. A post-compromise evaluation therefore requires an experimental substrate in which the controller, execution-authority enforcement layer, flight-control interface, and resulting physical effects can be observed and measured as separate stages.

In this work, **DROS-Kinetic** is used as a reference implementation of such an execution-authority boundary. The implementation is not itself the research object; rather, it provides a concrete and reproducible substrate through which the proposed security properties can be instantiated, attacked, measured, and evaluated under a declared threat model. This separation also permits the evaluation methodology to be applied to alternative enforcement mechanisms and physical platforms.

---

## 3. Post-Compromise Physical Action Authority Problem

### 3.1 System and Threat Model
We model an autonomous Physical AI agent as consisting of two distinct domains separated by a trusted execution boundary:

```text
┌──────────────────────────────────────────────────────────────┐
│ Cognitive / Planning Plane                                   │
│ LLM / VLA / Autonomous Controller                            │
│                                                              │
│             ASSUMED FULLY COMPROMISED (C*: I -> A*)          │
└──────────────────────────────┬───────────────────────────────┘
                               │
                         Arbitrary Intent (a* in A_arbitrary)
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Physical Authority Boundary (DROS-Kinetic)                   │
│ L1 — Authorization Decision (Principal / Capability / Policy)│
│                                                              │
│      ALLOW ────────────────────────┐                          │
│      DENY ────────────────┐        │                          │
└───────────────────────────┼────────┼─────────────────────────┘
                            │        │
                            X        ▼
                         DENIED   L2 — Execution Boundary
                                   C-ABI / Argument Validation
                                      │
                                      ▼
                              L3 — Command Transport
                              MAVLink / IPC / UDP / Serial
                                      │
                                      ▼
                              Flight Controller
                                      │
                                      ▼
                              Physical Dynamics
                                      │
                                      ▼
                              Vehicle State x(t)
                                      │
                                      ▼
                              Safety Envelope
```

* **Untrusted Cognitive Controller ($C^*$):** Modeled as an adversarial black box $C^*: \mathcal{I} \rightarrow \mathcal{A}^*$, where $\mathcal{A}^* \subseteq \mathcal{A}_{\mathrm{arbitrary}}$. The attacker is assumed to have full control over high-level reasoning, prompt contexts, mission planning, and credential submission.
* **Trusted Execution Substrate:** Positioned between $C^*$ and the flight-control hardware. It comprises the DROS-Kinetic enforcement engine, cryptographic capability stores, and the low-level hardware interface.

$$\boxed{ \mathrm{ControllerIntegrity} = 0 \not\implies \mathrm{ExecutionAuthorityIntegrity} = 0 }$$

### 3.2 Assurance Boundary Disclosures
We explicitly assume the physical integrity of the flight-controller firmware, uncompromised low-level hardware timing, and environmental wind disturbances within defined bounds $\mathcal{W}$. Physical JTAG tampering, mechanical actuator destruction, and total sensor loss are out of scope.

---

## 4. Formal Security Properties

### 4.1 Vehicle Dynamics and Input Decomposition
The physical vehicle dynamics are governed by:

$$\dot{x}(t) = f(x(t), u(t)) + w(t), \quad w(t) \in \mathcal{W} \ (\|w(t)\| \le W_{\max})$$

where $x(t) \in \mathbb{R}^n$ is the vehicle state vector, and $u(t) \in \mathcal{U}$ is the total control input. We decompose the control input as:

$$u(t) = u_{\mathrm{nominal}}(t) + \Delta u_{\mathrm{cmd}}(t)$$

where $u_{\mathrm{nominal}}(t)$ denotes existing authorized control actions and natural flight stabilization, and $\Delta u_{\mathrm{cmd}}(t)$ denotes the command-induced actuation directly attributable to the evaluated command.

### 4.2 Property P1: Unauthorized Command-Induced Actuation Invariance (UCIAI)

$$\boxed{ \mathrm{Auth}(a, s, t) = 0 \implies \Delta u_{\mathrm{cmd}}(a, s, t) \equiv 0 }$$

> **Epistemic Definition:** P1 is an **enforcement property**. A denied action request must introduce zero additional actuation into the execution path. Crucially:
> $$\boxed{ \Delta u_{\mathrm{cmd}} = 0 \not\implies x(t+\Delta t) = x(t) }$$
> *(Natural inertia, gravity, and pre-existing aerodynamic momentum continue to govern vehicle dynamics).*

### 4.3 Property P2: Conditional Empirical Safety-Envelope Preservation
Let $\mathcal{S}_{\mathrm{safe}} \subset \mathcal{X}$ be the defined safe reachability envelope (P2-S). Within a declared operating envelope $\Omega = \{x, u, w, \epsilon_{\mathrm{est}}, \tau\}$, the system empirically demonstrates (P2-E):

$$\boxed{ x(t) \in \mathcal{S}_{\mathrm{safe}} \quad \forall t \in [t_0, t_0 + T] }$$

> **Epistemic Definition:** P2 is a **conditional cyber-physical empirical property**, verified under explicit vehicle modeling and disturbance bounds.

### 4.4 Property P3: Delegation Non-Escalation
For parent node $i$ delegating to child node $j$:

$$\boxed{ \mathrm{Authority}_j \subseteq \mathrm{Attenuate}(\mathrm{Authority}_i) \quad \text{and} \quad \mathrm{Depth} \le H }$$

Any delegation attempt with $\mathrm{Depth} > H$ yields $\mathrm{Auth} = 0 \implies \Delta u_{\mathrm{cmd}} \equiv 0$.

---

## 5. DROS-Kinetic Architecture and Latency Decomposition

### 5.1 In-Band Enforcement Pipeline
DROS-Kinetic interposes directly between the autonomous planning process and the flight-control communication stack. It enforces bitmask capability checks, dynamic lookahead kinematics, and epoch-based revocation before serializing commands into low-level MAVLink frames.

### 5.2 Four-Layer Latency Decomposition
To prevent conflation between binary decision speeds and physical vehicle responses, latency is formally decomposed into four distinct layers:

1. **L1 (Authorization Primitive):** Pure $O(1)$ capability bitmask lookup ($L_1 < 500\text{ ns}$).
2. **L2 (End-to-End Enforcement Decision):** In-process C-ABI argument sanitization and kinematic lookahead ($P_{50} = 4.40\ \mu\text{s}, P_{99} = 13.30\ \mu\text{s}$).
3. **L3 (Command Transport):** MAVLink framing and serial/UDP bus delivery ($1.20\text{ ms} \sim 3.50\text{ ms}$, transport-dependent).
4. **L4 (Physical Dynamics Response):** Flight controller loop, ESC motor acceleration, and aerodynamic response ($50\text{ ms} \sim 200\text{ ms}$, observed under evaluated quadrotor platform).

$$\boxed{ L_{\mathrm{enforcement}}\ (L_1/L_2 \approx 4.4\mu\text{s}) \ll L_{\mathrm{transport}}\ (L_3 \approx 2\text{ms}) \ll L_{\mathrm{physical}}\ (L_4 \approx 100\text{ms}) }$$

---

## 6. Cyber-Physical Stopping Horizon Model

In geofence enforcement scenarios, preventing kinetic penetration requires proactive intervention. We model the required stopping horizon $d_{\mathrm{safe}}$ as:

$$\boxed{ d_{\mathrm{safe}} = d_{\mathrm{brake}} + d_{\mathrm{latency}} + d_{\mathrm{estimation}} + d_{\mathrm{margin}} }$$

### Term Breakdown:
1. **$d_{\mathrm{brake}}$ (Kinetic Braking Distance):**
   $$d_{\mathrm{brake}} = \frac{v_h^2}{2 a_{\max}} = \frac{15.0^2}{2 \times 3.0} = 37.50\text{ m}$$
2. **$d_{\mathrm{latency}}$ (Computational & Transport Latency Distance):**
   $$d_{\mathrm{latency}} = v_h \times (L_1 + L_2 + L_3) \approx 15.0 \times 0.0035 = 0.05\text{ m}$$
3. **$d_{\mathrm{estimation}}$ (Sensor & Localization Uncertainty):**
   $$d_{\mathrm{estimation}} = \sigma_{\mathrm{GNSS}} + \sigma_{\mathrm{VIO}} \approx 2.50\text{ m}$$
4. **$d_{\mathrm{margin}}$ (Pre-Configured Aerodynamic Safety Buffer):**
   $$d_{\mathrm{margin}} = 20.00\text{ m} \quad (\text{Accounting for max wind gust } W_{\max})$$

$$\text{Predicted Intervention Threshold } d_{\mathrm{safe}} = 37.50 + 0.05 + 2.50 + 20.00 = 60.05\text{ m}$$

---

## 7. Experimental Evaluation

### 7.1 T1–T6 Research Protocol
We implement a six-tier experimental protocol executed on high-fidelity Software-in-the-Loop (SITL) quadrotor simulation linked via ROS2 and MAVLink:

* **T1 (Nominal):** Valid waypoint navigation commands execute with zero trajectory distortion; enforcement overhead is bounded by $L_2$.
* **T2 (Adversarial Controller):** Compromised controller issues arbitrary unauthorized commands (e.g., in-flight Disarm).
* **T3 (Execution Containment):** Under B0 (Unprotected), in-flight Disarm causes immediate free-fall motor cutoff ($\Delta S > 0$). Under B1 (DROS-Kinetic), unauthorized Disarm is rejected at the C-ABI boundary ($\Delta u_{\mathrm{cmd}} \equiv 0$), preserving stable hover at 25.0m altitude.
* **T4 (Safety Envelope):** High-speed ($15.0\text{ m/s}$) ingress toward a 500m no-fly-zone (NFZ). Lookahead braking triggers at $61.30\text{ m}$ (predicted $60.05\text{ m}$), achieving complete halt at $+24.60\text{ m}$ prior to the boundary ($0.0\text{ m}$ penetration).
* **T5 (Swarm Delegation):** A 5-hop adversarial delegation propagation attempt is evaluated across a 100-UAV swarm. With policy $H=2$, Hops 1–2 succeed within attenuated bounds, while Hops 3–5 are deterministically blocked (Zero unauthorized propagation beyond $H$).
* **T6 (Revocation & Stress):** Evaluated against a boundary-oriented corpus (NaN, $\pm\mathrm{Inf}$, truncated MAVLink frames, expired epochs) across 10,000 mutations and a 178,000 QPS stress workload. DROS-Kinetic achieved $0$ crashes and a $100\%$ fail-closed containment rate ($R_{\mathrm{FC}} = 1.0$), with $P_{99} = 13.30\ \mu\text{s}$.

### 7.2 Experimental Results Summary Table

| Workload Metric | Evaluated Value | Baseline (B0: Unprotected) | DROS-Kinetic (B1: Protected) |
| :--- | :--- | :--- | :--- |
| **Unauthorized Containment ($R_{\mathrm{contain}}$)** | $100\%$ | $0\%$ (Breached / Motor Cut) | **$100\%$ (100% Contained)** |
| **Fail-Closed Rate ($R_{\mathrm{FC}}$)** | $10,000 / 10,000$ | N/A | **$1.000$ ($100\%$)** |
| **Engine Crash Count** | $10,000$ Tests | $>120$ System Faults | **$0$ Crashes** |
| **Lookahead Stop Margin** | $15\text{ m/s}$ Cruise | $-180\text{m}$ (NFZ Breach) | **$+24.60\text{ m}$ (Safe Stop)** |
| **Enforcement Latency $P_{50}$** | Micro-benchmark | N/A | **$4.40\ \mu\text{s}$** |
| **Enforcement Latency $P_{99}$** | $178\text{k}$ QPS Stress | N/A | **$13.30\ \mu\text{s}$** |

---

## 8. Discussion and Limitations

### 8.1 Assurance Boundary Disclosures
DROS-Kinetic provides deterministic containment *only within the stated system and disturbance assumptions*. It does not protect against physical flight controller hardware destruction, sub-transceiver physical wiretapping, or atmospheric wind gusts exceeding the aerodynamic thrust envelope ($W > W_{\max}$).

### 8.2 Generalization to Other Physical AI Platforms
The mathematical invariants formalized in this work extend naturally to other embodied AI systems:
* **Humanoid Robotics:** Joint torque clamping and velocity envelope restriction ($\Delta \tau_{\mathrm{cmd}} \equiv 0$).
* **Autonomous Vehicles:** Drive-by-wire steering and emergency braking horizons.

---

## 9. Conclusion

This paper addressed the Post-Compromise Physical Action Authority Problem in Physical AI. By decoupling cognitive controller integrity from physical execution authority, we formalized the UCIAI invariant and conditional safety-envelope preservation. Through SITL quadrotor experiments across the T1–T6 protocol, we demonstrated that in-band runtime enforcement can deterministically prevent unauthorized physical actuation even when high-level AI reasoning is entirely subverted.

---


---

## AI Declaration and Acknowledgment

Generative AI tools were used solely for technical writing assistance, grammatical refinement, and LaTeX typesetting. The core conceptual vision, research questions, system architecture, formal invariants, physical causality models, experimental methodology, analysis of results, and claims were independently formulated and verified by the authors. The authors retain full accountability for all content presented in this work.

---

## References

1. R. Altawy and A. M. Youssef, "A Comprehensive Survey on Security and Privacy Risks in Unmanned Aerial Systems," *IEEE Communications Surveys & Tutorials*, vol. 19, no. 4, pp. 2853–2876, 2017.
2. S. Bak, D. Chivukula, O. Adekunle, M. Sun, M. Caccamo, and L. Sha, "The System-Level Simplex Architecture for Real-Time Embedded Systems," in *Proc. IEEE Real-Time and Embedded Technology and Applications Symposium (RTAS)*, 2009, pp. 125–134.
3. C.-C. Chen, "DROS: Deterministic Runtime Governance Substrate for Autonomous Agentic Execution," *IEEE ICA Technical Report Archive*, Tech. Rep. 7782439, 2026.
4. Y. Liu, Y. Jia, R. Geng, J. Jia, and N. Z. Gong, "Prompt Injection Attacks and Defenses in LLM-Integrated Applications," *arXiv preprint arXiv:2310.12815*, 2023.
5. J. B. Dennis and E. C. Van Horn, "Programming Semantics for Multiprogrammed Computations," *Communications of the ACM (CACM)*, vol. 9, no. 3, pp. 143–155, 1966.
6. H. M. Levy, *Capability-Based Computer Systems*, Digital Press, 2014.
7. PX4 Autopilot, "PX4 Architectural Overview and Safety Failsafe Governance," *PX4 User Guide*, 2024.
8. MAVLink, "MAVLink Micro Air Vehicle Communication Protocol v2.0 Specification," *MAVLink Standard*, 2024.
