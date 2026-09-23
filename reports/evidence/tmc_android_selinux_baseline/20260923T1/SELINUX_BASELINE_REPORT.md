# ANDROID-SELINUX-01 — SELinux Environment Baseline

## Observed configuration

- AVD: `Pixel_7`
- Android API: `34`
- ABI: `x86_64`
- `getenforce`: `Enforcing`
- DROS baseline app process context: `u:r:untrusted_app:s0:c191,c256,c512,c768`
- Security patch property observed: `2023-09-05`
- App-specific AVC matches in the captured log: none

## Evidence classification

This slice is **observational, not canonical security-effect evidence**. It
records that the declared AVD runs in enforcing mode and that the application
process runs in the `untrusted_app` SELinux domain. The captured generic AVC
records belong to other system components and are not attributed to the DROS
baseline app.

The result does not establish that SELinux alone caused any application
denial, nor does it establish Android-wide, Binder, kernel, or cross-device
security properties. A targeted SELinux denial experiment would require a
controlled policy/resource pair and independent AVC correlation.
