# Environment & Pinning Specification: Claude-Red × VEP

## 1. Upstream Pinning
* **Repository**: `https://github.com/SnailSploit/Claude-Red.git`
* **Pinned Commit SHA**: `24d7968bab4b883e7f13477afe0fd91f2df3b722`
* **Date Pinned**: 2026-09-13
* **Local Submodule/Source**: `benchmarks/claude-red-vep/adapters/claude_red/upstream`

## 2. Selected Tier-1 Skills Mapping
Only Tier-1 skills mapped to RFC-010 threat fixtures are enabled for the initial evaluation:

| Skill Path in Upstream | Category | Target VEP Scenario |
| :--- | :--- | :--- |
| `Skills/ai/offensive-ai-security` | AI Security | `VEP-RT-002` (IPI), `VEP-RT-008` (Post-Compromise) |
| `Skills/api/offensive-api-security` | API Security | `VEP-RT-001` (Direct Tool Abuse), `VEP-RT-004` |
| `Skills/api/offensive-api-abuse` | API Security | `VEP-RT-003` (Tool Chaining) |
| `Skills/container/offensive-container-escape` | Container | `VEP-RT-001`, `VEP-RT-005` (Credential Abuse) |
| `Skills/privesc/linux-privesc` | Privilege Escalation | `VEP-RT-004` (Privilege Escalation) |
| `Skills/post-exploitation/lateral-movement` | Post-Exploitation | `VEP-RT-006` (Delegation Escalation) |
| `Skills/post-exploitation/persistence` | Post-Exploitation | `VEP-RT-007` (Persistence & Revocation Bypass) |

## 3. Runner Architecture
* **Isolation**: OpenShip Docker Compose isolated testbed network (`172.28.0.0/16`)
* **Model Configuration**: 
  - Phase A / Smoke: Anthropic Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`)
  - API Credentials: Read exclusively from `ANTHROPIC_API_KEY` environment variable. Never written to disk or logs.
