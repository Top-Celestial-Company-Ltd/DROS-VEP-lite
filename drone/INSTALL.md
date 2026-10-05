# Install — DROS Drone Extension (Phase 0/1 scaffold)

> This file must be kept accurate enough that a third party can go clone → install → build → launch → run first governance test → inspect evidence with **no undocumented manual step, no private dependency, no developer-machine-specific path, no hidden configuration** (v0.3 T0-01 acceptance criteria). Until every step below is filled in and verified, installability is `NOT_PROVEN` — do not claim otherwise.

## 0. Freeze the baseline first

Before installing anything, fill in `../DRONE_BASELINE_MANIFEST.json` (DROS version, VEP version, host OS, CPU, compiler, PX4 version, MAVLink dialect, simulator version, git commit, artifact hash) and set `"frozen": true`. All later benchmark/latency numbers are meaningless without this.

## 1. Prerequisites

- OS: Windows 10/11 x86_64 or Ubuntu 22.04 LTS
- Python: 3.10+ (Current frozen baseline: Python 3.12.0)
- Python Dependencies: `pytest`, `jsonschema`, `pyyaml`
- Optional for live hardware/SITL: PX4 Autopilot v1.14 toolchain / `pymavlink`

## 2. Clone & Setup

```bash
git clone https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite.git
cd DROS-VEP-lite
pip install -r requirements.txt  # ensures jsonschema, pytest, pyyaml
```

## 3. Verify Baseline & Schema Integrity

```bash
# Verify frozen baseline and schema definitions
python -m pytest -s tests/drone/test_t0_installability.py
```

## 4. Run Drone Execution Governance Suites

```bash
# Run all 7 drone security & governance suites (ATS-006 ~ ATS-010, T4, T5, T8)
python -m pytest -s tests/drone/
```

## 5. Run via Unified VEP CLI

```bash
# Check registered substrate
python vep.py substrate list

# Evaluate canonical post-compromise scenario against drone substrate
python vep.py benchmark post-compromise --scenario PC-001 --substrate dros-drone
```

## 6. Inspect Evidence

Evidence lands in `reports/evidence/drone/` and is indexed in `DRONE_EVIDENCE_MANIFEST.json`.
Check `reports/evidence/drone/DRONE_CLAIM_MATRIX.md` for claim status and limitations.
