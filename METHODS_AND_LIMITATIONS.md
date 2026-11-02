# Measurement Methods, Test Configurations, and Engineering Limitations

This document provides technical definitions, measurement methodologies, and hardware constraints corresponding to the empirical evaluations presented in the IEEE ICA 2026 paper (*DROS-6P*).

---

## 1. Measurement Methods and Statistical Definitions

### 1.1 High-Resolution Timestamping
- **Clock Source:** On Windows platforms, microbenchmarks utilize the Windows QueryPerformanceCounter (QPC) API via native Rust timing wrappers (`std::time::Instant`).
- **Nominal Resolution:** The observed QPC frequency corresponds to approximately 10 MHz (~100 ns nominal tick interval).
- **Quantization Artifacts:** Individual sub-100 ns execution primitives (such as isolated in-memory bitwise operations) cannot be reliably resolved and are not reported as standalone figures to avoid quantization distortion.

### 1.2 Quantile and Percentile Computation Convention
- **Order-Statistic Formula:** All reported percentiles ($p_{50}$, $p_{95}$, $p_{99}$) in the reload latency and microbenchmark evaluations use the harness's rounded order-statistic index:
  $$\text{Index}(p) = \text{round}\big(p \times (N - 1)\big)$$
  where array indices are zero-based ($0, \dots, N-1$).
- **Sample Sizes ($N$):**
  - Policy reload microbenchmarks (Claim M11): $N = 1,000$ per configuration.
    - $p_{50}$ index: $\text{round}(0.50 \times 999) = 500$ (501st sorted sample).
    - $p_{99}$ index: $\text{round}(0.99 \times 999) = 989$ (990th sorted sample).
  - Atomic pointer publication (Claim M12): $N = 10,000$ per reader concurrency level ($0, 1, 2, 4, 8$).
  - Decision cost microbenchmark T07 (Claim M18): $N = 20,000$ (concurrency 1, 5, 10); $N = 50,000$ (concurrency 25); $N = 100,000$ (concurrency 50). Published data is a summary quantile table; raw timing traces are held private.

---

## 2. Test Environments and Hardware Profiles

The experimental data published in this repository originate from bounded test harnesses executed on the following documented test configurations:

### 2.1 Configuration S2 (Reload, Atomic Publication, and Receiver Audit)
- **Host OS:** Windows 10 IoT Enterprise LTSC (x86-64).
- **Processor:** Intel Xeon E3-1275L v3 @ 2.70 GHz (4 cores / 8 threads).
- **Compiler Toolchain:** Rust `1.96.0` (release profile, optimizations enabled) / Go `1.22+` (Receiver harness).
- **Omitted Metrics:** System RAM capacity and CPU thermal throttling states were not systematically logged during this trial run.

### 2.2 Configuration Base (7-Gate Decision Baseline and T07)
- **Host OS:** Windows 10 IoT LTSC (x86-64).
- **Workload:** In-process closed-loop synthetic request generation (direct C-ABI invocation).
- **Revision Bloodline:** Base revision `1e680c61`.

### 2.3 Configuration Historical Soak (2,880 Rounds Sampling)
- **Host OS:** Ubuntu Linux 22.04 LTS (x86-64, Node 31).
- **Sampling Scheme:** Periodic scheduled execution (~30 s interval across ~86,372 s).

---

## 3. Engineering Boundaries and Test-Only Assumptions

### 3.1 Test-Only Feature Builds
- **Explicit Constraint:** All reported `ALLOW` outcomes originate from test-only build configurations compiled with permissive test keys and mocked fixture providers.
- **Production Guard:** The production-default build of DROS requires valid cryptographic credentials to initialize the authenticated path and fails closed without proper authentication.

### 3.2 Closed-Loop Latency Bounds
- **Microbenchmarks vs. End-to-End Overhead:** The reported T07 latencies ($p_{50} = 900\ \text{ns}$, $p_{99} = 1,900\ \text{ns}$) measure in-process C-ABI invocation and volatile ring buffer push under closed-loop conditions. They do not constitute ungoverned network end-to-end execution baselines.
- **Tail Latency Extremes:** Under high concurrency (50 threads), maximum observed single-invocation latencies reach up to 2.8 ms due to thread preemption and OS scheduling jitter; $N=20,000$ samples are insufficient to bound extreme tails ($\ge 99.99$th percentile).
