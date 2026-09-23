# DROS-VEP TMC Android Evidence Addendum

**Status:** Evidence-indexed research addendum | **Date:** 2026-09-23 | **Target:** Pixel_7 AVD / Android 34 / x86_64

This addendum records the Android evidence supporting the substantially expanded DROS-Mobile manuscript. It supplements the VEP evidence taxonomy; it does not broaden DROS product guarantees or replace the canonical experiment artifacts.

## Evidence lanes

### DROS application-runtime lane

- **Security semantics:** T4/BASE-04 unauthorized deny, T5/BASE-03 authorized execution, and T7/BASE-05 revocation form the declared grant–enforce–revoke lifecycle.
- **Decision-path measurements:** T9/T10 provide serial DENY/ALLOW observations; T16/T18/T20 provide an accounting-backed descriptive 2/4/8-concurrency series.
- **Ingress and accounting:** T14 and T15/T17/T19 establish the declared ingress and pipeline-accounting prerequisites. T11/T12 remain failure provenance and are not canonical performance results.
- **Canonical index:** [`ANDROID_BASELINE_EVIDENCE_INDEX.md`](../../reports/evidence/tmc_android_phase1_2_index/20260922T_INDEX_CLOSED/ANDROID_BASELINE_EVIDENCE_INDEX.md) and its JSON index.

### Android framework-baseline lane

| Unit | Evidence status | Bounded observation |
|---|---|---|
| `ANDROID-PERM-01` | Verified | Native permission state correlated with the declared ContactsProvider fixture outcome. |
| `ANDROID-APPOPS-01` | Verified | AppOps deny/allow states correlated with the declared app-side result and effect marker. |
| `ANDROID-BINDER-01` | Verified | Permission state correlated with a protected test Binder service transaction/effect. |
| `ANDROID-SELINUX-01` | Observed, not canonical | Enforcing mode and app context were captured; no app-specific AVC denial attribution was established. |

The framework-baseline closure index and bilingual reports are in [`reports/evidence/tmc_android_framework_baselines/20260923T_INDEX_CLOSED/`](../../reports/evidence/tmc_android_framework_baselines/20260923T_INDEX_CLOSED/).

## Reproduction entry points

- Experiment contract: [`TMC_ANDROID_BASELINE_PHASE1_CONTRACT.md`](../benchmarks/TMC_ANDROID_BASELINE_PHASE1_CONTRACT.md)
- Android security tests: `python -m pytest tests/security/android -q`
- AVD runners and app fixtures: `benchmark/run_tmc_android_*_avd.py`, `scripts/build_tmc_android_*_baseline.ps1`, and `benchmarks/android_*_app/`
- Human- and machine-readable framework report/index: linked above; raw records and closure files remain under `reports/evidence/`.

## Claim ceiling

The evidence is limited to the declared Pixel_7 Android 34 x86_64 AVD paths and their specific application-runtime or framework fixtures. The 2/4/8 series is descriptive, not a scalability law or causal attribution. The work does not establish Android-wide or OS-wide enforcement, general Binder/SELinux properties, physical-device performance or energy behavior, or product-wide mobile security guarantees. Frozen T4–T20 canonical artifacts are not modified by this addendum.

The associated manuscript is the v2.0.1 Zenodo preprint, submitted to IEEE Transactions on Mobile Computing: <https://doi.org/10.5281/zenodo.22913070>.
