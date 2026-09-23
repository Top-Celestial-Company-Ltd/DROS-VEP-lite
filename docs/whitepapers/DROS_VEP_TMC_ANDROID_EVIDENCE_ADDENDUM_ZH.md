# DROS-VEP TMC Android 證據補充

**狀態：** 已索引之研究證據補充 | **日期：** 2026-09-23 | **目標環境：** Pixel_7 AVD / Android 34 / x86_64

本補充記錄支撐擴充版 DROS-Mobile 論文的 Android 證據，並補充 VEP 證據分類；不擴大 DROS 商品保證，也不取代 canonical 實驗 artifacts。

## 證據軌道

### DROS application-runtime 軌道

- **Security semantics：** T4/BASE-04 未授權拒絕、T5/BASE-03 授權執行、T7/BASE-05 撤銷，形成宣告範圍內的 grant–enforce–revoke lifecycle。
- **Decision-path measurements：** T9/T10 提供 serial DENY/ALLOW observations；T16/T18/T20 提供 accounting-backed 的描述性 2/4/8 concurrency series。
- **Ingress 與 accounting：** T14 及 T15/T17/T19 建立宣告的 ingress 與 pipeline-accounting 前置證據。T11/T12 僅保留為 failure provenance，不是 canonical performance results。
- **Canonical index：** [`ANDROID_BASELINE_EVIDENCE_INDEX.md`](../../reports/evidence/tmc_android_phase1_2_index/20260922T_INDEX_CLOSED/ANDROID_BASELINE_EVIDENCE_INDEX.md) 及其 JSON index。

### Android framework-baseline 軌道

| Unit | 證據狀態 | 有界觀測 |
|---|---|---|
| `ANDROID-PERM-01` | Verified | Native permission state 與宣告的 ContactsProvider fixture outcome 相符。 |
| `ANDROID-APPOPS-01` | Verified | AppOps deny/allow state 與宣告的 app-side result、effect marker 相符。 |
| `ANDROID-BINDER-01` | Verified | Permission state 與受保護測試 Binder service 的 transaction/effect 相符。 |
| `ANDROID-SELINUX-01` | Observed, not canonical | 記錄 enforcing mode 與 app context；未建立 app-specific AVC denial attribution。 |

Framework-baseline closure index 與中英文報告位於 [`reports/evidence/tmc_android_framework_baselines/20260923T_INDEX_CLOSED/`](../../reports/evidence/tmc_android_framework_baselines/20260923T_INDEX_CLOSED/)。

## 重現入口

- 實驗契約：[`TMC_ANDROID_BASELINE_PHASE1_CONTRACT.md`](../benchmarks/TMC_ANDROID_BASELINE_PHASE1_CONTRACT.md)
- Android security tests：`python -m pytest tests/security/android -q`
- AVD runners 與 app fixtures：`benchmark/run_tmc_android_*_avd.py`、`scripts/build_tmc_android_*_baseline.ps1`、`benchmarks/android_*_app/`
- 雙語報告與 machine-readable index：見上方連結；raw records 與 closure files 保存在 `reports/evidence/`。

## Claim ceiling

證據只適用於宣告的 Pixel_7 Android 34 x86_64 AVD path 及其特定 application-runtime 或 framework fixture。2/4/8 series 是描述性結果，不是 scalability law 或因果歸因。本研究不建立 Android-wide／OS-wide enforcement、一般 Binder／SELinux 性質、實體裝置效能或能耗，也不建立產品層級的 mobile security guarantee。本補充不修改已凍結的 T4–T20 canonical artifacts。

對應論文為 v2.0.1 Zenodo preprint，已投稿 IEEE Transactions on Mobile Computing：<https://doi.org/10.5281/zenodo.22913070>。
