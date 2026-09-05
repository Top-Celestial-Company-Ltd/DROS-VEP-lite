# 🌐 DROS™ Official Master Technical & Commercial FAQ Hub
<!-- dros_component: dros-master-faq-hub-en -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md, DROS_SAFETY_AND_LEGAL_WARNINGS_EN.md] -->
<!-- dros_description: Official Single Source of Truth (SSOT) Master FAQ powering dr-os.io website, commercial packages, Gumroad listings, and support desks -->
<!-- dros_status: Active -->

> **Role:** Official Single Source of Truth (SSOT) Master FAQ Hub.  
> **Synchronization Targets:** Official Website (`dr-os.io/faq`), Delivery ZIP Package (`DROS_Commercial_Release_Specification_v1.0.zip`), Gumroad Storefront, Technical Support Desk.  
> **Patents & Standards:** U.S. Provisional Patent App. No. 64/111,973 · RFC-001 / RFC-010 · IEEE 6-Pillars

---

## 🧭 Table of Contents
* [1. Concept & Architectural Positioning](#1-concept--architectural-positioning)
* [2. Security & Defensive Invariants](#2-security--defensive-invariants)
* [3. Licensing & Commercial Boundaries](#3-licensing--commercial-boundaries)
* [4. Enterprise Operations & Deployment](#4-enterprise-operations--deployment)
* [5. Legal, Patents & Compliance Disclosures](#5-legal-patents--compliance-disclosures)

---

## 1. Concept & Architectural Positioning

### Q1.1 What is "Open Identity, Localized Governance"? Will external visiting agents compromise enterprise security?
**A: Absolutely not! This is DROS's core paradigm for resolving Agentic Web trust conflicts.**
* When an external agent visits carrying an RFC-010 Passport (`libdros-id`), it only presents its principal identity and issuer signature.
* **The enterprise's local GuardVM gateway retains 100% deterministic execution sovereignty**: On the VajraAgent console, administrators define local Capability Bitmaps. Even if an external passport claims root permissions, DROS in-band C-ABI evaluation (26.1 μs) restricts it strictly to authorized APIs. Any unauthorized call triggers an immediate hardware-speed termination returning HTTP 403.

### Q1.2 How does DROS's "6-Pillars Deterministic Governance" differ from traditional IAM / OAuth or API Gateways?
**A: In-band physical C-ABI enforcement vs. Out-of-band network soft boundaries.**
* **Ultra-Low Latency**: Traditional API Gateways operate at the HTTP layer (4ms~50ms). DROS-6P operates in-band at the C-ABI layer with median decision latency of **26.1 μs** (p99 = 29.8 μs).
* **Cryptographic Proofs**: Built-in SHA-256 Merkle audit chains with Ed25519 digital signatures producing court-admissible non-repudiation records.

### Q1.3 Does deploying DROS require rewriting existing Agent code (e.g., LangChain / AutoGen)?
**A: Absolutely not! Zero code refactoring, zero system downtime.**
* DROS uses transparent C-ABI in-band interception and drop-in `libdros-id` SDKs. Policies hot-reload in sub-microseconds without disrupting active workflows.

---

## 2. Security & Defensive Invariants

### Q2.1 Can DROS stop novel Zero-Day prompt injection attacks?
**A: 100% Yes.**
* DROS operates on a **Default Fail-Closed (Strict Whitelist)** model.
* Regardless of how clever the prompt injection is, any unauthorized tool call or file access is blocked instantly at the FFI boundary before touching the OS.

### Q2.2 How does DROS prevent Prompt Injection attacks aimed at exfiltrating sensitive PII?
**A: Pillar 4 Policy Gate + In-Band Dynamic PII Redaction.**
* Policy Gate dynamically redacts sensitive fields before memory persistence. For high-risk transactions, it automatically triggers Human-In-The-Loop (HITL) dual-authorization, eliminating semantic privilege escalation.

### Q2.3 Will nominal business agents be killed due to occasional LLM hallucinations?
**A: No.** DROS implements a 3-tier **Graduated Eviction State Machine**:
* **Tier 1 (Soft Deny)**: Isolated errors return a `DENY` response allowing the agent to self-correct without terminating the process.
* **Tier 2 (Quarantine)**: Sliding window violations (e.g., 3 breaches in 10s) transition the agent to a read-only sandbox.
* **Tier 3 (Hard Kill)**: Fatal escape vectors (Direct Syscalls, audit tampering, key forgery) trigger immediate `SIGKILL` termination.

### Q2.4 If an attacker attempts to overwrite the DROS microkernel binary (.dll / .so), will enforcement break?
**A: Absolutely not.** DROS enforces quadruple defensive invariants:
1. **Modification is a governed syscall**: Overwriting requires filesystem writes, which are intercepted in-band.
2. **Kernel Hard Invariants**: DROS permanently blocks writes targeting runtime binaries and private keys.
3. **OS File Locks & Signatures**: Running binaries are locked by OS kernels (Windows `FILE_SHARE_READ` / Linux `ETXTBUSY`) and validated via Ed25519 signatures.

---

## 3. Licensing & Commercial Boundaries

### Q3.1 Since the individual edition is free, what core value does the Enterprise Edition provide?
**A:** DROS maintains a strict two-tier model: "Free for Individuals, Paid for Enterprise & Swarm Governance":
1. **Free Community Edition**: Single-process in-memory governance, lightweight mock benchmarks, and basic tool interception (max 2 active roles).
2. **Paid Enterprise Edition (SKU 1--4)**:
   * **Unlimited Multi-Agent Swarms**: Cross-departmental IAM isolation preventing Confused Deputy exploits.
   * **Production-Grade SLAs & Soak Testing**: 24h/72h continuous bake testing (160k+ requests with zero memory leak), K8s DaemonSet support, and dedicated SLA support.
   * **3-Tier Graduated Eviction Engine**: Sliding window quarantine and physical `SIGKILL` eviction.
   * **Court-Admissible Forensics**: Immutable Merkle SHA-256 audit logs with EU AI Act Article 12 compliance exports.
   * **Cross-Enterprise PKI Federation**: Ed25519 / ECDSA-P256 3-tier certificate chains with hop attenuation.

### Q3.2 For on-premise air-gapped VPCs, does DROS require outbound phone-home connections?
**A: Absolutely not.** DROS enforces a strict **Zero-Phone-Home** architecture:
* All policy evaluations and cryptographic signature validations execute locally in-memory using offline public keys and compiled binary policies (`policy.bin`).

---

## 4. Enterprise Operations & Deployment

### Q4.1 How does the VajraAgent Console manage dual-direction inbound and outbound permissions?
**A: VajraAgent provides an intuitive dual-direction control interface:**
1. **Inbound API Gatekeeping**: Visually toggle Capability bitmasks to restrict external agents' access scope and enforce dynamic PII redaction.
2. **Outbound Passport Issuance**: Issue 3-Tier PKI DIT passports for internal AI employees with defined external scope and data labels.
3. **Sub-Microsecond RCU Revocation**: Instantly isolate compromised agents across the enterprise mesh via atomic RCU pointer swapping ($<1\mu\text{s}$).

### Q4.2 How do we automatically prevent administrative wildcard misconfigurations in CI/CD?
**A: Enforce static pre-flight scanning via `VajraCLI` (`cli.py lint`).**
* Integrated into CI/CD pipelines, `python cli.py lint <policy.yaml>` automatically fails (Exit Code 1) if non-admin roles are granted wildcard `*` or `admin.*` access.

---

## 5. Legal, Patents & Compliance Disclosures

### Q5.1 What scenarios fall outside DROS physical protection? (Boundary Disclosures)
**A: DROS transparently discloses 4 out-of-scope vectors:**
1. **Pure text conversational dialogue**: Conversational output without tool calls is governed by upstream LLM Guardrails.
2. **Authorized logic errors within valid bounds**: Actions within declared permissions require Level 3 CoW transaction rollback.
3. **Private key compromise**: Private key security relies on HSM hardware and cold storage.
4. **Host OS root-level compromise**: Root-level OS breaches fall under host kernel security.

### Q5.2 How are DROS patent and open-source licenses demarcated?
**A: Standard 3-Tier IP Constitution:**
1. **Core Runtime Substrate** ➔ U.S. Patent Pending (**U.S. PPA No. 64/111,973**).
2. **Community Client & Plugins** ➔ Permanent **Free License for Individuals**.
3. **Evaluation Harnesses** ➔ **Apache-2.0 License** (Evaluation code openness $\neq$ Core patent openness).

---
*DROS Official Master FAQ Hub ── Single Source of Truth, Globally Authoritative.* 🌐💎⚖️🏢🛡️
