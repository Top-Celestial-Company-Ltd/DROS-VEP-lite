# Android Framework Baseline Evidence Index

Status: **CLOSED — declared Phase 1 framework-baseline set complete**

Target: `Pixel_7` AVD / Android 34 / `x86_64` / `emulator-5554`.

This aggregate index closes the declared comparative baseline set. It does
not modify the frozen DROS Android Phase 1–2 index or any T4–T20 canonical
artifact.

## Evidence map

| Baseline | Authority substrate | Artifact | Status | Evidence ceiling |
|---|---|---|---|---|
| `ANDROID-PERM-01` | Android native `READ_CONTACTS` permission manager | `reports/evidence/tmc_android_permission_baseline/20260923T1R4/` | Verified | Declared application-runtime permission path only |
| `ANDROID-APPOPS-01` | Android native `READ_CONTACTS` AppOps manager | `reports/evidence/tmc_android_appops_baseline/20260923T1R3/` | Verified | Declared AppOps application-runtime path only |
| `ANDROID-BINDER-01` | Protected exported Binder service with declared runtime permission | `reports/evidence/tmc_android_binder_baseline/20260923T1R4/` | Verified | Declared protected Binder service path only |
| `ANDROID-SELINUX-01` | SELinux enforcing-mode and app-context observation | `reports/evidence/tmc_android_selinux_baseline/20260923T1/` | Observed, not canonical | Enforcing mode/context observation; no isolated denial attribution |

## Controlled framework observations

- Native permission: revoked → `DENY` with no execution/effect; granted →
  `ALLOW` with bounded ContactsProvider effect.
- AppOps: permission granted plus AppOps deny → `DENY`; AppOps allow →
  `ALLOW` with bounded provider effect.
- Binder service: service permission revoked → `DENY` with no service-side
  effect; granted → `ALLOW` with completed transaction and independent
  `effects.jsonl` marker.
- SELinux: the declared AVD reported `Enforcing` and the app ran in the
  `untrusted_app` domain; no app-specific AVC denial was attributed.

## Reproducibility closure

The machine-readable closure index is stored beside this document in
`ANDROID_FRAMEWORK_BASELINE_INDEX.json`. It records artifact references,
closure status, selected SHA-256 hashes, and evidence ceilings. The raw
artifacts remain in their original baseline directories.

## Explicit non-claims

This closure does not establish Android-wide security, Binder-framework-wide
security, kernel enforcement, SELinux causal enforcement for the fixture,
physical-device behavior, energy consumption, scalability, or equivalence
between Android framework mechanisms and DROS execution governance.
