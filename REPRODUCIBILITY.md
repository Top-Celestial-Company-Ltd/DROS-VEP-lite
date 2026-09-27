<!-- dros_component: dros-vep-standards -->
<!-- dros_depends: [EVIDENCE_STATUS.md, docs/EVIDENCE_READING_GUIDE.md, benchmarks/claude-red-vep/FREEZE_MANIFEST_PHASE2.md, docs/VEP_METRIC_SPECIFICATION.md] -->
<!-- dros_description: Public reproducibility requirements and historically documented VEP workflows -->
<!-- dros_status: Public guidance / historical workflows require separate authorization -->
# 🔬 VEP Benchmark: Public Reproducibility Guide / VEP 基準：公開可重現性指南

> **Status: guidance only / 僅供指引。** The commands retained below are historical workflow descriptions, not a claim that the full suite is currently reproducible and not authorization to execute experiments. 下列命令是歷史工作流程說明，不代表整套基準目前可重現，也不構成實驗執行授權。

## Minimum record for a reproducibility claim / 可重現性主張的最低紀錄

A result may be described as reproducible only when its record binds all of the following / 只有在結果紀錄綁定下列全部資訊時，才可稱為可重現：

1. Exact source revision / 精確 source revision
2. Runner identity and version / runner 身分與版本
3. Environment and dependencies / 環境與相依項
4. Exact input and resulting output / 精確輸入與輸出
5. Independent, claim-appropriate oracle / 符合 claim 類型的獨立 oracle
6. Artifact provenance and custody / 工件 provenance 與保管鏈
7. Cryptographic hashes for the bound artifacts / 綁定工件的密碼學雜湊
8. Verification status and reviewerable reconstruction / verification status 與可供審查的重建方式

**The presence of a script or report alone does not establish reproducibility.** A hash match establishes byte identity only for the named bytes; it does not establish runtime validity or claim support. **僅有腳本或報告不構成可重現性。** 雜湊相符只證明指定 bytes 的身分，不代表 runtime 有效或 claim 獲得支持。

Start with [EVIDENCE_STATUS.md](EVIDENCE_STATUS.md). Do not infer a current result from the historical examples below. Begin any execution only after obtaining separate authorization for the exact scope. 請先閱讀 [EVIDENCE_STATUS.md](EVIDENCE_STATUS.md)；不得從下列歷史範例推定目前結果。任何執行前都須另行取得針對精確範圍的授權。

---

## 1. Environment Requirements / 環境需求

- **Runtime / 執行環境:** Python 3.10+ (the historical guide reports a Python 3.12.0 check / 舊指南記載曾以 Python 3.12.0 檢查)
- **Dependencies / 相依項:** Pure Python standard library (`urllib.request`, `json`, `hashlib`, `time`, `re`) for the described harness / 本指南所述 harness 使用 Python 標準函式庫。
- Some historical workflows used an external model provider. Any required credentials must be configured outside the repository; never commit or print credential values. 部分歷史流程使用外部模型服務；必要憑證須在倉庫外設定，不得提交或輸出憑證值。

The expected outputs in the following historical workflow are examples from prior documentation, not guaranteed or currently verified results. 以下歷史流程中的預期輸出是舊文件所載範例，不是保證值或目前已驗證結果。

---

## 2. Integrity Verification of Benchmark Assets / 基準工件完整性核對

Before any separately authorized run, compare the exact local fixtures and target definitions with the named manifest. The manifest's existence or a matching file hash alone does not establish that a run or result is valid. 任何另行授權的執行前，先比對精確 fixture、target definitions 與指定 manifest；manifest 存在或單一檔案 hash 相符，均不單獨證明 run 或結果有效：

```powershell
# Run from the repository root in PowerShell (Windows):
Set-Location benchmarks/claude-red-vep
Get-FileHash targets.py, targets_2d.py, targets_2e.py, targets_2f.py -Algorithm SHA256
```

Compare outputs against [`FREEZE_MANIFEST_PHASE2.md`](benchmarks/claude-red-vep/FREEZE_MANIFEST_PHASE2.md), while checking that the manifest binds the exact source, runner, environment, input, and artifacts for the result under review.

---

## 3. Historical Suite Workflow / 歷史套件流程

### Stage 1: Phase 1 Smoke Test / 階段一：Phase 1 Smoke Test（歷史流程；須另行授權）
```powershell
python run_smoke_test.py
```
- **Historical reported output / 歷史文件所載輸出:** UER: ARM-A = 100.0%, ARM-B = 0.0%. Not a current or guaranteed result. 非目前結果或保證值。

### Stage 2: Phase 2A Attribution Gap Pilot / 階段二：Phase 2A Attribution Gap Pilot（歷史流程；須另行授權）
```powershell
python run_autonomous_phase2.py
```
- **Historical reported output / 歷史文件所載輸出:** Model outputs `decline`; ARM-A executes unchecked (Attribution Gap), ARM-B denies. Not a current or guaranteed result. 非目前結果或保證值。

### Stage 3: Phase 2B Autonomous Execution / 階段三：Phase 2B Autonomous Execution（歷史流程；須另行授權）
```powershell
python run_autonomous_phase2b.py
```
- **Historical reported output / 歷史文件所載輸出:** Model tool calls and ARM-B UER = 0.0%, 2/2 Benign Pass. Not a current or guaranteed result. 非目前結果或保證值。

### Stage 4: Phase 2C Adaptive Attack Loop / 階段四：Phase 2C Adaptive Attack Loop（歷史流程；須另行授權）
```powershell
python run_autonomous_phase2c.py
```
- **Historical reported output / 歷史文件所載輸出:** AAR ≥ 50% (three-round pivot description); ARM-B PD-UER = 0.0%. Not current or guaranteed. 歷史描述為三輪 pivot；非目前結果或保證值。

### Stage 5: Phase 2D Capability Chaining & Argument Gating / 階段五：能力串鏈與參數門控（歷史流程；須另行授權）
```powershell
python run_autonomous_phase2d.py
```
- **Historical reported output / 歷史文件所載輸出:** Same-interface argument bounds blocked; 3/3 benign controls preserved. Not current or guaranteed. 歷史記載為同介面參數邊界阻擋、3/3 benign controls 保留；非目前結果或保證值。

### Stage 6: Phase 2E Post-Compromise Crucible / 階段六：入侵後測試（歷史流程；須另行授權）
```powershell
python run_autonomous_phase2e.py
```
- **Historical reported output / 歷史文件所載輸出:** Five-round adversarial mandate; PC-EER: ARM-A = 100.0%, ARM-B = 0.0%. Not current or guaranteed. 歷史記載為五輪 adversarial mandate；非目前結果或保證值。

### Stage 7: Phase 2F Temporal Authority & Hot Revocation / 階段七：時效授權與即時撤銷（歷史流程；須另行授權）
```powershell
python run_autonomous_phase2f.py
```
- **Historical reported output / 歷史文件所載輸出:** T1 ALLOW ➔ T2 Revoke ➔ T3/T4 DENY ➔ T5 unrevoked read ALLOW; RER = 0.0%. Not current or guaranteed. 歷史狀態序列與數值，非目前結果或保證值。

---

## 4. Metric Computation & Output Audit / 指標計算與輸出稽核

The historical workflow describes JSONL output under `benchmarks/claude-red-vep/logs/`; file creation alone does not establish immutability, completeness, provenance, or a valid run. 舊流程描述會在該路徑輸出 JSONL；檔案生成不代表不可變、完整、來源清楚或 run 有效。
Formal metric definitions (UER, PC-EER, RER, AAR) and inclusion/exclusion rules are described in [`docs/VEP_METRIC_SPECIFICATION.md`](docs/VEP_METRIC_SPECIFICATION.md). Their existence does not establish that a particular run satisfies those rules. 指標定義與納入／排除規則見該文件；文件存在不代表任何特定執行已符合規則。
