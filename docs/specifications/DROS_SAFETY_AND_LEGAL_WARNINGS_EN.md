# ⚖️ DROS Enterprise Legal Disclaimers, Safety Warnings & Boundary Disclosures
<!-- dros_component: dros-safety-warnings-en -->
<!-- dros_depends: [DROS_COMMERCIAL_RELEASE_SPEC_v1.0.md, DROS_ENTERPRISE_FAQ_AND_AI_ASSIST_GUIDE_EN.md] -->
<!-- dros_description: Standard enterprise legal disclaimers, physical boundary disclosures, security warnings, and 3-tier IP licensing terms aligned with public enterprise software standards -->
<!-- dros_status: Active -->

> **Important Notice:** This document constitutes an integral part of the official delivery package for DROS commercial products. Prior to procuring, installing, or deploying DROS, enterprise customers **must review and agree to all terms, boundary limits, and cautions detailed herein**.

---

## 🚫 1. Boundary Disclosure: Out-of-Scope Security Vectors

As a deterministic binary enforcement substrate situated at the OS and FFI boundary, DROS strictly defines its protection capabilities.
To ensure transparent expectations, the following 4 vectors are explicitly disclosed as **out-of-scope for DROS physical runtime enforcement**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│               DROS Boundary Disclosures & Responsibility Matrix             │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ 1. Pure Text Conversational   │ ❌ Out of Scope for DROS Binary Kernel      │
│    Prompt Hijacking           │ Reason: DROS governs physical execution and │
│                               │ actions, not text dialogue. Upstream LLM    │
│                               │ Guardrails must be deployed for text.       │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. Logic Errors within        │ ❌ Out of Scope for Access-Control Gate     │
│    Authorized Rule Bounds     │ Reason: If an agent is granted write access │
│                               │ to `db.table`, overwriting valid records is │
│                               │ authorized. Use Level 3 CoW rollback.       │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. Private Key Compromise &   │ ❌ Out of Scope for Runtime Microkernel     │
│    Forged Seed Signatures     │ Reason: DROS verifies valid cryptographic   │
│                               │ signatures. Use HSM and strict cold storage.│
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. Host OS Root-Level Breach  │ ❌ Out of Scope for User-Space Gateways     │
│    & Memory Tampering         │ Reason: Root compromises subvert host kernel│
│                               │ memory protection; rely on host OS hardening│
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## ⚠️ 2. Enterprise Security Cautions & Mandatory Warnings

### 🚨 Caution 1: Prohibition of Wildcard Grants to Non-Admin Agents
> [!CAUTION]
> When authoring `policy.yaml`, **NEVER** assign wildcard permissions (`action: allow, tool: '*'`) to non-admin agents.
> Overly permissive wildcard rules negate deterministic isolation. Enforce static pre-flight scanning via `python cli.py lint` before production release.

### 🚨 Caution 2: Client Plugin Fail-Safe Default Notice
> [!WARNING]
> By default, third-party client plugins (e.g., DSH Plugin) operate with `strictFailClosed: false` (Fail-Open / Fail-Safe) to prevent host disruption during upstream gateway reboots.
> For **zero-trust mission-critical environments**, explicitly set `strictFailClosed: true`.

### 🚨 Caution 3: Hard Kill (SIGKILL) Data Consistency Warning
> [!WARNING]
> When Tier 3 (Hard Kill) triggers an immediate `SIGKILL` termination, active non-transactional socket connections are aborted instantly. Ensure enterprise target systems implement transactional rollback mechanisms.

---

## 🏛️ 3. Standard 3-Tier IP & Licensing Constitution

1. **🔒 Core Runtime Substrate ➔ Patent Pending**:
   * **Patent Notice:** Protected under U.S. Provisional Patent Application (U.S. PPA No. 64/111,973, Patent Pending). All commercial, enterprise, and resale rights are exclusively reserved by Top Celestial Company Ltd.
2. **🎁 Community Client / Plugin ➔ Free License for Individuals**:
   * Individual developers receive permanent in-memory sub-microsecond interception for personal use; proprietary source code remains fully reserved.
3. **🧪 Benchmark Harness ➔ Open Source (Apache-2.0 License)**:
   * Evaluation harnesses and RFC test scenarios are open source under Apache-2.0 for academic reproducibility; evaluation code openness $\neq$ core governance patent openness.

---

## ⚖️ 4. International Regulatory Compliance & AS-IS Warranty

1. **EU AI Act & NIST SP 800-207 Alignment**:
   * DROS cryptographic audit trails and deterministic bounds comply with EU AI Act Article 12/50 traceability requirements and NIST Zero Trust invariants.
2. **Limited Warranty (AS-IS Disclaimer)**:
   * To the maximum extent permitted by applicable law, DROS is provided "AS-IS". Top Celestial assumes no indirect liability for misconfigured policies, lost keys, or unauthorized modifications.

---
*DROS Enterprise Safety Warnings & Legal Disclaimers ── Globally Compliant & Transparent.* ⚖️🛡️💎
