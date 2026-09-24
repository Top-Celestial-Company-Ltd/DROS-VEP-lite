# Claim Boundary — DROS Drone Extension

## Disallowed claims (never publish these, regardless of test results)

- "全球第一個 Drone AI Governance" / "world's first drone AI governance"
- "世界上唯一的 Drone Governance" / "the only drone governance system"
- "完整保護所有無人機" / "fully protects all drones"
- "可以防止所有 UAV 攻擊" / "prevents all UAV attacks"
- "符合航空安全認證" / "meets aviation safety certification"
- "DO-178C certified"
- "SORA compliant"
- "Complete Mediation of the entire drone"
- "DROS 可以保證飛行安全" / "DROS guarantees flight safety"
- "DROS is proven safe for real-world autonomous drone operations" (disallowed unless and until real-world operational evidence exists, which this plan does not currently produce)

Note: sparse public prior art is not evidence of "first" — see plan v0.3 §1.1. Adjacent public work exists (autonomous drone mission governance, MAVLink/PX4-focused robotics governance, MAVLink AI drone safety layers); DROS's public positioning should rest on verifiable, evidence-linked differences, not on claimed scarcity of competitors.

## Approved claim language templates

**If only SITL is complete:**
> The reference implementation is publicly installable and executable against PX4 SITL.

**If HIL is complete:**
> The reference implementation has additionally been evaluated against a physical flight-controller execution path under the documented test conditions.

**General framing:**
> DROS-VEP includes a public drone governance extension demonstrating how deterministic AI execution governance can be integrated with a PX4/MAVLink-based autonomous drone execution stack.

**Boundary statement (include with any public claim):**
> DROS governs only execution paths for which an enforceable policy enforcement point exists and whose mediation boundary has been explicitly identified and tested. Any unmediated execution path remains outside the proven governance boundary and must be reported as NOT PROVEN.

## Status classification (use these five values only)

`PROVEN` / `PARTIALLY_PROVEN` / `NOT_PROVEN` / `FAILED` / `NOT_APPLICABLE`

Do not write "implemented" where the correct word is "proven." Do not write "SITL passed" where the correct phrase is "real drone proven." Do not write "MAVLink path protected" where the correct phrase is "entire drone execution protected" — these are different claims with different evidence requirements.

## Stop conditions that affect claims

If a bypass is found (STOP-01), it must be documented and classified `NOT_PROVEN` / `BYPASS` publicly — not hidden. If physical safety behavior is undefined (STOP-02), physical testing halts until an architecture decision is recorded in `../DRONE_SAFETY_DEGRADATION_MATRIX.md`. See plan v0.3 §44 for the full stop-condition list.
