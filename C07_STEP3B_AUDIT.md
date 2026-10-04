# C07 Step 3-B Mutation Audit

## Scope

H3 (asserted-role semantics) + H5 (privileged token boundary).

## Before

Two caller-controlled paths to privileged downstream authority:

1. X-Agent-Role: ciso-agent header from any untrusted HTTP caller
2. ypass_guard == true (env-based, after Step 3-A)

Both paths directly injected X-Privileged-Token: ERP-ADMIN-TOKEN-999 at line 241-242, bypassing any cryptographic verification.

## Mutation

Replaced the privilege injection block with a disabled no-op:

`python
# DISABLED_UNTIL_TRUSTED_AUTHORIZATION: caller-controlled role and bypass
# no longer independently produce privileged downstream authority.
# X-Privileged-Token requires a verified authorization result.
# See C07 Historical Impact Audit H3/H5.
pass  # NO-OP: privileged token injection disabled
`

The condition if agent_role == "ciso-agent" or bypass_guard: and the headers["X-Privileged-Token"] = "ERP-ADMIN-TOKEN-999" line are both removed.

## After

- Caller-supplied X-Agent-Role is still used for policy lookup (preserved), but no longer directly creates privileged downstream authority
- ypass_guard (env) no longer triggers privileged token injection
- ciso-agent role still has broad endpoint policy (preserved), but cannot independently authorize privileged downstream access

## Security Invariant

`
caller-asserted role != authenticated principal
caller-supplied role != privileged authority
`

## Preserved

- Normal role policy lookup -- UNCHANGED
- Normal allow/deny logic -- UNCHANGED
- H1 (header bypass removed) -- UNCHANGED
- H2 (control-plane isolation) -- NOT MODIFIED
- H4 (DIT semantics) -- NOT MODIFIED
- H6 (audit schema) -- NOT MODIFIED

## Verification

| Check | Result |
|-------|--------|
| py_compile | PASS |
| ciso-agent to privileged token path | REMOVED |
| bypass_guard to privileged token path | REMOVED |
| DIT unchanged | PASS |
| Audit schema unchanged | PASS |
| Policy definitions unchanged | PASS |
| git diff --check | PASS |
| git diff --stat | 1 file, 7 insertions, 5 deletions |
| Deployment | NOT EXECUTED |
| Live regression | NOT EXECUTED |

## Scope

H1: ALREADY FIXED
H2: NOT MODIFIED
H3: MODIFIED
H4: NOT MODIFIED
H5: MODIFIED
H6: NOT MODIFIED

## Conclusion

H3_H5_STATIC_REPAIR = PASS
