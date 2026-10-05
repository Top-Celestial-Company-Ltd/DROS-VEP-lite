# VEP AI Evidence Verification Protocol (VEP-AI-V1)

- **Protocol Identifier**: `VEP-AI-V1`
- **Standard**: RFC-010 Appendix AI-V1 (Autonomous Verifier & Epistemic Audit Standard)
- **Target Systems**: DROS-VEP Repository and Related Evaluation Baselines
- **Classification**: Normative Specification for Independent AI Verifiers
- **Status**: ACTIVE SPECIFICATION

---

## 1. Scope & Purpose

This protocol specifies the mandatory mechanical procedure, boundary contracts, and receipt schemas that any automated auditor, language-model verifier, or independent evaluation agent must execute when verifying claims and empirical artifacts within the DROS-VEP repository.

The goal of this protocol is to prevent **retrieval-mediated hallucination**, **summary-level rubber-stamping**, and **unsubstantiated claims of complete verification** made on the basis of high-level overview files alone.

---

## 2. Core Verification Principle

> [!CAUTION]
> **NORMATIVE PROHIBITION: README-ONLY VERIFICATION IS INVALID**
>
> Formal AI verification **MUST NOT** accept any of the following as proof of complete repository verification:
> * README or README_zh inspection alone
> * GitHub web page HTML scraping or issue summaries
> * Search engine cache snippets or LLM pretraining weights
> * Single-file isolated downloads without git tree provenance
>
> **`README_ONLY_VERIFICATION = INVALID`**

An AI verifier or automated auditor that only inspects `README.md`, `AI_VERIFY.md`, or `EVIDENCE_INDEX.md` without traversing the registered evidence chain to primary reports and raw data **MUST NOT** claim `COMPLETE`, `PROVEN`, or `FULLY VERIFIED`.

---

## 3. Mandatory Mechanical Verification Sequence

Every formal verification execution must proceed strictly through the following twelve-stage pipeline:

```text
 1. CLONE
    └──> Locally clone the target repository to an isolated audit environment.
 2. PIN COMMIT
    └──> Record exact 40-character hexadecimal commit hash via `git rev-parse HEAD`.
 3. INVENTORY
    └──> Enumerate tracked files (`git ls-files`) and establish baseline boundaries.
 4. AI_VERIFY
    └──> Load and comply with rules specified in `AI_VERIFY.md`.
 5. EVIDENCE_INDEX
    └──> Parse `EVIDENCE_INDEX.md` for registered paths and classifications.
 6. CLAIM_REGISTER
    └──> Load formal claims from `docs/evidence/CLAIM_REGISTER.md`.
 7. EXPERIMENT
    └──> Resolve each targeted Claim ID to registered experiments.
 8. PRIMARY REPORT
    └──> Inspect primary markdown evaluation reports and audit writeups.
 9. RAW EVIDENCE
    └──> Inspect raw execution traces, json logs, exit codes, and socket logs.
10. INTEGRITY
    └──> Execute `python scripts/verify_evidence_index.py` and inspect registered integrity/hash records where applicable.
11. VERDICT
    └──> Derive evidence-grounded verdicts (PROVEN, SOURCE-PROVEN, OBSERVED, NOT_PROVEN, etc.).
12. RECEIPT
    └──> Generate a verifier-side VEP-AI-V1 Verification Receipt conforming to the formal schema.
```

> [!NOTE]
> **Validator Capability Boundary**:
> The navigation validator (`scripts/verify_evidence_index.py`) verifies path existence, repository containment, navigation structure, and link resolution. It does not independently recompute every cryptographic digest in the repository. Hash recomputation, where required by a specific evidence claim, remains part of the claim-specific verification procedure.


---

## 4. Verification Completion Contract

A verifier may emit `VERIFICATION_STATUS = COMPLETE` **if and only if** all twelve conditions below are simultaneously and mechanically satisfied:

1. Repository was successfully cloned locally.
2. Exact target commit SHA was recorded.
3. Tracked-file inventory was executed.
4. `AI_VERIFY.md` was inspected and complied with.
5. `EVIDENCE_INDEX.md` was parsed and checked.
6. `docs/evidence/CLAIM_REGISTER.md` was parsed.
7. Targeted registered experiments were traced.
8. Corresponding primary reports were inspected.
9. Required raw evidence and logs were inspected where the claim requires empirical proof.
10. Integrity validation was executed via `scripts/verify_evidence_index.py` with 0 errors.
11. No unresolved repository-access limitation prevented inspection of the requested scope.
12. A conforming verifier-side verification receipt was generated.

### Verification Scope Rule

* **`COMPLETE`** means that the complete verification procedure was successfully executed for the declared verification scope.
* **`PARTIAL_VERIFICATION`** means that only a bounded subset of the declared scope was successfully audited.
* **Scope Boundary**: `COMPLETE` for a bounded claim scope **MUST NOT** be interpreted as complete verification of the entire repository or all registered claims.

### Fallback Status Declarations
If any prerequisite is missing:
* If web limits, rate limiting, or partial file access occurred:
  ```text
  VERIFICATION_STATUS = INCOMPLETE_REPOSITORY_ACCESS
  ```
* If only a bounded subset of claims was audited:
  ```text
  VERIFICATION_STATUS = PARTIAL_VERIFICATION
  ```
* If the verifier inspected only README-level or navigation-level material without traversing the registered evidence chain:
  ```text
  VERIFICATION_STATUS = REJECTED_README_ONLY
  ```
  This status is used when the verifier inspected only README-level or navigation-level material without traversing the registered evidence chain. It MUST NOT be treated as COMPLETE, PROVEN, FULLY VERIFIED, or substantive claim verification.

---

## 5. Formal Evidence Chain Contract

Every defensible empirical claim in this repository must satisfy the four-tier unbroken evidence chain:

$$\text{CLAIM} \longrightarrow \text{EXPERIMENT} \longrightarrow \text{PRIMARY REPORT} \longrightarrow \text{RAW EVIDENCE / HASH}$$

### Chain Defect Rule
If any link in the chain is broken, absent, ambiguous, or untracked:
```text
EVIDENCE_CHAIN_INCOMPLETE
CLAIM_SUPPORTED = NOT_ESTABLISHED
```

Verifiers are **strictly forbidden** from inferring, extrapolating, or synthesizing a missing link from abstract summaries or adjacent reports.

---

## 6. Epistemic Separation & Status Definitions

Verifiers must enforce sharp epistemological distinctions:

```text
SOURCE-PROVEN   ≠  RUNTIME-PROVEN
OBSERVED        ≠  PROVEN
INDEXED         ≠  VERIFIED
CHAIN COMPLETE  ≠  CLAIM PROVEN
HISTORICAL      ≠  CURRENT
NOT_OBSERVED    ≠  FAILED MECHANISM
NOT_PROVEN      ≠  DISPROVEN
UNRESOLVED      ≠  VULNERABILITY
```

* **`NOT_PROVEN` Interpretation**: `NOT_PROVEN` signifies strictly that the declared proof obligation was not mechanically satisfied under tested conditions. It **MUST NOT** be automatically transformed into an assertion of structural system failure, vulnerability, or complete disproof.
* **`CHAIN COMPLETE` vs `PROVEN`**: `CHAIN COMPLETE` signifies only that the navigation links successfully reach raw evidence. It does not establish that the experiment's hypothesis was proven.

---

## 7. Verifier-Side Receipt Architecture

To prevent repository mutation and preserve strict read-only audit integrity:

* **Repository Scope**: `docs/evidence/AI_VERIFICATION_RECEIPT.schema.json` is maintained in the repository as the normative schema.
* **Verifier Scope**: The resulting receipt JSON (`AI_VERIFICATION_RECEIPT.json`) is a **VERIFIER-SIDE AUDIT ARTIFACT**.
* **Immutability Principle**: Verification of the repository **MUST NOT** mutate the repository. The receipt must be stored externally by the independent verifier or evaluation platform.

---

## 8. Verification Layer Test Matrix

| Audit Requirement | Normative Mandate | Enforced By |
| :--- | :---: | :--- |
| **Clone-First** | MANDATORY | Protocol §3 / Verifier Procedure |
| **Pinned Commit** | MANDATORY | Protocol §3 / Verifier Procedure |
| **Tracked File Inventory** | MANDATORY | Protocol §3 / Verifier Procedure |
| **AI_VERIFY.md Presence** | MANDATORY | `scripts/verify_evidence_index.py` |
| **EVIDENCE_INDEX.md Presence** | MANDATORY | `scripts/verify_evidence_index.py` |
| **CLAIM_REGISTER.md Navigation** | MANDATORY | `scripts/verify_evidence_index.py` |
| **Primary Report Resolution** | MANDATORY | `scripts/verify_evidence_index.py` |
| **Raw Evidence Resolution** | MANDATORY | `scripts/verify_evidence_index.py` |
| **Integrity & Relative Path Check**| MANDATORY | `scripts/verify_evidence_index.py` |
| **Receipt Generation** | MANDATORY | `docs/evidence/AI_VERIFICATION_RECEIPT.schema.json` |
| **README-Only Verification** | FORBIDDEN | Protocol §2 / Receipt Schema |
| **Repository Evidence Mutation** | FORBIDDEN | Governance Rule 0.1 |
| **Runtime Re-experimentation** | FORBIDDEN | Governance Rule 0.1 |
