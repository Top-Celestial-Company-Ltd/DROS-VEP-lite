# Android Framework Baseline Test Report

## 1. Scope and target

This report documents the declared comparative Android framework baseline set
for DROS-Mobile. All runs used the same experimental target:

- Pixel_7 Android Virtual Device;
- Android API 34;
- x86_64 ABI;
- ADB transport;
- application-runtime fixtures with independently inspectable effect markers.

The baselines are comparison observations, not replacements for DROS and not
proof of Android-wide security. The declared set contains native permission,
AppOps, protected Binder service, and SELinux environment observation slices.

## 2. Evidence protocol

Each baseline was implemented as an independent fixture and runner. The
runner records the request, authority state, decision, execution-started and
execution-completed fields, and an effect marker owned by the fixture or
service. A result string alone is insufficient for closure. Clean candidates
were selected only after the runner could reproduce the expected deny/allow
or observational outcome from the stored artifacts.

Failed or contaminated attempts remain provenance history and are excluded
from canonical results. The aggregate machine-readable index records the
canonical paths and selected SHA-256 hashes.

## 3. Results

| Baseline | Authority state | Observed outcome | Evidence status |
|---|---|---|---|
| `ANDROID-PERM-01` | `READ_CONTACTS` revoked/granted | `DENY` with no execution/effect; `ALLOW` with bounded ContactsProvider effect | Verified |
| `ANDROID-APPOPS-01` | permission granted; AppOps deny/allow | `DENY` or `ALLOW` according to AppOps mode, with corresponding effect marker | Verified |
| `ANDROID-BINDER-01` | protected service permission revoked/granted | Binder bind denied without effect; transaction completed with service-side effect when granted | Verified |
| `ANDROID-SELINUX-01` | declared AVD policy/context observation | `getenforce=Enforcing`; app in `untrusted_app`; no app-specific AVC attribution | Observed, not canonical |

### 3.1 Native permission baseline

Artifact: `reports/evidence/tmc_android_permission_baseline/20260923T1R4/`.

The app declared `READ_CONTACTS` and used the Android permission-mediated
ContactsProvider path. With permission revoked, the app returned `DENY`, did
not start or complete the bounded action, and produced no fixture marker.
With permission granted, the provider query completed and emitted the
bounded permission-fixture marker. APK SHA-256:
`87139e56bb922cde4a22736404b3d45022cb915d3ccacab2e2a472dacd935fcb`.

### 3.2 AppOps baseline

Artifact: `reports/evidence/tmc_android_appops_baseline/20260923T1R3/`.

`READ_CONTACTS` remained granted in both phases. Only the native AppOps mode
changed. `READ_CONTACTS=deny` produced `DENY`, no execution, and no marker;
`READ_CONTACTS=allow` produced `ALLOW`, a completed bounded query, and a
marker. APK SHA-256:
`8104c7c0e8346d845e31187fa80b2a14ae700948001b29748ba799c6f4e6b1ef`.

### 3.3 Protected Binder service baseline

Artifact: `reports/evidence/tmc_android_binder_baseline/20260923T1R4/`.

The client called the same exported Binder service in two clean
uninstall/reinstall phases. With the declared service permission revoked,
the client recorded `DENY`, `execution_started=false`,
`execution_completed=false`, and no service-side `effects.jsonl` record.
With the permission granted, the Binder transaction completed and the
service independently recorded `BOUNDED_BINDER_FIXTURE`.

Service APK SHA-256:
`56a3ac869a3294749201ccc41b3c02fbbaf14ed07e6ac4ee30f4415e03b2fdea`.
Client APK SHA-256:
`1c96bae4f2850cf3d26b9666e27ca526945a79ca56c240bdcd3a5a848535b8ff`.

### 3.4 SELinux observation

Artifact: `reports/evidence/tmc_android_selinux_baseline/20260923T1/`.

The AVD reported enforcing mode and the DROS baseline process ran in an
`u:r:untrusted_app:s0` context. The captured generic AVC records were not
attributed to the DROS fixture, so this slice is observational only. It does
not show that SELinux caused an application denial.

## 4. Failure provenance

- Permission and AppOps early runner attempts are retained in their baseline
  directories and are not canonical when they lacked clean attribution or
  closure.
- Binder `T1` omitted Java inner classes from the DEX input.
- Binder `T1R2` used a same-signer signature permission that Android treated as
  non-changeable at runtime.
- Binder `T1R3` reused an installed package and therefore retained the prior
  permission grant. `T1R4` corrected this with clean uninstall/reinstall
  state reset.

## 5. Claim ceiling

The results support only the following bounded statement:

> On the declared Pixel_7 Android 34 x86_64 application-runtime target,
> native permission, AppOps, and a protected Binder-service path produced
> reproducible authority-dependent execution outcomes, while SELinux
> enforcing mode and app context were observed without causal denial
> attribution.

The report does not establish Android-wide security, Binder-framework-wide
security, kernel enforcement, physical-device energy behavior, scalability,
or equivalence between Android framework mechanisms and DROS execution
governance.
