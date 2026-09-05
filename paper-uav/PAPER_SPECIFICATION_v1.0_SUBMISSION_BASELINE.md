# 📑 Formal Paper Specification (v1.0 - Submission Baseline)
# 《Post-Compromise Security for Physical AI: Deterministic Runtime Enforcement of Physical Action Authority in Autonomous UAVs》
<!-- dros_component: dros-physical-ai-paper-spec-v1.0 -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md, RFC-001-VEP-Execution-Governance-Spec.md] -->
<!-- dros_description: 官方最終提交基線 Paper Specification v1.0 (8 大學術手術刀深度收斂，研究範式與 3 大形式化性質永久凍結) -->
<!-- dros_status: Active / Submission Baseline (Frozen v1.0) -->

> **Target Venues:** IEEE DASC (Digital Avionics Systems Conference) / NDSS VehicleSec / IEEE IROS / IEEE T-RO  
> **Research Object:** Post-Compromise Physical Action Authority  
> **Reference Implementation:** DROS-Kinetic  
> **Controlled Physical Platform:** Autonomous UAV (SITL / ROS2 / MAVLink)

---

## 🧭 The Two Core Research Questions

> **Primary:**  
> **When a Physical AI controller is fully compromised, where does the last enforceable security boundary remain?**

> **Secondary / Investigatory:**  
> **We investigate whether that boundary can be placed at the transition from autonomous intent to physical action, bounding action authority independently of cognitive controller integrity.**

### 🏛️ Central Security Thesis
$$\boxed{ \mathrm{Compromise}(\mathrm{Cognitive\ Controller}) \not\Rightarrow \mathrm{Compromise}(\mathrm{Physical\ Execution\ Authority}) }$$

*The paper does **not** claim that a compromised UAV can be made universally safe. Instead, it investigates whether a trusted execution layer can preserve explicitly defined authorization and safety properties under a stated threat model and operating envelope.*

---

# 1. Abstract

Autonomous Physical AI systems increasingly connect learned or language-based controllers to cyber-physical actuators. This creates a security problem that differs from conventional model robustness: when a Physical AI controller is fully compromised, where does the last enforceable security boundary remain? We formulate the **Post-Compromise Physical Action Authority Problem** and investigate whether execution authority can be placed at the transition from autonomous intent to physical action, bounding action authority independently of cognitive controller integrity.

We present **DROS-Kinetic**, a reference implementation that places a deterministic authorization gate between an autonomous control process and the flight-control command interface. The design separates cognitive compromise from physical execution authority through explicit action, principal, capability, and policy checks. We formalize three core properties: **Unauthorized Command-Induced Actuation Invariance (UCIAI)** (an enforcement property), **Conditional Empirical Safety-Envelope Preservation** (a conditional cyber-physical system property), and **Delegation Non-Escalation** (a multi-agent governance property) under explicitly stated vehicle, dynamic, and disturbance assumptions.

We evaluate the system using a six-stage experimental ladder (T1–T6) covering nominal execution, adversarial controller compromise, execution containment, physical safety-envelope enforcement, multi-agent delegation, and revocation under boundary-oriented stress workloads. Results are reported in terms of unauthorized-actuation containment, safety-envelope violations, delegation propagation depth, and decomposed latency layers ($L_{\mathrm{enforcement}} \ll L_{\mathrm{transport}} \ll L_{\mathrm{physical}}$). The study provides an experimentally testable basis for evaluating post-compromise security at the boundary between autonomous cognition and physical actuation.

---

# 2. Academic Contributions

* **C1 — Problem Formulation:**  
  We formulate the **Post-Compromise Physical Action Authority Problem** as a distinct security problem at the boundary between autonomous cognition and physical actuation, explicitly separating compromise of the cognitive controller from compromise of the authority to produce physical actions.
* **C2 — Formal System & Security Properties:**  
  We define three formally testable properties:
  1. **Unauthorized Command-Induced Actuation Invariance (UCIAI)** (*Enforcement Property*);
  2. **Conditional Empirical Safety-Envelope Preservation** (*Conditional Cyber-Physical System Property*);
  3. **Delegation Non-Escalation** (*Multi-Agent Governance Property*).
* **C3 — Reference Architecture:**  
  We design and implement **DROS-Kinetic**, a trusted runtime enforcement substrate positioned between the autonomous control process and the flight-control command interface, explicitly decoupling intent from execution authority.
* **C4 — Reproducible Evaluation Methodology:**  
  We define a six-stage experimental methodology (T1–T6) for evaluating post-compromise physical action authority and release an implementation-independent evaluation procedure compatible with the VEP framework.

---

# 3. System and Threat Model

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

## 3.1 Untrusted Controller Model ($C^*$)
The cognitive controller is modeled as an **adversarial black-box**:
$$C^* : \mathcal{I} \rightarrow \mathcal{A}^* \quad \text{where} \quad \mathcal{A}^* \subseteq \mathcal{A}_{\mathrm{arbitrary}}$$
We do not restrict the attacker to prompt injection; the controller is assumed capable of issuing *any arbitrary, syntactically valid but unauthorized action request*.

## 3.2 Trusted Boundary
* **Trusted:** DROS-Kinetic enforcement substrate, authorization state, protected execution boundary, flight-controller firmware (unless explicitly ablated), sensor/actuator interfaces.
* **Fundamental Epistemic Invariant:**
  $$\mathrm{ControllerIntegrity} = 0 \not\implies \mathrm{ExecutionAuthorityIntegrity} = 0$$

## 3.3 Out-of-Scope Compromise
Physical JTAG/SWD hardware tampering, mechanical actuator destruction, total sensor destruction, environmental conditions outside declared disturbance bounds $\mathcal{W}$.

---

# 4. Formal System Model & Dynamics Decoupling

The vehicle is modeled as:
$$\dot{x}(t) = f(x(t), u(t)) + w(t), \quad w(t) \in \mathcal{W} \ (\|w(t)\| \le W_{\max})$$

Control input is decomposed as:
$$u(t) = u_{\mathrm{nominal}}(t) + \Delta u_{\mathrm{cmd}}(t)$$
* $u_{\mathrm{nominal}}(t)$: Existing authorized control behavior and natural flight stabilization.
* $\Delta u_{\mathrm{cmd}}(t)$: Command-induced actuation attributable to the evaluated command.

---

# 5. Formal Security Properties (The Three Frozen Properties)

## 5.1 Property P1 — Unauthorized Command-Induced Actuation Invariance (UCIAI)
$$\boxed{ \mathrm{Auth}(a, s, t) = 0 \implies \Delta u_{\mathrm{cmd}}(a, s, t) \equiv 0 }$$

* **Property Type:** **Enforcement Property** (Deterministic binary boundary guarantee).
* **Crucial Clarification:**
  $$\boxed{ \text{Command Non-Execution } (\Delta u_{\mathrm{cmd}} = 0) \not\implies \text{Vehicle State Non-Change } (x_{t+1} = x_t) }$$
  *(Natural inertia, gravity, aerodynamics, and previously authorized stabilization continue to operate).*

---

## 5.2 Property P2 — Conditional Empirical Safety-Envelope Preservation

* **P2-S (Safety Specification):** $\mathcal{S}_{\mathrm{safe}} \subset \mathcal{X}$ defines the valid operational geofence and dynamic limits.
* **P2-E (Empirical Preservation):** Within the declared operating envelope $\Omega = \{x, u, w, \epsilon_{\mathrm{est}}, \tau\}$, the system empirically demonstrates:
  $$\boxed{ x(t) \in \mathcal{S}_{\mathrm{safe}} \quad \forall t \in [t_0, t_0 + T] }$$
* **Property Type:** **Conditional Cyber-Physical System Property** (*Not an unconditional physical theorem*).

---

## 5.3 Property P3 — Delegation Non-Escalation
$$\boxed{ \mathrm{Authority}_j \subseteq \mathrm{Attenuate}(\mathrm{Authority}_i) } \quad \text{and} \quad \boxed{ \mathrm{Depth} \le H }$$
$$\mathrm{Depth} > H \implies \mathrm{Auth} = 0 \implies \Delta u_{\mathrm{cmd}} \equiv 0$$

* **Property Type:** **Multi-Agent Governance Property**.
* **Precise Metric:** **Zero unauthorized delegation propagation beyond configured depth $H$.**

---

# 6. Cyber-Physical Stopping Horizon Model (T4 Formalization)

The predicted intervention threshold $d_{\mathrm{safe}}$ is explicitly formalized:

$$\boxed{ d_{\mathrm{safe}} = d_{\mathrm{brake}} + d_{\mathrm{latency}} + d_{\mathrm{estimation}} + d_{\mathrm{margin}} }$$

### Term Breakdown:
1. **$d_{\mathrm{brake}}$ (Kinetic Braking Distance):**
   $$d_{\mathrm{brake}} = \frac{v_h^2}{2 a_{\max}} = \frac{15.0^2}{2 \times 3.0} = 37.50\text{ m}$$
2. **$d_{\mathrm{latency}}$ (Computational & Transport Latency Distance):**
   $$d_{\mathrm{latency}} = v_h \times (L_1 + L_2 + L_3) \approx 15.0 \times 0.0035\text{ s} \approx 0.05\text{ m}$$
3. **$d_{\mathrm{estimation}}$ (Sensor & Localization Uncertainty):**
   $$d_{\mathrm{estimation}} = \sigma_{\mathrm{GNSS}} + \sigma_{\mathrm{VIO}} \approx 2.50\text{ m}$$
4. **$d_{\mathrm{margin}}$ (Configured Aerodynamic & Control Margin):**
   $$d_{\mathrm{margin}} = 20.00\text{ m} \quad (\text{Pre-configured experimental parameter for wind gust } W_{\max})$$

$$\text{Predicted Intervention Threshold } d_{\mathrm{safe}} \approx 37.50 + 0.05 + 2.50 + 20.00 = 60.05\text{ m}$$

* **Empirical Comparison:**
  * Predicted Intervention Threshold: $60.05\text{ m}$
  * Observed Intervention Threshold: $61.30\text{ m}$
  * Observed Final Stopping Position: $+24.60\text{ m}$ prior to boundary ($0.0\text{ m}$ boundary penetration).

---

# 7. Latency Layer Decomposition ($L_{\mathrm{enforcement}} \ll L_{\mathrm{transport}} \ll L_{\mathrm{physical}}$)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ L1 — Authorization Primitive Latency (Bitmask C-ABI)                        │
│      • Pure capability lookup: L1 < 500 ns                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ L2 — End-to-End Enforcement Decision Latency (Argument/Policy Check)         │
│      • P50 = 4.40 μs, P95 = 6.90 μs, P99 = 13.30 μs, P99.9 = 22.50 μs      │
├─────────────────────────────────────────────────────────────────────────────┤
│ L3 — Command Transport Latency (MAVLink Serial / UDP Delivery)              │
│      • Transport-dependent transmission: 1.20 ms ~ 3.50 ms                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ L4 — Physical Response Latency (Flight Controller / Motor Dynamics)         │
│      • Aerodynamic & ESC response: 50 ms ~ 200 ms                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

$$\boxed{ L_{\mathrm{enforcement}}\ (L_1/L_2 \approx 4.4\mu\text{s}) \ll L_{\mathrm{transport}}\ (L_3 \approx 2\text{ms}) \ll L_{\mathrm{physical}}\ (L_4 \approx 100\text{ms}) }$$

---

# 8. T1–T6 Experimental Protocol

| Tier | Stage | Core Question | Injected Adversarial Condition | Primary Metrics |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | **Nominal Execution** | Does authorized control execute correctly? | Valid navigation command | Authorization correctness, $L_1/L_2$ latency, trajectory deviation |
| **T2** | **Adversarial Controller** | Can arbitrary malicious intent be generated? | Arbitrary $a^* \in \mathcal{A}_{\mathrm{arbitrary}}$ | Intent generation confirmed at cognitive plane |
| **T3** | **Execution Containment** | Does unauthorized intent cross physical boundary? | Unauthorized disarm / mode change | Unauthorized actuation count ($\Delta u_{\mathrm{cmd}} = 0$) |
| **T4** | **Physical Envelope** | Can physical state remain within envelope? | 15 m/s high-speed NFZ approach | $d_{\mathrm{safe}}$ prediction vs observation, boundary penetration (0.0m) |
| **T5** | **Delegation** | Can compromised nodes amplify authority? | 5-hop attack attempt ($H=2$) | Propagation cutoff depth ($H=2$), zero unauthorized propagation |
| **T6** | **Revocation & Stress** | Does invariant hold under high-rate load? | Boundary-oriented adversarial corpus | CrashRate = 0%, FailClosedRate = 100%, $P_{99} = 13.30\ \mu\text{s}$ |

### 8.1 Boundary-Oriented Adversarial Corpus (Replacing Unrelated SQL Injections):
* NaN / $\pm\text{Inf}$ / Overflow / Underflow;
* Out-of-range negative altitudes / coordinates;
* Malformed serialization & truncated MAVLink packets;
* Capability mismatch / Stale capabilities / Expired epochs;
* Replayed commands / Type confusion / Invalid enum payloads;
* Race-condition revocation attempts.

---

# 9. Target Venue & Evidence Alignment

* **IEEE DASC / NDSS VehicleSec:** Well aligned with current SITL, HIL, decomposed latency, and boundary adversarial corpus.
* **IEEE IROS / T-RO Extension:** Target for future physical quadrotor flight trials and aerodynamic disturbance validation.

---

# 10. Complete Paper Structure (Final Submission Blueprint)

```text
01. INTRODUCTION
    • The "Last Enforceable Boundary" Problem in Physical AI
    • Cognitive Integrity != Execution Authority Integrity
    • Summary of Contributions (C1–C4)
02. RELATED WORK
    • UAV Cybersecurity & Runtime Assurance
    • LLM/VLA Agent Governance & Attribution Gaps
03. POST-COMPROMISE PHYSICAL ACTION AUTHORITY PROBLEM
    • Formal Problem Statement
    • Decoupling Cognitive Compromise from Physical Actuation
04. SYSTEM & THREAT MODEL
    • Adversarial Controller Model (C*)
    • Trusted Execution Boundary & Out-of-Scope Disclosures
05. DROS-KINETIC ARCHITECTURAL DESIGN
    • In-Band C-ABI Interception Pipeline
    • Dynamic Lookahead Watchdog & Delegation Attenuation
06. FORMAL SECURITY PROPERTIES
    • P1: Unauthorized Command-Induced Actuation Invariance (UCIAI)
    • P2: Conditional Empirical Safety-Envelope Preservation (P2-S / P2-E)
    • P3: Delegation Non-Escalation
07. CYBER-PHYSICAL SAFETY & STOPPING MODEL
    • Formal Stopping Horizon Model (d_safe = d_brake + d_lat + d_est + d_margin)
    • Predicted vs. Observed Lookahead Intervention
08. EXPERIMENTAL METHODOLOGY (T1–T6 PROTOCOL)
    • Baselines: B0 (Unprotected) vs. B1 (Protected)
    • Boundary-Oriented Adversarial Corpus
09. RESULTS & EVALUATION
    • Single-UAV Containment & Latency Decomposition
    • High-Speed NFZ Kinetic Trajectory & Swarm Delegation Cutoff
    • High-Rate Stress & Robustness Micro-benchmarks
10. DISCUSSION & EXTENSIONS
    • Generalization to Humanoids & Autonomous Vehicles
    • Aviation Standards Alignment (DO-178C, FAA Part 89)
11. LIMITATIONS & ASSURANCE BOUNDARY
    • Assumptions on Firmware, Disturbance Bounds, and SITL Fidelity
12. CONCLUSION
```

---
*DROS Formal Paper Specification v1.0 — Submission Baseline Frozen.* 🛸📐💎⚖️🛡️
