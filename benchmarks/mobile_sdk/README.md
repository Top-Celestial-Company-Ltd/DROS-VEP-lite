# DROS Mobile SDK Policy Harness

This VEP module is a host-side policy fixture for mobile-agent threat scenarios. Its Python adapters load a host Windows DLL via `ctypes`; they emulate mobile-style request shapes but do not execute Android JNI, iOS Swift, or a physical-device runtime.

## Scenarios

The harness contains local assertions for photo/contact access, clipboard/OTP access, background location and microphone requests, and biometric-gated payment actions. These checks characterize the declared fixture only; they are not Android OS permission tests or mobile-platform security results.

## Run

```bash
python benchmarks/mobile_sdk/run_mobile_bench.py
```

## Evidence boundary

- Any P50/P99 printed by the legacy adapter is host-side wrapper timing, not on-device latency; raw timing samples are not archived by this runner.
- Battery, power, energy, and network-egress impact are **not measured** by this harness. Historical `<0.001 mAh` / `<0.05 μJ` values were unvalidated estimates and are not supported as measurements.
- For declared Pixel_7 Android 34 x86_64 application-runtime evidence, use the TMC indexes under `reports/evidence/tmc_android_phase1_2_index/` and `reports/evidence/tmc_android_framework_baselines/`.
