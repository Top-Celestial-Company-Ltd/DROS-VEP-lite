# The Agent Execution Boundary Problem — Round 1 Report

Protocol: `PROTO-AGENT-CLI-COMPLETE-MEDIATION-2026-v1.0`

Date: 2026-09-22

## Conclusion

The reviewed primary sources show that Codex CLI, Claude Code, Gemini CLI, Cursor, and OpenHands provide varying combinations of sandboxing, approval, tool policy, container, VM, or kernel-substrate controls. However, the reviewed public evidence is insufficient to establish CM-1 through CM-7 for complete mediation across a generally applicable Agent-CLI topology.

Formal research verdict:

```text
INSUFFICIENT_PUBLIC_EVIDENCE
```

This does not mean that any named product is unsafe, nor that it lacks enforcement. It means that public evidence has not established that every reachable execution path crosses one verifiable authorization boundary.

## Implication for DROS MCP defense

The MCP layer should reduce unnecessary execution topology rather than claim to replace host-wide CLI enforcement:

- deny arbitrary shell capability by default;
- validate typed semantic-tool arguments before constructing argv;
- keep the MCP handler as PEP-only; it must not mint `ALLOW`;
- route positive authorization through the canonical DROS Execution Authority;
- verify principal credentials, executable digests, TTL, revocation, and audit separately;
- scope claims to the registered MCP execution path.

## New VEP evidence

- `MCP-EXEC-AUTHORITY-01`: 24/24 registered-path contract tests pass, covering arbitrary-shell denial, typed argument validation, principal-credential rejection, executable-digest mismatch, canonical authority routing, and expiry fail-closed behavior.
- `EXEC-BOUNDARY-15-BPF-LSM-LIVE-ROUND2`: live `agentserver` evidence confirms BPF-LSM attachment, pre-exec denial, and baseline recovery after cleanup.
- BPF-LSM, AppArmor, and Landlock substrate evidence is not upgraded to host-wide choke-point or universal DROS-authority evidence.

## Not yet established

- a production vLEI or other cryptographic principal-credential verifier;
- fd-based `execveat` and immutable executable binding;
- host-wide alternate-topology closure;
- universal DROS CLI governance.

See the source registry and topology matrix for provenance and scope.
