# 🏛️ DROS Research Trajectory Reading Guide (Unified Overview)
## An Agent Runtime Operation Substrate across Digital and Physical Domains

**Author:** Jimmy Chen  
**Affiliation:** Top-Celestial Company Ltd.  
**Type:** Technical Note / Research Trajectory Guide  
**Deposit Nature Disclosure:** All Zenodo identifiers referenced herein represent **archived technical reports / preprints** to establish public timestamps and prior-art defense, rather than peer-reviewed journal/conference camera-ready accepted papers.  
**Permanent Zenodo v2 Record:** [https://zenodo.org/records/22255275](https://zenodo.org/records/22255275) (DOI: `10.5281/zenodo.22255275`)

---

> [!IMPORTANT]
> **Epistemic Status & Research-Program Hypothesis**:  
> The research trajectory formalized in this work is formulated as a **research-program hypothesis**, evolving continually through empirical falsification and independent counterexamples.  
> **Claim Boundary**: This series **does not claim** internal model non-compromise (statistical robustness). Rather, it investigates whether, within declared enforcement boundaries and under explicit system assumptions, unauthorized downstream physical and system effects can be deterministically constrained to zero.

---

### 1. Purpose and The "6 Papers + 1 Research Vessel" Trajectory

The DROS research trajectory expands a singular, foundational scientific question across six progressive scales of execution governance, supported by an open, reproducible evaluation vessel (**DROS-VEP Lite**):

$$\boxed{ \text{Governance} \longrightarrow \text{Authority} \longrightarrow \text{Runtime} \longrightarrow \text{Agentic Web} \longrightarrow \text{Digital Effect} \longrightarrow \text{Physical Effect} }$$

```text
                                 [ 🚢 DROS-VEP Lite Research Vessel ]
                (RFC-001 Open Protocol • Reproducible Benchmarks • Multi-Domain Sandbox)
                                                 │
          ┌──────────────────────────────────────┼──────────────────────────────────────┐
          ↓                                      ↓                                      ↓
   [ 🏹 1. Governance Spec ]             [ 🏹 2. Runtime Execution ]            [ 🏹 3. Kernel Control ]
        DROS-6P                              DROS 4-Layer                            DROS-PGM
   (6P Enterprise Trust)                (Forensic Merkle Audit)                (C-ABI Binary Gate)
          │                                      │                                      │
          └──────────────────────────────────────┴──────────────────────────────────────┘
                                                 │
                         ┌──────────────────────┼──────────────────────┐
                         ↓                      ↓                      ↓
              [ 🏹 4. Agentic Web & MCP ]  [ 🏹 5. Digital Substrate ]    [ 🏹 6. Physical Substrate ]
                     DROS-WebMCP          Post-Compromise Mobile         Post-Compromise UAV
             (Web Capability Closure)    (Mobile OS/API Action Guard)   (Kinetic Envelope Preserved)
```

---

### 2. The Core Technical Papers & Evaluation Vessel Matrix

| Component | Title / Topic | Role in Research Trajectory | Core Question / Functional Scope | Reference / DOI (Preprints / Code) |
| :---: | :--- | :--- | :--- | :--- |
| 🚢 **Vessel** | **DROS-VEP Lite** | **Evaluation Protocol & Testbed** | **How to provide an objective, falsifiable evaluation testbed?** | [GitHub Official Repo](https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite) |
| 🏹 **1** | **DROS-6P** | Governance Model | **Who has authority? Why? When does it expire?** (Enterprise Trust) | DOI: `10.5281/zenodo.21833970` |
| 🏹 **2** | **DROS 4-Layer** | Runtime Architecture | **How does policy deterministically reach execution?** (Attribution & Merkle) | DOI: `10.5281/zenodo.22092008` |
| 🏹 **3** | **DROS-PGM** | Kernel-Level Control | **Once compromised, can the execution control plane still block action?** | DOI: `10.5281/zenodo.21903687` |
| 🏹 **4** | **DROS-WebMCP** | **Agentic Web & Capability** | **How to enforce authorization and non-repudiation over WebMCP capability exposure?** | **DOI: `10.5281/zenodo.22290238`** |
| 🏹 **5** | **Post-Compromise Mobile** | Digital Substrate | **Does execution authority hold across Mobile OS/APIs?** | DOI: `10.5281/zenodo.22253147` |
| 🏹 **6** | **Post-Compromise UAV** | Cyber-Physical Substrate | **When actions cause physical motion, can the kinetic envelope hold?** | DOI: `10.5281/zenodo.22254372` |
| 🌟 **Semantic 1** | **Constraint-as-Code** | **Foundational Paradigm & Circuit Breaker** | **How to translate doctrinal classification into verifiable hard contracts with CPU thread panic?** | DOI: [`10.5281/zenodo.20823227`](https://doi.org/10.5281/zenodo.20823227) |
| 🌟 **Semantic 2** | **DROS v7.3 (DOR Framework)** | **Semantic Layer & Hallucination Control** | **How to deterministically constrain semantic drift and hallucinations in high-precision domains?** | DOI: [`10.5281/zenodo.20776075`](https://doi.org/10.5281/zenodo.20776075)<br>Repo: [Dharma-Reasoning-OS](https://github.com/Top-Celestial-Company-Ltd/Dharma-Reasoning-Operating-System) |
| 🛡️ **Foundational 1** | **Runtime Attribution Framework** | **Attribution & Execution Identity Archetype** | **How to resolve context-blindness in MAS and establish cryptographic non-repudiation?** | DOI: [`10.5281/zenodo.20823163`](https://doi.org/10.5281/zenodo.20823163) |
| 🛡️ **Foundational 2** | **VajraAgent & VajraClaw** | **Dual-Isolation Empirical Archetype** | **Can binary FFI circuit breaking neutralize sophisticated prompt injections bypassing semantic layers?** | DOI: [`10.5281/zenodo.20823189`](https://doi.org/10.5281/zenodo.20823189) |

---

> [!NOTE]
> **Dual-Track Governance Architecture (Semantic vs. Execution)**:  
> * **Semantic & Epistemic Track (Constraint-as-Code & DOR)**: Governs internal *cognitive content*—translating doctrinal classification into Vajra Contracts, flat-file document decoupling, manifestation isolation, and hallucination containment for domain-restricted knowledge systems.  
> * **Execution & Enforcement Track (6P to UAV)**: Governs downstream *external effects*—binary gates, capability bitmaps, and post-compromise physical envelope invariants.

### 3. The Overarching Research Thesis

$$\boxed{ \mathrm{Compromise}(\mathrm{Cognitive\ Controller}) \not\Rightarrow \mathrm{Compromise}(\mathrm{Downstream\ Execution\ Authority}) }$$

> **"A compromise of the autonomous cognitive controller does not inherently entail a compromise of downstream execution authority."**  
> Rather than relying exclusively on internal statistical alignment of generative models, the DROS research trajectory investigates the formal decoupling of cognitive intent from actual execution, establishing verifiable deterministic execution gates within declared enforcement boundaries that cannot be arbitrarily subverted by untrusted cognitive planes.

---

### 4. Substrate vs. Protocol Positioning (The VEP Vessel)

This series formalizes the research problem as an **executable, attackable, and measurable experimental substrate problem**:

1. **VEP Research Vessel (Evaluation Protocol)**:
   * Formalizes vendor-neutral **RFC-001 Execution Governance Evaluation Standards**.
   * Provides reproducible multi-architecture comparative baselines, 72-hour soak tests, and an open falsification channel.
2. **DROS Runtime (Reference Substrate)**:
   * Operates as a concrete, deterministic binary reference implementation under the VEP specification.
3. **Dual-Domain Instantiations (Digital & Physical)**:
   * **Mobile**: Evaluates Unauthorized Protected System-Effect Invariance ($\mathrm{Auth}=0 \implies \mathrm{PSE} \equiv 0$) and microsecond revocation races ($T_{\mathrm{rev}} < 2.5\mu\text{s}$).
   * **UAV**: Evaluates Unauthorized Command Invariance ($\mathrm{Auth}=0 \implies \Delta u_{\mathrm{cmd}} \equiv 0$) and physical safety-envelope preservation ($\mathcal{S}_{\mathrm{safe}}$).

---

### 5. Cross-Domain Substrate Mapping

DROS demonstrates that deterministic runtime governance applies uniformly across heterogeneous operational substrates:
* **Digital Domains (Mobile OS):** Protects privileged APIs, clipboard, storage, and sensors against unauthorized state leakage.
* **Physical Domains (Robotics & UAVs):** Enforces physical kinetic invariance, dynamic deceleration horizons, and geofence boundary containment.

---

### 6. Recommended Reading Paths

* **Architects & Decision Makers**: Start with this Guide $\to$ explore the [DROS-VEP Lite Root README](file:///E:/vscode/AI%E7%9F%A5%E8%AD%98%E5%BA%AB/dros-vep-lite/README.md).
* **Foundational Archetypes & Inception**: **Runtime Attribution Framework** $\to$ **Vajra Sandboxing** $\to$ **DROS-6P** $\to$ **DROS 4-Layer**.
* **Web & MCP Developers**: **DROS-WebMCP** (DWGR-8 & Nonce Architecture) $\to$ **DROS 4-Layer**.
* **Governance & Policy Researchers**: **DROS-6P** $\to$ **DROS 4-Layer**.
* **Security Engineers & Binary Specialists**: **VajraClaw Archetype** $\to$ **DROS-PGM** $\to$ **Post-Compromise Mobile**.
* **Robotics & Control Theorists**: **Post-Compromise UAV** (Kinematics, braking horizon, latency decoupling).

---

### 7. References & Identifiers

When referencing technical claims, cite via the official DOI or technical report identifier of these archived preprints:
1. **DROS-VEP Lite:** *Verifiable Execution Protocol & Evaluation Sandbox*, 2026.
2. **DROS-6P:** DOI: `10.5281/zenodo.21833970`
3. **DROS 4-Layer:** DOI: `10.5281/zenodo.22092008`
4. **DROS-PGM:** DOI: `10.5281/zenodo.21903687`
5. **DROS-WebMCP:** DOI: `10.5281/zenodo.22290238`
6. **DROS-Mobile:** DOI: `10.5281/zenodo.22253147`
7. **DROS-Kinetic (UAV):** DOI: `10.5281/zenodo.22254372`
8. **Constraint-as-Code (Foundational):** DOI: `10.5281/zenodo.20823227`
9. **DROS v7.3 (DOR Framework):** DOI: `10.5281/zenodo.20776075`
10. **Runtime Attribution Framework (Identity Prehistory):** DOI: `10.5281/zenodo.20823163`
11. **Neutralizing Prompt Injection (Vajra Archetype):** DOI: `10.5281/zenodo.20823189`

---

---

### 8. Research Vision & The Falsification Manifesto

> **"Build the substrate first. Let the field prove—or falsify—the claims."**  
> 
> * **We built the execution substrate.**
> * **We defined the measurable boundary.**
> * **We provide the implementation and evaluation protocol.**
> * **Now the field can reproduce, extend, challenge, and falsify it.**

The fundamental objective of the DROS research trajectory and the VEP evaluation vessel is to establish an open, measurable, and falsifiable experimental foundation. Rather than claiming unverifiable global security guarantees, we invite the global systems, robotics, mobile, and AI governance communities to independently reproduce our empirical benchmarks, explore adversarial edge cases, and challenge our formal invariants through open scientific falsification.
