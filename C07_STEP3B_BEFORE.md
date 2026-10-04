# C07 Step 3-B Before

## Current Role / Privilege Path

### Line 144 — Role source
`python
agent_role = request.headers.get("X-Agent-Role", "unknown")
`
X-Agent-Role is a caller-controlled HTTP header. Any untrusted caller can set any value.

### Line 148 — Policy lookup
`python
lookup_key = (agent_role, full_path)
`
The role string is used directly as the policy lookup key. This is caller-asserted, not authenticated.

### Line 241-242 — Privileged token injection
`python
if agent_role == "ciso-agent" or bypass_guard:
    headers["X-Privileged-Token"] = "ERP-ADMIN-TOKEN-999"
`

**TWO caller-controlled paths to privileged authority:**
1. X-Agent-Role: ciso-agent from any untrusted HTTP caller → X-Privileged-Token injected
2. ypass_guard == true (env or, before Step 3-A, HTTP header) → X-Privileged-Token injected

Both paths bypass cryptographic verification and rely purely on caller-supplied values.

### Endpoint policy for ciso-agent (DROS_POLICIES)
ciso-agent has broad access: finance, secrets, deploy, payroll all explicitly allowed.

## Security Problem

Any HTTP caller can set X-Agent-Role: ciso-agent and:
1. Get past policy lookup (policy allows ciso-agent on privileged endpoints)
2. Trigger X-Privileged-Token injection
3. Downstream ERP mock accepts the static token unconditionally
4. Access confidential finance data

## Step 3-A Context

Step 3-A removed X-Bypass-Guard header security effect. ypass_guard is now only controlled by environment variable. However, bypass_guard still triggers privileged token injection at line 241-242 via or bypass_guard.
