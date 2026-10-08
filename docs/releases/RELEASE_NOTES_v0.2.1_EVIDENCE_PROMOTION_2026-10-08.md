# Release Notes — DROS-VEP 2.0 Runtime Evidence Promotion (2026-10-08)

**Release Baseline:** `d5f63bf0b9536c3ab8bf4ec777688b3311cc9894` (PR #3)  
**Associated Promotion Commit:** `319df9916f52f8cfb66b8520769288a63fc47ac9`  
**Governance Protocol:** RFC-010 Open VEP / Strict Epistemic Conformance  

---

## 1. Summary of Promoted Evidence

This public release incorporates the complete, reproducible 2026-10-08 runtime evidence package into the authoritative public tree under `docs/evidence/runtime-recovery-2026-10-08/`.

### Verified Metrics
1. **RCU Policy Hot-Swap (`01-RCU`)**:
   - Total reader observations: 7,428
   - Total swaps executed: 5
   - Observed torn reads: 0
   - Average atomic publication latency: **1.96 µs** (shadow table preparation 2.69 µs ~ 3.99 µs).
2. **M5 Runtime Enforcement (`02-M5`)**:
   - 6/6 controlled authorization test cases matched expected decisions and downstream Mock ERP effects.
3. **PDP Microbenchmark (`03-PDP`)**:
   - Sample size: 100,000 queries
   - P50: **730 ns** | P95: 947 ns | P99: **1,223 ns** | P99.9: 1,354 ns | Max: 13,482 ns
   - Measurement boundary: pure policy evaluation loop (zero socket/HTTP/disk I/O).
4. **PGM 24-Hour Continuous Run (`04-PGM-24H`)**:
   - Observation count: 268,120 consecutive events
   - Errors: 0 | Timeouts: 0 | Process crashes: 0
   - Internal PDP Latency: P50 = **18.99 µs**, P99 = **47.78 µs**
   - End-to-End Client Latency: P50 = 4.38 ms, P99 = 10.41 ms

---

## 2. Updated Authoritative Documents
- `docs/whitepapers/DROS_AgenticWeb_Defense_Whitepaper_CN.md`
- `docs/whitepapers/DROS_AgenticWeb_Defense_Whitepaper_EN.md`
- `docs/evidence/runtime-recovery-2026-10-08/RUNTIME_EVIDENCE_INDEX.md`
- `docs/evidence/runtime-recovery-2026-10-08/governance/FINAL_CLAIM_RECONCILIATION.md`

---

## 3. Strict Boundary Disclosures
- Historical reported benchmark figures (`420 ns`, `555.4 ns`, `800 ns`, `160,611`) are preserved as `HISTORICAL_REPORTED_RESULT` and are not replaced.
- Complete mediation against all arbitrary OS syscall bypasses remains **NOT_PROVEN**.
- PX4 UAV S2-D perimeter containment remains **NOT_PROVEN**.
