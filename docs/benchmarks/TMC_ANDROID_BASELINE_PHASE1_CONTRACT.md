# TMC Android Baseline Phase 1 Contract

<!-- dros_component: dros-academic-paper-tmc -->
<!-- source_component: dros-vep-lite -->
<!-- status: ANDROID SECURITY SEMANTICS CLOSED / BASE-06 MEASUREMENT CONTRACT FROZEN -->
<!-- target: Pixel_7 AVD / Android 34 / x86_64 -->

## 1. Scope decision

This phase establishes a reproducible Android runtime execution baseline that can be compared with VEP post-compromise experiments. It does **not** claim Android-wide security enforcement.

### In scope

- Existing `Pixel_7` AVD;
- Android 34, `google_apis_playstore`, x86_64 system image;
- ADB-controlled execution and artifact collection;
- One minimal Android app/harness with an explicitly bounded action interface;
- Normal, authorized, unauthorized, compromised-agent simulation, and revocation paths;
- Request-level decision latency, P50/P95/P99, throughput, CPU and memory observations;
- Versioned workload, policy, request corpus, raw result and environment manifest.

### Explicitly out of scope

- Physical-device battery or power-meter claims;
- `<0.001 mAh` or other energy claims;
- Android kernel modification;
- SELinux policy modification;
- Binder framework modification;
- iOS or multi-device generalization;
- Android OS-wide privacy-permission enforcement;
- Any claim that the AVD represents all Android devices.

## 2. Experimental target and provenance

| Field | Frozen target |
| :--- | :--- |
| AVD | `Pixel_7` |
| Android API | 34 |
| Image | `google_apis_playstore` / `x86_64` |
| ADB | `E:\Android\Sdk\platform-tools\adb.exe` |
| Emulator | `E:\Android\Sdk\emulator\emulator.exe` |
| NDK candidates | 21.4.7075529, 25.2.9519653, 26.1.10909125; exact version pending contract implementation choice |
| Target identity | Experimental target only; no full-platform representativeness claim |
| Existing VEP link | M5.1 `EXP-1789532251-38a4fd` is a general cross-substrate reference, not an Android OS baseline |

The final run must record API level, build fingerprint, kernel version, ABI, AVD name, emulator arguments, ADB version, app APK hash, policy hash, workload hash, VEP commit and clock/measurement boundary.

## 3. Required workload paths

Each path uses the same request schema and action corpus. A path result must distinguish `decision`, `execution_started`, `execution_completed`, and `execution_effect`.

| Path ID | Scenario | Expected observation |
| :--- | :--- | :--- |
| `ANDROID-BASE-01` | Normal execution | A valid request reaches the bounded app action and records a completed effect. |
| `ANDROID-BASE-02` | Compromised-agent simulation | The simulated compromised agent can issue requests, but cannot alter the independently loaded policy or authority state. |
| `ANDROID-BASE-03` | Authorized execution | A request with the declared capability is allowed and produces the declared bounded effect. |
| `ANDROID-BASE-04` | Unauthorized execution | A request outside the capability set is denied before the bounded effect. |
| `ANDROID-BASE-05` | Revocation | A previously valid request is allowed before revocation and denied after revocation. |
| `ANDROID-BASE-06` | Measurement | Request-level timing and resource observations are emitted without being confused with physical energy measurement. |

## 4. Proposed public seams for TDD confirmation

The following seams are proposed for the first red slice. Tests must observe these interfaces rather than Android implementation internals.

### 4.1 Host-side baseline controller

Proposed interface: `AndroidBaselineController`

- `build_or_locate_apk()`
- `install(apk)`
- `launch()`
- `reset_state()`
- `submit(request)`
- `revoke(authority_id)`
- `collect_result()`
- `collect_environment_manifest()`

The controller is responsible for ADB orchestration and artifact capture. It must not make authorization decisions itself.

### 4.2 App-side action boundary

Proposed request shape:

```json
{
  "request_id": "ANDROID-BASE-04-000001",
  "principal": "compromised-agent",
  "action": "READ_CONTACTS",
  "capability": "CAP_CONTACTS",
  "policy_version": "sha256:...",
  "revocation_epoch": 0,
  "arguments_hash": "sha256:..."
}
```

Proposed result shape:

```json
{
  "request_id": "ANDROID-BASE-04-000001",
  "decision": "DENY",
  "execution_started": false,
  "execution_completed": false,
  "execution_effect": "NONE",
  "reason": "CAPABILITY_MISSING",
  "decision_latency_ns": 0,
  "app_elapsed_ns": 0,
  "policy_hash": "sha256:..."
}
```

The exact action effect must be a bounded test fixture, not a claim of OS-wide permission control. Any Android permission prompt or framework behavior must be recorded separately from the DROS decision.

## 5. Measurement contract

### 5.1 Required metrics

- Request-level decision latency;
- App-observed elapsed time;
- P50, P95 and P99 for the first phase;
- Throughput under a declared serial/concurrency configuration;
- CPU and memory observations with tool/version and sampling interval;
- Counts of allowed, denied, execution-started, execution-completed and unexpected effects.

### 5.2 Measurement boundaries

The following must never be conflated:

1. DROS decision latency;
2. ADB transport latency;
3. Android app IPC/UI/framework latency;
4. Action fixture execution latency;
5. physical energy or battery consumption.

Phase 1 excludes item 5. No energy number may be emitted as an experimental result in this phase.

### 5.3 Repetition and warm-up

The contract implementation must define before execution:

- warm-up count;
- sample count per path;
- serial versus concurrent mode;
- emulator cold-boot versus warm-boot state;
- background process and animation settings;
- outlier handling and percentile algorithm;
- app reset and revocation reset procedure.

### 5.4 BASE-06 decision-latency slice: frozen parameters

The first measurement slice is frozen before benchmark execution and measures
only the app-observed `request -> authorization decision` interval reported by
`decision_latency_ns`. ADB command/transport time, Android Activity launch
time outside the app timer, fixture execution, and physical energy are not
included.

| Parameter | Frozen value |
| :--- | :--- |
| Warm-up count | `10` requests; excluded from all reported statistics |
| Measured sample count | `100` requests |
| Serial/concurrency mode | Serial, one request in flight |
| AVD state | Warm AVD; device must be boot-complete before runner invocation |
| Background/animation configuration | No benchmark-induced changes; record the declared device state in `environment.json` and keep the run single-purpose |
| Percentile algorithm | Nearest-rank over sorted integer nanoseconds: `rank = ceil(p * n)`, clamped to `[1, n]` |
| Reset procedure | Clear the app package once before warm-up; no reset between measured samples; use unauthorized `CAP_CAMERA` for `READ_CONTACTS` so the fixture cannot create effects |

Each measured sample must be emitted to `results.jsonl` with its request ID,
decision result, `decision_latency_ns`, `app_elapsed_ns`, and the exact request
boundary fields. `summary.json` is derived only by the analysis script from
that raw file and must be reconstructable without rerunning the AVD.

### 5.5 First concurrency slice: frozen parameters

The first concurrency slice changes only the number of in-flight DENY
requests. It does not modify T4, T5, T7, T9, or T10, and it does not make a
causal claim about Android scheduling or framework behavior.

| Parameter | Frozen value |
| :--- | :--- |
| Workload | `READ_CONTACTS` with invalid `CAP_CAMERA`; expected `DENY`, no execution, no effect |
| Concurrency levels | `C1=2`, `C2=4`, `C3=8` |
| Requests per level | `100` measured requests after `10` serial warm-up requests |
| Dispatch mode | Fixed-size waves of at most the declared concurrency; one request per worker |
| AVD state | Warm AVD; one package clear before each level's warm-up |
| Primary observations | completed/denied/error counts, end-to-end batch throughput, app-observed decision latency P50/P95/P99 |
| Invariant gate | Every completed request must be `DENY`, not started, not completed, and `NONE` effect |

Throughput is reported as host-observed wave workload throughput and is kept
separate from the app-observed decision-latency boundary. ALLOW concurrency is
reserved for a later controlled slice.

### 5.6 Ingress seam closure before concurrency

Because T11/T12 showed that concurrent Activity launch did not provide a
complete request/result pairing, concurrency measurement is gated on a
separate app-side ingress invariant. The first green slice submits two request
IDs through an explicit `BroadcastReceiver` and checks that the app writes one
`RECEIVED` record for each ID to `ingress_records.jsonl`. Record order is not
treated as semantic. No authorization or execution decision is made in this
slice.

## 6. Required artifacts

Each run must produce a self-contained evidence directory containing:

- `environment.json`;
- `avd_config.txt` or equivalent AVD manifest;
- `adb_version.txt`;
- APK and native library SHA-256 values;
- policy and workload hashes;
- request-level `results.jsonl`;
- `summary.json` with counts and percentiles;
- raw `logcat` capture;
- controller command/configuration;
- analysis script and version;
- exit status and failure classification.

## 7. Release and claim gates

The Android Phase 1 result may be labeled `Verified` only when the run has all required artifacts and the six paths have independently checkable outcomes. Otherwise use `Partially Verified`, `Reported`, `Needs Artifact Verification`, or `Not Yet Tested`.

Even after a successful Phase 1 run, the permitted claim ceiling is:

> DROS-Mobile was evaluated on a reproducible Pixel_7 AVD configuration running Android 34 x86_64 under the declared application-level execution boundary.

The result does not establish Android-wide, kernel-level, SELinux-level, Binder-level, physical-device, battery, or cross-device security properties.

## 11. BASE-06 decision-latency status

The first measurement slice is closed for the declared app-observed boundary.
Canonical artifact: `reports/evidence/tmc_android_base_06_avd/20260922T9/`.

The run used the frozen parameters in Section 5.4: 10 warm-up requests, 100
serial measured requests, a warm `Pixel_7` AVD, nearest-rank percentiles, and a
single package clear before warm-up. All 100 requests were unauthorized
`READ_CONTACTS` requests with `CAP_CAMERA`; all returned `DENY`, with no started
or completed execution and no fixture effect.

The raw `results.jsonl` was independently passed through
`benchmark/analyze_tmc_android_base_06.py` and reproduced the recorded
`summary.json` exactly. The observed decision-latency percentiles for this run
were P50 `1,200,200 ns`, P95 `21,970,600 ns`, and P99 `89,285,200 ns`.

These are app-observed measurements for this declared warm AVD run only. They
do not include or characterize ADB transport, Activity/framework launch,
fixture execution, CPU, memory, throughput, energy, physical devices, or
Android-wide behavior.

### 11.2 BASE-06-ALLOW controlled pair

`ANDROID-BASE-06-ALLOW` was measured with the same frozen parameters and
declared target as T9, changing only the capability from invalid `CAP_CAMERA`
to valid `CAP_CONTACTS`. Canonical artifact:
`reports/evidence/tmc_android_base_06_allow_avd/20260922T10/`.

All 100 measured requests returned `ALLOW`, started and completed the bounded
fixture, and produced 100 measured effects (110 including warm-up). The
app-observed decision latency was P50 `1,122,300 ns`, P95 `7,453,500 ns`, and
P99 `27,274,000 ns`. Raw-to-summary reconstruction passed, and the T9/T10
artifacts share the same AVD target, APK hash, environment manifest, and
measurement parameters.

This is a controlled DENY/ALLOW decision-path pair, not an Android enforcement
overhead benchmark. The timing boundary and non-claims in Section 11.1 remain
unchanged.

### 11.3 Decision-path measurement closure

T9 and T10 are frozen as one aggregate controlled evidence unit:
`reports/evidence/tmc_android_base_06_decision_path/20260922T_PAIR_CLOSED/`.
The aggregate verifies target identity, APK and environment identity, frozen
measurement parameters, equal sample counts, and independent raw-to-summary
reconstruction. It records the latency-distribution difference as an
observation only; the current instrumentation does not establish its runtime
cause.

## 12. Concurrency ingress status

T11/T12 remain failure provenance: concurrent Activity launch lost a request
result and therefore did not produce canonical concurrency evidence. The first
canonical ingress seam artifact is T14:
`reports/evidence/tmc_android_ingress_avd/20260922T14/`.

T14 verified `2 submitted == 2 app-observed RECEIVED records` through the
explicit Android BroadcastReceiver seam. This closes ingress accounting only;
queue dispatch, action execution, concurrency latency, throughput, and higher
concurrency levels remain open.

The first C1 pipeline slice is T15:
`reports/evidence/tmc_android_c1_avd/20260922T15/`.
It verified `2 submitted == 2 received == 2 dispatched == 2 result` records,
with both results `DENY`, not started, not completed, and `NONE` effect. This
is pipeline accounting only; it does not close concurrency behavior or report
performance.

### 5.7 C1 performance slice: frozen parameters

The first performance run is limited to C1 (`2` concurrent requests) on the
same DENY workload used by the accounting slice. It reports only host-observed
pipeline throughput and app-observed dispatcher decision latency. The stage
accounting invariant remains a release gate.

| Parameter | Frozen value |
| :--- | :--- |
| Concurrency | `C1=2` |
| Workload | `READ_CONTACTS` with invalid `CAP_CAMERA`; expected `DENY`, no execution, no effect |
| Warm-up | `10` serial requests; excluded from reported metrics |
| Measured samples | `100` requests, fixed waves of two |
| Throughput boundary | Host wall-clock from measured submissions start through all measured broadcast calls returning; reported separately from app timing |
| Decision latency boundary | Dispatcher `request -> authorization result` interval recorded by `decision_latency_ns` |
| Percentiles | Nearest-rank P50/P95/P99 over measured result records |
| Release gate | `submitted = received = dispatched = result = 100`, all results satisfy DENY/no-start/no-complete/NONE |

The canonical C1 performance artifact is
`reports/evidence/tmc_android_c1_performance_avd/20260922T16/`. It records
P50/P95/P99 app decision latency of `715,700 / 1,879,400 / 3,494,200 ns` and
host-observed throughput of `15.773080638486732` requests/second for this one
declared run. These are observations under the frozen boundary, not
Android-wide performance or causal runtime explanations.

The C2 pipeline-accounting artifact is
`reports/evidence/tmc_android_c2_avd/20260922T17/`. It verified
`4 submitted == 4 received == 4 dispatched == 4 result`, with all four
requests preserving the DENY/no-start/no-complete/NONE invariant. C2
performance remains unstarted.

The canonical C2 performance artifact is
`reports/evidence/tmc_android_c2_performance_avd/20260922T18/`. With the same
workload and protocol as T16, C2 recorded P50/P95/P99 app decision latency of
`896,100 / 5,594,500 / 11,310,600 ns` and host-observed throughput of
`14.035331786330994` requests/second. Accounting remained `100/100/100/100`.
These are C2 observations only; no causal explanation of the T16/T18
difference is established.

The C3 pipeline-accounting artifact is
`reports/evidence/tmc_android_c3_avd/20260922T19/`. It verified
`8 submitted == 8 received == 8 dispatched == 8 result`, with all eight
requests preserving the DENY/no-start/no-complete/NONE invariant. C3
performance remains unstarted.

The canonical C3 performance artifact is
`reports/evidence/tmc_android_c3_performance_avd/20260922T20/`. With the same
workload and protocol as T16/T18, C3 recorded P50/P95/P99 app decision latency
of `859,100 / 6,492,900 / 21,480,700 ns` and host-observed throughput of
`16.506245492866505` requests/second. Accounting remained `100/100/100/100`.
Together with T16 and T18, this forms a descriptive 2/4/8-concurrency series
under the declared application-runtime boundary; it does not establish a
scaling law, saturation point, or runtime causality.

The aggregate Android evidence index is
`reports/evidence/tmc_android_phase1_2_index/20260922T_INDEX_CLOSED/`.

### 11.1 T9 tail characterization

The preserved T9 samples were analyzed without rerunning the experiment or
removing outliers. The derived artifact is
`reports/evidence/tmc_android_base_06_avd/20260922T9/tail_analysis.json`.
It records min/max, P50/P90/P95/P99, mean, bucket counts, top-10 tail samples,
and sample sequence positions. T9 does not contain raw timestamps or logcat,
so runtime-event correlation and causal attribution remain open.

## 9. Controlled allow/deny pair status

The first two Android slices now form a controlled pair on the same `Pixel_7` / Android 34 / x86_64 app-runtime path:

| Test | Authority state | Decision | Execution | Effect |
| :--- | :--- | :--- | :--- | :--- |
| `ANDROID-BASE-03` | Valid `CAP_CONTACTS` for `READ_CONTACTS` | `ALLOW` | Started and completed | `BOUNDED_FIXTURE` present |
| `ANDROID-BASE-04` | Invalid `CAP_CAMERA` for `READ_CONTACTS` | `DENY` | Not started | `NONE`, marker absent |

Canonical artifacts:

- BASE-03: `reports/evidence/tmc_android_base_03_avd/20260922T5/`
- BASE-04: `reports/evidence/tmc_android_base_04_avd/20260922T4/`

Both are verified only for the declared AVD app-runtime invariant and retain the same non-claims listed above.

## 10. Revocation lifecycle status

`ANDROID-BASE-05` extends the controlled pair into a bounded lifecycle without changing the execution fixture:

```text
valid authority → ALLOW → effect present
       ↓ revoke
same authority/request → DENY → not started → no new effect
```

Canonical artifact: `reports/evidence/tmc_android_base_05_avd/20260922T7/`.

The closure records `effect_count_before=1` and `effect_count_after=1`; the pre-revocation effect remains as history, but the post-revocation request creates no additional effect.

## 8. Red slice status

The public seams in Section 4 were confirmed. The first red test is:

`tests/security/android/test_android_base_04.py::test_android_base_04_denies_before_bounded_fixture_effect`

The targeted run fails at collection because `vep.android_baseline` does not yet exist:

```text
ModuleNotFoundError: No module named 'vep.android_baseline'
```

The minimal in-process reference seam now makes this test pass (`1 passed`). This green result verifies only the app-side bounded fixture invariant. It is not Android AVD evidence and does not establish Android framework or OS-level enforcement. No additional Android path may be implemented in the same slice.

The same request was subsequently executed through the real AVD path:

`Host Controller → ADB → Android Activity → app-side action boundary → fixture check`

Run artifact: `reports/evidence/tmc_android_base_04_avd/20260922T4/`

Observed result on `Pixel_7` / Android API 34 / x86_64:

```text
decision=DENY
reason=CAPABILITY_MISSING
execution_started=false
execution_completed=false
execution_effect=NONE
effect_marker_present=false
runner_exit=0
```

The run recorded an APK SHA-256, request/result/summary JSON, ADB version, device `getprop` output and the closure manifest `reports/evidence/tmc_android_base_04_avd/20260922T4/evidence_closure.json`. The recorded decision latency is an app-side diagnostic field only; this slice makes no performance claim.

Evidence ceiling for this slice:

- `Python seam`: authorization/execution ordering invariant;
- `Pixel_7 AVD`: the same invariant observed through the Android 34 x86_64 app runtime path;
- `Android OS`, SELinux, Binder, kernel and all-Android generalization: not established.
