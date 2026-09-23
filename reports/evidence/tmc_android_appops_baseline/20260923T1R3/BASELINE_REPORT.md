# ANDROID-APPOPS-01 — Native AppOps READ_CONTACTS Baseline

## Target

- AVD: `Pixel_7`
- Android: API 34
- ABI: `x86_64`
- Device: `emulator-5554`
- APK: `io.dros.tmc.appopsbaseline`
- APK SHA-256: `8104c7c0e8346d845e31187fa80b2a14ae700948001b29748ba799c6f4e6b1ef`

## Controlled pair

`READ_CONTACTS` was granted to the app in both phases. The only authority
state change was Android's native AppOps mode:

| Phase | AppOps state | Decision | Execution | Effect |
|---|---|---|---|---|
| DENY | `READ_CONTACTS=deny` | `DENY` | not started / not completed | `NONE`; no effect marker |
| ALLOW | `READ_CONTACTS=allow` | `ALLOW` | started / completed | bounded AppOps ContactsProvider marker |

The ALLOW phase observed zero contact rows on the declared AVD, but the
AppOps-mediated provider query completed and emitted the bounded fixture
effect marker.

## Evidence boundary

This is a native Android AppOps baseline on the declared Pixel_7 API 34
application-runtime path. It does not establish Android-wide security,
SELinux behavior, Binder behavior, kernel enforcement, physical-device
behavior, or equivalence to the DROS execution boundary.

## Provenance

- `T1` is retained as the initial AppOps runner failure provenance because the
  first implementation could not attribute AppOps denial separately from the
  permission check.
- `T1R2` is retained as corrected attribution provenance.
- `T1R3` is the first clean closure candidate with substrate-specific result
  labels and all seven checks passing.
