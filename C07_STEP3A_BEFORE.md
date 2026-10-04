# C07 Step 3-A Before

## Current Bypass Implementation

### Line 151 — Bypass source expression

`python
bypass_guard = (os.environ.get("BYPASS_GUARD", "false").lower() == "true") or (request.headers.get("X-Bypass-Guard", "false").lower() == "true")
`

**Two sources, OR semantics:**
1. BYPASS_GUARD environment variable (container env, subprocess env)
2. X-Bypass-Guard HTTP request header (any untrusted caller)

### Line 154-160 — Decision effect

`python
if bypass_guard:
    decision = "bypass"
    policy_id = "DROS-POL-BYPASS"
    rule_desc = "DROS Guard BYPASSED for Control Group Experiment"
    reason = "WARNING: Guard disabled. Attack payload passed directly to target system."
    defense_layer = "L0_CONTROL_GROUP"
    status_code = 200
`

Bypass completely skips PRECOMPILED_POLICY_INDEX lookup.

### Line 241-242 — Forwarding / privilege effect

`python
if agent_role == "ciso-agent" or bypass_guard:
    headers["X-Privileged-Token"] = "ERP-ADMIN-TOKEN-999"
`

Bypass triggers privileged token injection to downstream ERP.

### Audit effect

Audit records decision="bypass", policy_id="DROS-POL-BYPASS", defense_layer="L0_CONTROL_GROUP".

## Security Problem

Any untrusted HTTP caller can set X-Bypass-Guard: true and:
1. Skip all policy evaluation
2. Obtain 200 response for any endpoint
3. Trigger privileged downstream token injection
4. Access confidential finance data via ERP mock

Confirmed live in C07 Attack A.
