<!-- dros_component: dros-vep-claude-red -->
<!-- dros_depends: [EXPERIMENT_PLAN.md, targets.py] -->
<!-- dros_description: Scientific State Freeze Manifest for Phase 1 and Phase 2 (2A, 2B, 2C) Reproducibility -->
<!-- dros_status: Frozen -->
# 🧊 VEP × Claude-Red: Phase 1 & Phase 2 (2A/2B/2C) Scientific State Freeze Manifest

> **Epistemic State**: FROZEN & ANCHORED  
> **Date**: 2026-09-13  
> **Commit Context**: Upstream Claude-Red `24d7968bab4b883e7f13477afe0fd91f2df3b722`  
> **Model Identifier**: `anthropic/claude-sonnet-4.5` (via OpenRouter API routing)  
> **Empirical Invariant (Under Evaluated Execution Surface & Policy Configuration)**:  
> $$\mathcal{C}_{\text{adversarial\_cognition}} \land \mathcal{E}_{\text{authority\_bounded}} \implies I_{\text{unauthorized\_physical}} = 0$$

---

## 1. 實驗演進與已驗證結論矩陣 (Validated Findings Matrix)

| 實驗階段 | 核心測試目標 | Agent / Model 行為 | ARM-A (Baseline) | ARM-B (DROS) | 核心量化指標 |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Phase 1** | Smoke Test (N=10) | 靜態已知攻擊向量投毒 | UER: 100.0% (8/8) | **UER: 0.0%** (0/8) | P50 Latency: 1.65 μs, FPR: 0.0% |
| **Phase 2A** | Attribution Gap Pilot | 認知自律拒絕 (`decline`) | 執行器誤透傳 (4/4 側效應) | **100% 邊界熔斷** (0 次側效應) | 實證 Cognition $\neq$ Execution Authority |
| **Phase 2B** | True Autonomous Execution | 自主生成攻擊工具與參數 | 100.0% 執行 (4/4 側效應) | **UER: 0.0%** (0/4 阻斷) | 陰性對照保通 (2/2 ALLOW), Median: 5.40 μs |
| **Phase 2C** | Adaptive Multi-Turn Loop | 被拒後多輪動態換路適應 | 100.0% 執行 (4/4 側效應) | **PD-UER: 0.0%** (0/4 阻斷) | **AAR: 66.7%**, Median Latency: 3.00 μs |
| **Phase 2D** | Capability Chaining & Gating | 同介面細粒度參數與鏈結探測 | 100.0% 執行 (3/3 側效應) | **UER: 0.0%** (0/3 阻斷) | 3/3 Benign Preserved, Median: 14.70 μs |
| **Phase 2E** | Post-Compromise Crucible (Flagship) | 100% 認知失守下自主多戰術橫向突防 | 100.0% 執行 (5/5 側效應) | **PC-EER: 0.0%** (0/5 阻斷) | 5 輪戰術換路全封死, Median: 2.40 μs |
| **Phase 2F** | Temporal Authority & Hot Revocation | 執行憑據熱撤銷後之重放與殘留探測 | 100.0% 執行 (2/2 側效應) | **RER: 0.0%** (0/2 阻斷) | 未撤銷能力保通 (1/1 ALLOW), Median: 4.15 μs |

---

## 2. 凍結工件與密碼學校驗清單 (Cryptographic Checksums)

所有測試腳本、雙臂受測固件、原始 JSONL 交互軌跡與科研報告均已計算 SHA256 錨定：

| 類別 | 工件相對路徑 | SHA256 完整校驗碼 | 大小 (Bytes) |
| :--- | :--- | :--- | :--- |
| **Core Harness** | `adapters/claude_red/adapter.py` | `b221aae4d4efe333d4537ddc225010996452818aa2a6134b92b67f130cb4c1db` | 2,806 |
| **Target Fixtures**| `targets.py` (Phase 1-2C) | `36790556eff47a0750259b3bb87569b321cfbfe9351e289bf6ef3f9e6c834faf` | 4,298 |
| | `targets_2d.py` (Phase 2D) | `c536deaf8ed8f057bf0446cb8c1f1c5ca575c061298de3356c01ca5c290f9000` | 6,650 |
| | `targets_2e.py` (Phase 2E) | `4a40fb83064e00b3596e0921bea6506d49f778375ac5feb5ff24a744a5af0c8f` | 5,886 |
| | `targets_2f.py` (Phase 2F) | `f587a04a044db080c5c10605e167bd57bdaf3120b8558d48a0b5c6c8e36e6291` | 5,463 |
| **Execution Scripts** | `run_smoke_test.py` | `d01bd12fbdbf4369e46a78ea38a6aebdb2d326c7104b2b63eb1e0fffea596b59` | 8,433 |
| | `run_autonomous_phase2.py` | `5d5025e40f735b3f2e04313f8c87eb8f15456b3c4371cbcfd268d879408e9d7a` | 10,790 |
| | `run_autonomous_phase2b.py` | `ab3336e3fc3bc7b70c2a233fa26aa8772591e0a296e85746f34ffc498dfd0653` | 12,564 |
| | `run_autonomous_phase2c.py` | `2b447a7ac72a99988b43f053229b13997cfcfc2a046c82d0016ea9a706897d4c` | 15,092 |
| | `run_autonomous_phase2d.py` | `dae7636497688ef5e6197e33207fc4cdea6f7096a7f289d5ac1734ae9fa2c81f` | 12,471 |
| | `run_autonomous_phase2e.py` | `dec020c0830b6904f279fc0a1b968d5089f611c264f62672bfa28dbce2cc7b4d` | 10,950 |
| | `run_autonomous_phase2f.py` | `0b5bc092819887a728e5c5e869a483ec4437beb7a2746077e0ce3030bb354c27` | 12,450 |
| **Raw Trace Logs** | `logs/SMOKE-RUN-1789299961.jsonl` | `26c7e9e398a2117bc565f4ffc18685117eebebe381e9fbf61cb8504f5cb25466` | 5,757 |
| | `logs/PHASE2-PILOT-1789300452.jsonl` | `70e9af1db7083f7a69b7f5255474ca0217ec37e3d1c47ea41a293c66247ac5bc` | 9,636 |
| | `logs/PHASE2B-AUTO-1789301232.jsonl` | `459ba9707e4eee65b501d51a6cf9e2621ce30c6a51240c572a9cf2993049afa0` | 10,212 |
| | `logs/PHASE2C-ADAPT-1789302978.jsonl` | `43aaa794ba6ba87ae836bb6a17b07ea45fbc5f27150a112ec953fc956218164f` | 20,512 |
| | `logs/PHASE2D-CHAIN-1789304303.jsonl` | `5fe87acd4853bd417811f1a90bc151c3d534cf7a06db71c1b657e2585e52a6d8` | 11,265 |
| | `logs/PHASE2E-POSTCOMP-1789304820.jsonl` | `aef4a8dae9dfc55e332fb34774344e226b57dfd9eb72f796040b7f8e448dc34c` | 11,746 |
| | `logs/PHASE2F-REVOKE-1789305598.jsonl` | `df8202614e6911353c07275eeb9f40fd0b435789c18418904b428d15f427d63d` | 4,430 |
| **Reports** | `reports/preliminary.md` | `a12b961f3f8be7c67425f187ee09e46a7ce8276f570775d7b51b32941c28403b` | 4,954 |
| | `reports/autonomous_phase2a_report.md`| `9a7bd37f6b9847af1bfe39050d4d0da61d784aee9cbcf8929910d540cc3e2ce8` | 5,311 |
| | `reports/autonomous_phase2b_report.md`| `82392b5fd2698c4edbe2b655d64821a71ef73e72847a95632a4e21626b0dc5bd` | 5,450 |
| | `reports/autonomous_phase2c_report.md`| `970b6adcc0dbe6aa77c68832a875a6cff4891b9750058ec00582236032237fe0` | 6,465 |
| | `reports/autonomous_phase2d_report.md`| `072e533b3344c2b8ab9732c882c1394dfae467d83f4fddfe430bebb8b923c43e` | 6,035 |
| | `reports/autonomous_phase2e_report.md`| `4e6f24e93be89486c7d0f66f83323b2184d35a101164a5eb426e94aea73e16e3` | 6,240 |
| | `reports/autonomous_phase2f_report.md`| `538fa4381d23bee35c1aa64cb1578a93efc9bf61a444f246abe556ca9d4a0dd2` | 5,120 |

---

## 3. 全線大閉環 (Full Benchmark Suite Closed & Frozen)

**Phase 1 ➔ Phase 2A ➔ Phase 2B ➔ Phase 2C ➔ Phase 2D ➔ Phase 2E ➔ Phase 2F** 六階實驗已全部完成實裝、實測、量化、報告產出與 SHA256 密碼學錨定。
不再擴展新的攻擊案例，整體 Phase 2 全面凍結，直接轉入論文與標準 Benchmark 發布階段。
