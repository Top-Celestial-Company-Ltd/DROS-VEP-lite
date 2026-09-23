# ANDROID-BINDER-01 — Protected Binder Service Baseline

## Target

- AVD: `Pixel_7`
- Android: API 34
- ABI: `x86_64`
- Device: `emulator-5554`
- Service APK SHA-256: `56a3ac869a3294749201ccc41b3c02fbbaf14ed07e6ac4ee30f4415e03b2fdea`
- Client APK SHA-256: `1c96bae4f2850cf3d26b9666e27ca526945a79ca56c240bdcd3a5a848535b8ff`

## Controlled pair

The client invoked the same exported Android Binder service in two clean
install phases. The only authority-state change was the declared runtime
permission protecting the service endpoint.

| Phase | Service permission | Decision | Execution | Effect |
|---|---|---|---|---|
| DENY | revoked | `DENY` | not started / not completed | `NONE`; no service effect record |
| ALLOW | granted | `ALLOW` | started / completed | bounded Binder fixture record present |

The service-side `effects.jsonl` file is the independent bounded-effect
marker; the result JSON is not treated as sufficient evidence by itself.

## Evidence boundary

This is a native Android protected-service/Binder application-runtime
baseline on the declared Pixel_7 API 34 x86_64 path. It does not establish
Binder framework-wide security, Android-wide security, kernel enforcement,
SELinux behavior, physical-device behavior, or equivalence to the DROS
execution boundary.

## Provenance

- `T1` is retained as failure provenance: a client result was missing because
  the first APK omitted inner classes from the DEX input.
- `T1R2` is retained as failure provenance: the initial signature permission
  was automatically granted to the same debug-signed client and could not be
  changed with `pm grant/revoke`.
- `T1R3` is retained as failure provenance: an APK update preserved the prior
  permission state, so the nominal DENY phase observed ALLOW.
- `T1R4` is the first clean closure candidate with uninstall/reinstall state
  reset, both controlled outcomes, and all checks passing.
