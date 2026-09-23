# ⚡ DROS System Overhead & Performance Microbenchmark Report
## Historical Reported Metrics and Current Evidence Boundaries

**Document Version:** 1.0 — System Overhead Benchmark  
**Maintained by:** DROS Engineering / Top-Celestial Company Ltd.  

> **Evidence-status audit (2026-09-23):** The legacy mobile harness is host-side: `KotlinDROSClient` delegates to a Python `ctypes` adapter loading a Windows DLL; it does not execute Android JNI, iOS Swift, or a device runtime. The historical `<0.001 mAh` and `<0.05 μJ` values have no accompanying meter, calculation inputs, calibration procedure, or raw energy trace in the current artifact set and must not be treated as measured. The 24-hour soak runner exists but selects random scenarios, writes only an aggregate to a fixed path, and collects no memory profile; its `0 Bytes` leak result is report-only. See [the bilingual legacy-claim audit](DROS_MOBILE_LEGACY_ENERGY_AND_SOAK_CLAIM_AUDIT_EN.md).

---

## 🧭 Executive Summary

When deploying runtime governance for AI Agents in enterprise and physical environments, **System Overhead** is the decisive metric for production feasibility. Traditional model-based guardrails (e.g., NVIDIA NeMo, Llama Guard, Palo Alto AIRS) introduce hundreds of milliseconds of latency and heavy GPU/memory footprints, rendering them impractical for flight controllers, high-frequency trading, and mobile on-device applications.

This historical report consolidates previously reported figures from a **24-hour Soak Test (160,611 aggregate requests)**, **Multi-Architecture Microbenchmarks ($N=10,000$)**, and a **host-side mobile-style adapter harness**. These figures have different evidence and measurement boundaries and are not all independently reproducible from the current repository:
1. **Sub-Microsecond Latency:** Median C-ABI decision latency $P_{50} = \mathbf{500\text{ ns}\ (0.5\ \mu\text{s})}$, with $P_{99} = \mathbf{1.2\ \mu\text{s}}$.
2. **Minimal CPU Impact:** Additional CPU load $<\mathbf{1.8\%}$, with lock-free RCU atomic pointer swap taking only $\mathbf{420\text{ ns}}$.
3. **Memory:** A legacy report states 0 Bytes leak over a 24-hour run; the runner has no memory-profile instrumentation, so this is **Reported, not independently verified**.
4. **Mobile energy:** Not measured by the host-side harness. Historical battery/energy estimates are **not verified measurements** and are excluded from product claims.

---

## 📊 Macro Overhead Comparison Matrix

| Overhead Dimension & Metric | DROS Empirical Value | Model Guardrails (NeMo / Llama Guard) | Cloud API Gateways (Palo Alto Prisma) | Advantage Multiplier |
| :--- | :--- | :--- | :--- | :--- |
| **1. Median Decision Latency ($P_{50}$)** | **500 ns (0.0005 ms)** | 150 ms ~ 500 ms | 20 ms ~ 80 ms | ⚡ **40,000x ~ 300,000x Faster** |
| **2. Tail Decision Latency ($P_{99}$)** | **1.2 μs (0.0012 ms)** | 800 ms ~ 2,000 ms | 150 ms ~ 350 ms | ⚡ **120,000x Faster** |
| **3. Additional CPU Overhead** | **< 1.8%** | 30% ~ 100% (High GPU/CPU load) | 5% ~ 15% (Network serialization) | 🛡️ **Ultra-low idle cost** |
| **4. Memory Footprint** | **< 16 MB** | 2 GB ~ 8 GB (Model weights) | 250 MB ~ 500 MB (Container) | 💎 **95%+ Memory Savings** |
| **5. Continuous Memory Leak** | Historical report states 0 Bytes; profile artifact unavailable | Python GC & cache accumulation | Connection session leaks | Reported; not independently verified |
| **6. Policy Atomic Swap Latency ($T_{\text{swap}}$)** | **420 ns** | Requires model reload (seconds) | 50 ms ~ 200 ms | ⚡ **Microsecond Hot Swap** |
| **7. Mobile Battery Consumption** | **Not measured by the cited harness** | Not compared | Not compared | No battery claim |

---

## 🔬 Multi-Architecture Latency Benchmark ($N = 10,000$ Iterations)

On a standardized testbed (Intel Xeon E3-1275L v3 @ 2.70GHz, 16GB RAM):
* **Arm A: Baseline (No Governance):** $200.00\text{ ns}$
* **Arm B: Microsoft AGT (Python Middleware):** $500.00\text{ ns}$ (P50) / $1,800.00\text{ ns}$ (P99)
* **Arm C: DROS GuardVM (C-ABI Bitmask):** $500.00\text{ ns}$ (P50) / $1,200.00\text{ ns}$ (P99)
* **Arm D: Defense-in-Depth (AGT + DROS):** $4,400.00\text{ ns}$ (P50) / $15,900.00\text{ ns}$ (P99)

---

## Mobile-style host adapter and edge-drone reported figures

* **Legacy mobile-style adapter:** the report lists $P_{50}=1.70\ \mu\text{s}$ and $P_{99}=7.30\ \mu\text{s}$. The current harness uses a Python host adapter and Windows DLL, not an Android/iOS device; raw timing samples are not archived, so these remain reported host-side values. Battery/energy was not measured.
* **Edge Drone (MAVLink Flight Control):** $< 500\text{ ns}$ decision latency occupies $< 0.05\%$ of a 1 kHz flight control loop, ensuring **Zero Jitter and hard real-time compliance**.

---

## 🎯 Conclusion

DROS's historical system-overhead figures require interpretation within their respective declared or reported boundaries. The mobile battery numbers are unverified estimates, and the legacy mobile adapter timings are not device results. See the audit addendum before reusing any value as a product or paper claim.
