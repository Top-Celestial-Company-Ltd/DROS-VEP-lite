# Phase 5 / Step 3-D — Control-Plane Isolation

## STEP
Phase 5 / Step 3-D

## SCOPE
H2 only

## BEFORE_HEAD
c98f8a81818b2ef696992949388abdaa8cbb2236

## PRE_SHA256
324B147000DB05E3BE95434CD20D9A36741A8B838A719C1234673B6538BD9F80

## POST_SHA256
D0D71E3108CE97639573CBB00E212731FE308C9419E3028763EE2F2B5244C894

## FINDING
BYPASS_GUARD env remained as a local control input (already not reachable
by HTTP data-plane callers). Required explicit source-level classification
as control-plane/test-only.

## DATA_PLANE_EFFECT
X-Bypass-Guard = ineffective (per H1, confirmed)
All HTTP caller inputs to bypass = BLOCKED

## CONTROL_PLANE
BYPASS_GUARD environment variable, set via deployment config or
dashboard/control_center.py subprocess env. The dashboard sets env
in subprocess but it does NOT propagate to Guard container -- the
env path is deployment-time / local-only.

## TEST_ONLY
YES -- classified TEST_CONTROL_ONLY in source code

## HTTP_TO_BYPASS
BLOCKED (every path checked)

## CONTROL_TO_BYPASS
Available via deployment-time BYPASS_GUARD env or dashboard
subprocess env (though the subprocess path does not actually
reach the Guard container in standard Compose topology)

## H1
PASS / UNCHANGED

## H3
PASS / UNCHANGED

## H4
PASS / UNCHANGED

## H5
PASS / UNCHANGED

## H6
PASS / UNCHANGED

## PRIVILEGED_TOKEN
NOT REINTRODUCED

## PX4
NOT TOUCHED

## LIVE_EXECUTION
NOT EXECUTED

## DEPLOYMENT
NOT EXECUTED

## STATIC_VERIFICATION
- py_compile (guard + dashboard): PASS
- git diff --check: PASS
- X-Bypass-Guard header -> bypass: BLOCKED: PASS
- X-Agent-Role -> bypass: BLOCKED: PASS
- X-DROS-Identity-Token -> bypass: BLOCKED: PASS
- BYPASS_GUARD env -> bypass: TEST_CONTROL_ONLY: PASS
- Privileged token not reintroduced: PASS
- H1 intact: PASS
- H3 intact: PASS
- H4 intact: PASS
- H5 intact: PASS
- H6 intact: PASS
- VALID_ED25519 not reintroduced: PASS
- LOCAL_SELF_SIGN present: PASS
- principal_verified present: PASS
- identity_assertion_source present: PASS
