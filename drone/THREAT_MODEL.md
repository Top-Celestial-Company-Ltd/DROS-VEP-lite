# Threat Model — DROS Drone Extension

## Core thesis

> Compromised Cognition / Control ≠ Compromised Execution Authority

An agent's reasoning, planning, prompt context, or control logic being compromised should not automatically imply it retains authority to execute dangerous physical actions.

Extended to the cyber-physical domain:

> Cyber-Cognitive Compromise → Physical Execution Boundary

## In-scope adversary capabilities (by scenario)

| Scenario | Adversary capability assumed |
|---|---|
| ATS-006 | Compromised onboard mission agent issuing unauthorized flight commands (forged/unsigned/expired/wrong-principal requests, direct adapter bypass) |
| ATS-007 | External navigation input spoofed or degraded; tests DROS's response to posture, not spoofing detection itself |
| ATS-008 | Network-adjacent observer capturing and replaying a previously valid ExecutionRequest |
| ATS-009 | Agent or attacker forging, omitting, or staling a provenance credential |
| ATS-010 | Agent self-asserting a favorable runtime posture that contradicts the true external posture |

## Explicitly out of scope for this threat model (tracked, not solved, here)

- Physical hijacking of the airframe (not an AI-governance problem)
- GPS-spoofing *detection* (DROS consumes posture, does not detect spoofing — see ATS-007 boundary note)
- CLI-level governance completeness — carried over as a known open problem from the software-agent DROS work; see `trustworthy-agent-architecture` project notes. Recommendation there (avoid CLI, prefer MCP/structured tool calls) applies here too, and `PATH-SHELL` in `../DRONE_EXECUTION_PATH_INVENTORY.json` is marked accordingly.
- Aviation certification (DO-178C, SORA) — mapping only, see `../DRONE_ASSURANCE_MAPPING.md`

## Attacker vs. DROS boundary

DROS's claimed boundary is: **execution paths for which an enforceable Policy Enforcement Point exists and whose mediation boundary has been explicitly identified and tested.** Any unmediated path is out of the proven boundary by default and must be reported as `NOT_PROVEN`, not silently assumed covered. See `T4-01` bypass testing and `../DRONE_EXECUTION_PATH_INVENTORY.json`.

## PEP Evaluation Integrity & Anti-Mock Constraint (STOP-01 Protocol)

> **RIGID IMPLEMENTATION MANDATE**:
> Policy Enforcement Point (PEP) verdicts must originate strictly from the full DROS Policy Engine evaluation pipeline (`adapter.evaluate_and_execute()` or C-ABI PGM microkernel) over parsed, structured schemas (Principal, Capability, Provenance, ArgHash, Expiry, Runtime Posture).
> 
> **Explicitly Prohibited**:
> 1. Keyword/substring matching on raw wire bytes (e.g., matching `b"UNAUTHORIZED"` or `b"ARM_ATTACK"`).
> 2. Hardcoded test-script tokens or shared magic strings between test harness and proxy.
> 3. Bypassing schema deserialization or policy decision loops under the guise of "network optimization".
> 
> Every denial must be backed by a deterministic, auditable reason code emitted by the policy engine (`ARG_HASH_MISMATCH`, `PROVENANCE_FORGERY_OR_INVALID`, `REQUEST_EXPIRED`, `UNAUTHORIZED_CAPABILITY`, `UNTRUSTED_POSTURE_REFERENCE`). Tests must assert this engine-emitted reason code directly from the proxy audit trail.

