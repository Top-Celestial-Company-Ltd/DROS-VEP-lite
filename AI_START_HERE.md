# AI_START_HERE: AI Navigation Protocol for DROS-VEP Lite

- **Repository**: https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite
- **Pinned baseline commit**: `6d305d7c1a460569661eaea045a562ed802a243e`
- **Layer**: discovery layer on top of VEP-AI-V1 (it does not replace [`AI_VERIFY.md`](AI_VERIFY.md))

## Purpose

This is the AI-readable navigation entrypoint for DROS-VEP.

If you arrived from a GitHub URL, do not stop at `README.md`.
README-only inspection is insufficient for VEP verification. A reviewer who stops at README has not completed the evidence audit.

## Capability modes

### Mode A: Web / Chat AI (read access only)

You can: read documentation, claims, experiment descriptions, reports and any exposed raw evidence; follow links; understand epistemic status.

You cannot: execute validators, reproduce experiments, reproduce runtime behavior, or claim reproduction you did not perform.

Allowed verdicts: `DOCUMENTARY_REVIEW` or `PARTIAL_VERIFICATION`, depending on what you actually accessed. Reading a primary report is not experiment reproduction.

### Mode B: Clone / Terminal Agent

You can: clone, pin the commit, inventory files, read governance files, run validators, inspect raw evidence, reproduce where authorized, and generate a verifier-side receipt.

Verdicts follow VEP-AI-V1 (`COMPLETE`, `PARTIAL_VERIFICATION`, `INCOMPLETE_REPOSITORY_ACCESS`, `REJECTED_README_ONLY`); see [`docs/evidence/AI_VERIFICATION_PROTOCOL.md`](docs/evidence/AI_VERIFICATION_PROTOCOL.md) and [`docs/evidence/AI_VERIFICATION_RECEIPT.schema.json`](docs/evidence/AI_VERIFICATION_RECEIPT.schema.json).

## Reading order

1. [`README.md`](README.md)
2. `AI_START_HERE.md` (this file)
3. [`MANIFEST.md`](MANIFEST.md) (also [`llms.txt`](llms.txt))
4. [`AI_VERIFY.md`](AI_VERIFY.md)
5. [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
6. [`docs/evidence/CLAIM_REGISTER.md`](docs/evidence/CLAIM_REGISTER.md)
7. [`docs/evidence/AI_VERIFICATION_PROTOCOL.md`](docs/evidence/AI_VERIFICATION_PROTOCOL.md)
8. The relevant experiment
9. The relevant primary report
10. The relevant raw evidence
11. Integrity / hash metadata

**Reading order != proof order.** Proof requires the chain
`CLAIM -> EXPERIMENT -> PRIMARY REPORT -> RAW EVIDENCE / HASH`.

## Epistemic rules

```text
INDEXED != PROVEN
CHAIN COMPLETE != CLAIM PROVEN
OBSERVED != UNIVERSALLY PROVEN
HISTORICAL != CURRENTLY REPRODUCED
NOT_PROVEN != SYSTEM FAILURE
README SUMMARY != RAW EVIDENCE
DISCOVERABLE != VERIFIED
WEB ACCESS != EXPERIMENT REPRODUCTION
```

If evidence is inaccessible, report the limitation. Do not infer missing evidence. Do not upgrade a claim because a report sounds convincing. Cite evidence by commit-pinned URL (see [`MANIFEST.md`](MANIFEST.md)), not by branch name.

## Physical drone (S2-D)

S2-D is `CLOSED - NOT_PROVEN`. README text cannot overturn it. Read the forensic report
[`reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md`](reports/evidence/drone/m1_1/s2_v2/s2_d/S2_D_PX4_EXECUTION_AUTHORITY_FORENSIC_REPORT.md)
and the Gate 1 evidence under `reports/evidence/drone/m1_1/s2_v2/s2_d_gate1/`. `NOT_PROVEN` means the proof obligation was not established; it is not a vulnerability finding and not disproof.

## Running the validators (Mode B only)

```bash
python scripts/verify_evidence_index.py
python scripts/verify_ai_verification_receipt.py <receipt.json>
```

The navigation validator checks paths, links and index structure. It does not recompute every digest and does not convert indexed evidence into `PROVEN`. Receipts are verifier-side artifacts and must be stored outside this repository.
