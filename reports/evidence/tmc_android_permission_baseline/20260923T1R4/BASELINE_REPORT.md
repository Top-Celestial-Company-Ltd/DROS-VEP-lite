# ANDROID-PERM-01 — Native READ_CONTACTS Permission Baseline

## Target

- AVD: `Pixel_7`
- Android: API 34
- ABI: `x86_64`
- Device: `emulator-5554`
- APK: `io.dros.tmc.permissionbaseline`
- APK SHA-256: `87139e56bb922cde4a22736404b3d45022cb915d3ccacab2e2a472dacd935fcb`

## Controlled pair

The same APK and bounded content-provider fixture were exercised twice. The
only authority-state change was Android's native `READ_CONTACTS` permission.

| Phase | Native permission state | Decision | Execution | Effect |
|---|---|---|---|---|
| DENY | revoked | `DENY` | not started / not completed | `NONE`; no effect marker |
| ALLOW | granted | `ALLOW` | started / completed | bounded contacts-provider query marker |

The ALLOW phase observed zero contact rows on the declared AVD, but the
permission-mediated provider query completed and emitted the bounded fixture
effect marker.

## Evidence boundary

This is a native Android permission baseline on the declared Pixel_7 API 34
application-runtime path. It does not establish Android-wide security,
SELinux behavior, Binder behavior, kernel enforcement, or equivalence to the
DROS execution boundary. No latency, scalability, energy, or causal runtime
claim is made by this slice.

## Provenance

- `T1`, `T1R2`, and `T1R3` are retained as runner failure provenance; they are
  not canonical evidence.
- `T1R4` is the first clean closure candidate and passed all nine declared
  checks.
