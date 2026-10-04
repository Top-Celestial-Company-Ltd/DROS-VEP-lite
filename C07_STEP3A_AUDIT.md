# C07 Step 3-A Mutation Audit

## Scope

H1 only: Remove caller-controlled X-Bypass-Guard security effect.

## Before

HTTP X-Bypass-Guard header was read at dros_guard.py:151 via:

`python
request.headers.get("X-Bypass-Guard", "false").lower() == "true"
`

Combined with environment BYPASS_GUARD via OR semantics. Any untrusted HTTP caller could set X-Bypass-Guard: true to bypass all policy evaluation (confirmed live in C07 Attack A).

## Mutation

Removed the
equest.headers.get("X-Bypass-Guard", ...) portion from the bypass expression at line 151. The new line is:

`python
bypass_guard = (os.environ.get("BYPASS_GUARD", "false").lower() == "true")
`

The or request.headers.get(...) clause is deleted. HTTP caller can no longer control bypass via X-Bypass-Guard header.

## After

HTTP caller supplied X-Bypass-Guard: true no longer produces any security effect:
- Cannot set ypass_guard = true
- Cannot skip policy evaluation
- Cannot force status code 200
- Cannot trigger privileged token injection via bypass

## Preserved

- policy logic (PRECOMPILED_POLICY_INDEX: allow/deny) -- UNCHANGED
- role logic (X-Agent-Role, lookup_key, ciso-agent) -- UNCHANGED
- DIT logic (verify_pki_dit_identity, VALID_ED25519) -- UNCHANGED
- privileged-token logic (X-Privileged-Token, ERP-ADMIN-TOKEN-999) -- UNCHANGED
- audit logic (schema, fields) -- UNCHANGED
- environment/test semantics (BYPASS_GUARD env via dashboard/subprocess) -- PRESERVED

## Verification

| Check | Result |
|-------|--------|
| Branch | fix/vep-lite-guard-c07 |
| HEAD before mutation | 773b840dfe21cb0ec9f06e0b555a4d45b4c6d817 |
| Original Guard SHA | 4B072F44FBAB5E00C1AE09AD6355D9E7816AF973ACA2085A757A36915D08A5B2 |
| Mutated Guard SHA | CC1411DD6A74CA684571623C9848E48FC77A57CC9DE0C7CB551FA5BA9CD008DE |
| py_compile | PASS (warning only for pre-existing escape sequence in banner) |
| X-Bypass-Guard caller security effect | REMOVED |
| Static search: X-Bypass-Guard header read | 0 results |
| Environment test semantics | PRESERVED |
| git diff --check | PASS |
| git diff --stat | 1 file, 1 insertion, 1 deletion |
| Only H1 modified | PASS |
| No other source mutation | PASS |
| LIVE REGRESSION | NOT EXECUTED |

## Scope Boundary

H1: MODIFIED
H2: NOT MODIFIED
H3: NOT MODIFIED
H4: NOT MODIFIED
H5: NOT MODIFIED
H6: NOT MODIFIED

## Conclusion

H1_STATIC_REPAIR = PASS
