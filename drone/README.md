# DROS Drone Governance Extension

**Status:** Preview / Phase 0 scaffold — see `DROS-VEP-DRONE-PLAN-2026-v0.3.md` for the full plan this directory implements.

## What this is

DROS is an installable execution-governance substrate for autonomous AI agents. This directory is an experimental extension of that substrate to cyber-physical drone execution, publicly evaluated through reproducible post-compromise security tests against a PX4/MAVLink reference platform.

## What this is not (yet)

- Not a certified aviation safety system (see `DRONE_ASSURANCE_MAPPING.md` — mapping only)
- Not a claim of complete mediation of the entire drone (see `DRONE_EXECUTION_PATH_INVENTORY.json` — most paths are `NOT_PROVEN` until enumerated and tested)
- Not validated on physical hardware yet (SITL-first; HIL is a later phase, see plan §26 T9)

## Directory map

- `schemas/` — JSON Schemas for ExecutionRequest, runtime posture, provenance, and safety state
- `adapters/` — px4 / mavlink / ros2 adapters (implementation pending)
- `scenarios/ATS-00[6-10]/` — adversarial test scenario manifests
- `manifests/` — scenario/test manifests shared across the drone extension
- `../DRONE_BASELINE_MANIFEST.json` — frozen environment baseline (fill before Phase 1)
- `../DRONE_EXECUTION_PATH_INVENTORY.json` — candidate execution paths and mediation status
- `../reports/evidence/drone/DRONE_CLAIM_MATRIX.md` — what is and isn't proven, right now
- `../reports/evidence/drone/DRONE_EVIDENCE_MANIFEST.json` — append-only evidence log

## Core principle

> If DROS cannot prove the execution boundary, DROS must not claim the execution boundary.

See `CLAIM_BOUNDARY.md` for the disallowed claim list and approved claim language templates.

## Install

See `INSTALL.md`.

## Threat model

See `THREAT_MODEL.md`.
