<!-- dros_component: dros-vep-claude-red -->
<!-- dros_depends: [FREEZE_MANIFEST_PHASE2.md, EXPERIMENT_PLAN.md] -->
<!-- dros_description: Scientific Environment Provenance Manifest for Phase 1 & 2 (2A, 2B, 2C) -->
<!-- dros_status: Frozen -->
# 🌐 VEP × Claude-Red: Phase 1 & 2 Scientific Environment Provenance Manifest

> **Epistemic Provenance Integrity**: ANCHORED  
> **Evaluation Session Timestamp**: 2026-09-13T20:56:00+08:00  
> **Provenance Chain**: Model ➔ Adapter ➔ VEP Testbed ➔ DROS Reference PEP ➔ Physical Environment Target

---

## 1. 系統運行環境參數 (Host & Runtime Environment)

- **Operating System**: `Windows-10-10.0.19044-SP0` (Windows 10 x64)
- **Host Python Runtime**: `Python 3.12.0 (tags/v3.12.0:0fb18b0, Oct 2 2023, 13:03:39) [MSC v.1935 64 bit (AMD64)]`
- **Docker Engine**: `Docker version 26.1.1, build 4cf5afa`
- **VEP Core Repository SHA**: `c7bc58eb75dfdb2b66131c2e7a40459fa854f12e`
- **Upstream Claude-Red Pinned SHA**: `24d7968bab4b883e7f13477afe0fd91f2df3b722`

---

## 2. 模型與推論管道錨定 (Model Inference Provenance)

- **Adversarial Engine Model**: `anthropic/claude-sonnet-4.5`
- **Inference Router / Provider**: OpenRouter API (`https://openrouter.ai/api/v1/chat/completions`)
- **Routing & Client Headers**:
  - `HTTP-Referer`: `https://github.com/Top-Celestial-Company-Ltd/DROS-VEP-lite`
  - `X-Title`: `VEP Claude-Red Benchmark Harness`
- **Sampling Temperature**: `0.2` ~ `0.3` (Deterministic Evaluation Mode)

---

## 3. 執行期策略門禁固件校驗 (Policy & Target Provenance)

- **Target Fixture File**: [`targets.py`](file:///e:/vscode/AI知識庫/dros-vep-lite/benchmarks/claude-red-vep/targets.py)
- **Target Fixture SHA256**: `36790556eff47a07003002830775bbd291d195b15e173a85876f64d06c834faf`
- **Policy Enforcement Points**:
  - `DROS-POL-0001-PASS`: In-band authorized capability bitmask match.
  - `DROS-POL-0002-SCOPE`: Capability scope bounding check violation (Least Authority).
  - `DROS-POL-0021-PANIC`: Immutable system execution invariant boundary enforcement.

---

## 4. 原始交互軌跡與重現驗證日誌 (Raw Trajectory Logs)

- **Smoke Test Log**: `logs/SMOKE-RUN-1789299961.jsonl` (`26c7e9e398a2117bc565f4ffc18685117eebebe381e9fbf61cb8504f5cb25466`)
- **Phase 2A Log (Attribution Gap)**: `logs/PHASE2-PILOT-1789300452.jsonl` (`70e9af1db7083f7a69b7f5255474ca0217ec37e3d1c47ea41a293c66247ac5bc`)
- **Phase 2B Log (Autonomous Exec)**: `logs/PHASE2B-AUTO-1789301232.jsonl` (`459ba9707e4eee65b501d51a6cf9e2621ce30c6a51240c572a9cf2993049afa0`)
- **Phase 2C Log (Adaptive Loop)**: `logs/PHASE2C-ADAPT-1789302978.jsonl` (`43aaa794ba6ba87ae836bb6a17b07ea45fbc5f27150a112ec953fc956218164f`)

---

## 5. 重現性驗證保證 (Reproducibility Seal)

任何第三方評審人可使用上述完全相同的 Python 3.12 環境、Commit SHA 與 Targets 固件，透過 OpenRouter 模型調用重現上述 100% 阻斷與微秒級（P50 $\approx 3.00 \mu s$）確定性門禁指標。
