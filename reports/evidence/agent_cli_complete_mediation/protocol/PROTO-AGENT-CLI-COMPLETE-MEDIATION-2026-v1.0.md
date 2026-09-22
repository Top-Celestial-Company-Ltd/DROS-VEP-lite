可以。這次我建議**不要讓 Codex 直接開始測**，而是先給它一份完整、可凍結的研究 protocol，讓它自己建立 evidence matrix → 公開證據掃描 → 選測試對象 → 再決定是否需要 live test。

下面這份可以直接交給 Codex 執行。

# PROTO-AGENT-CLI-COMPLETE-MEDIATION-2026-v1.0

## 0. Research Title

**The Agent Execution Boundary Problem: Public Evidence for Complete Mediation of AI Agent CLI Execution**

Short name:

`AGENT-CLI-CM-2026`

Research question:

> Do currently available AI-agent CLI execution environments provide publicly verifiable evidence of complete mediation across all reachable process-execution paths?

Secondary question:

> When complete mediation cannot be publicly established, can capability minimization through semantically narrow interfaces reduce the execution topology that must be governed?

---

# 1. Research Objective

本研究不是比較哪個 Agent CLI「比較安全」。

也不是證明 CLI「一定危險」。

研究目標是：

1. 定義 AI Agent CLI execution topology。
2. 建立 complete mediation 的可驗證條件。
3. 系統性蒐集公開產品文件、security documentation、CVE、research papers、security advisories、source code 與 reproducible research。
4. 建立各方案 execution-topology coverage matrix。
5. 區分：

   * explicitly covered
   * explicitly outside boundary
   * unknown / insufficient public evidence
6. 對具有公開可驗證 enforcement claim 的代表性方案進行有限 live reproducibility testing。
7. 不將單一 bypass、單一 CVE 或單一測試結果膨脹成「整個系統不安全」。
8. 評估「CLI deny-by-default / capability minimization」是否是一項合理的 architecture recommendation。

---

# 2. Theoretical Foundation

## 2.1 Complete Mediation

核心理論來源：

Saltzer & Schroeder, 1975:

> Every access to every object must be checked for authority.

本研究將其轉換成 Agent execution context：

> Every reachable execution authority transition must pass through an applicable and enforceable authorization boundary.

注意：

本研究不得把傳統 complete mediation 原則直接宣稱為「AI Agent CLI 的既有正式定義」。

必須明確標示：

* classical principle
* research operationalization

---

## 2.2 Confinement

Lampson, 1973：

研究 confinement problem 及其必要條件。

本研究可使用 confinement 作為歷史與理論背景，用於說明：

> controlled execution environment 中的 alternate information/control paths 是經典 security problem。

不得直接聲稱：

> Lampson 1973 已經證明 AI Agent CLI topology completeness 在一般情況下不可判定。

若需要使用 undecidability claim，必須另外建立 formal computability / program-analysis literature support。

---

# 3. Core Research Thesis

Primary thesis:

> Publicly available evidence may demonstrate substantial sandboxing, approval, process, filesystem, network, or kernel-level enforcement for AI Agent CLI environments, but such evidence should not automatically be interpreted as proof of complete mediation across all reachable execution paths.

Secondary thesis:

> Where business objectives can be expressed through narrower semantic capabilities, capability minimization may reduce the reachable execution topology and therefore reduce the burden of execution governance.

Important:

The study does NOT assume that MCP is inherently safer than CLI.

---

# 4. Research Non-Claims

The study MUST NOT claim:

* CLI is inherently insecure.
* CLI is always exploitable.
* Any named product is unsafe.
* Any named vendor failed security.
* MCP is inherently secure.
* WebMCP is inherently secure.
* DROS universally solves CLI governance.
* Sandbox escape research proves universal bypassability.
* Absence of public evidence proves absence of enforcement.
* A single bypass proves complete system compromise.
* A single successful enforcement test proves complete mediation.

---

# 5. Operational Definition

For this study, a solution demonstrates **Complete-Mediation Evidence (CME)** only if public evidence establishes all of the following within a declared boundary:

### CM-1 — Execution authority definition

The system explicitly defines what execution authority is being controlled.

Examples:

* process creation
* executable invocation
* shell command execution
* interpreter execution
* subprocess creation
* script execution

### CM-2 — Pre-execution enforcement

The enforcement decision occurs before the protected execution effect.

### CM-3 — Reachable-path coverage

All execution paths claimed within the declared topology are shown to traverse the enforcement boundary.

### CM-4 — Alternate-path resistance

The evidence addresses relevant alternate paths, including where applicable:

* execve
* execveat
* child process
* interpreter-mediated execution
* script execution
* alternate executable resolution
* PATH manipulation
* inherited execution context
* hooks / configuration-triggered execution
* runtime/container transition
* indirect process creation

### CM-5 — Authorization binding

The enforcement decision is tied to a defined identity/capability/policy context rather than only a generic deny rule.

### CM-6 — Fail-closed behavior

When authorization state is unavailable, invalid, expired, revoked, or malformed, the declared protected execution path fails closed.

### CM-7 — Evidence reproducibility

The claimed enforcement is supported by reproducible documentation, source, test, or independent research.

---

# 6. Evidence Classification

Every matrix cell MUST use exactly one of:

### C — Covered

Public evidence explicitly establishes that the path is within the enforcement boundary.

### N — Not Covered

Public documentation/source explicitly states that the path is outside the protection boundary or demonstrates that it bypasses the mechanism.

### U — Unknown

Available public evidence is insufficient to establish either C or N.

### T — Tested

Live reproducibility test independently confirms the behavior.

### X — Not Applicable

The execution path is outside the declared architecture and is explicitly documented as such.

Do NOT convert:

`U → N`

merely because documentation is silent.

Do NOT convert:

`C → complete mediation`

unless the full CM-1 through CM-7 conditions are satisfied.

---

# 7. Evidence Hierarchy

Rank evidence:

## E0 — Vendor marketing claim

Examples:

* "secure"
* "sandboxed"
* "protected"
* "safe execution"

Use as contextual evidence only.

## E1 — Official documentation

Examples:

* security model
* sandbox documentation
* permission model
* architecture documentation

## E2 — Source code / implementation

Publicly inspectable implementation showing enforcement.

## E3 — Security advisory / CVE

Documented vulnerability or limitation.

## E4 — Independent security research

Peer-reviewed paper, reputable security research, responsible disclosure, or high-quality technical analysis.

## E5 — Reproducible live test

Independent test harness with machine-readable result.

E5 is strongest for tested behavior, but still bounded by tested topology.

---

# 8. Candidate Landscape

Initial candidate set:

### Agent CLI / coding agents

* OpenAI Codex CLI
* Claude Code
* Gemini CLI
* Cursor Agent / Cursor terminal
* Kiro CLI
* OpenHands
* other major publicly documented agentic coding/CLI environments discovered during research

### Execution / sandbox mechanisms

* Landlock
* AppArmor / Linux LSM
* BPF-LSM
* Seccomp
* container runtime isolation
* VM-based sandboxing
* other Agent-specific execution sandbox systems

Candidate inclusion requires public documentation or reproducible evidence.

Do not assume all candidates provide equivalent functionality.

---

# 9. Execution-Topology Taxonomy

The following topology must be used consistently.

## ET-01 Direct process creation

* execve
* equivalent process creation APIs

## ET-02 execveat

Explicitly test/document separately where applicable.

## ET-03 Child process creation

Parent Agent process spawning another process.

## ET-04 Shell-mediated execution

Examples:

* sh
* bash
* zsh
* powershell
* cmd

## ET-05 Interpreter-mediated execution

Examples:

* Python
* Node.js
* Ruby
* Perl
* Java
* other script interpreters

## ET-06 Script execution

Shell scripts or executable scripts.

## ET-07 Alternate executable resolution

Examples:

* PATH manipulation
* relative executable resolution
* symlink/path mutation
* alternate binary shadowing

## ET-08 Environment inheritance

Examples:

* environment variables
* inherited credentials
* inherited runtime configuration

## ET-09 Hook/configuration-triggered execution

Examples:

* repository hooks
* task hooks
* configuration files
* startup scripts
* build hooks

## ET-10 Runtime/container transition

Examples:

* container execution
* namespace transition
* runtime launcher
* nested execution environment

## ET-11 JIT / anonymous executable memory

Only include where relevant to the claimed execution model.

## ET-12 Indirect process creation

Examples:

* helper processes
* service managers
* task schedulers
* language runtimes
* trusted components

## ET-13 Inherited execution context

Examples:

* inherited file descriptors
* inherited namespaces
* inherited capabilities
* inherited credentials

## ET-14 External effect transition

Examples:

* network clients
* cloud CLI
* SSH
* package managers
* deployment tools

Do not automatically classify external effects as process creation.

---

# 10. Coverage Matrix

Create:

`reports/evidence/agent_cli_complete_mediation/AGENT_CLI_EXECUTION_TOPOLOGY_MATRIX.md`

and:

`reports/evidence/agent_cli_complete_mediation/agent_cli_execution_topology_matrix.json`

Required columns:

```text
solution
version
declared_boundary
execution_authority
ET-01
ET-02
ET-03
ET-04
ET-05
ET-06
ET-07
ET-08
ET-09
ET-10
ET-11
ET-12
ET-13
ET-14
evidence_level
source_count
live_test_status
complete_mediation_status
limitations
last_verified
```

---

# 11. Complete-Mediation Status

Allowed values:

### ESTABLISHED

Only when CM-1 through CM-7 are supported within an explicitly declared topology.

### PARTIAL

Some execution paths are explicitly covered, but complete mediation across the declared topology is not established.

### TOPOLOGY_DEPENDENT

Coverage depends materially on deployment/runtime topology.

### UNKNOWN

Public evidence is insufficient to establish the security property.

### NOT_APPLICABLE

The solution does not claim to provide execution governance.

Never use:

* SAFE
* UNSAFE
* SECURE
* INSECURE
* BEST
* WORST

as research classifications.

---

# 12. MCP Control Experiment

This study MUST explicitly include the following distinction.

MCP itself is not automatically a security property.

Compare:

### MCP-A — Arbitrary shell capability

```text
run_bash(command: string)
```

Classify as:

`ARBITRARY_EXECUTION_CAPABILITY`

### MCP-B — Semantic capability

```text
create_invoice(
    customer_id,
    items,
    currency
)
```

Classify as:

`SEMANTICALLY_BOUNDED_CAPABILITY`

Question:

> Does changing protocol from CLI to MCP actually reduce reachable execution topology?

If MCP-A ultimately invokes arbitrary shell, do not claim topology reduction.

If MCP-B exposes only a bounded semantic operation, document the reduced execution authority.

---

# 13. Primary Hypothesis

H1:

> Public evidence will show extensive but heterogeneous enforcement coverage across Agent CLI execution environments, while no candidate should be classified as COMPLETE-MEDIATION ESTABLISHED without explicit evidence satisfying the complete-mediation criteria.

This is a hypothesis.

It must be allowed to fail.

If a candidate satisfies all criteria, record it as such.

---

# 14. Secondary Hypothesis

H2:

> Semantically bounded capabilities can expose materially narrower execution authority than arbitrary shell/CLI capability.

This must be demonstrated structurally, not rhetorically.

Do not claim security improvement merely because the interface is called MCP.

---

# 15. Live-Test Selection Criteria

Do NOT immediately test every product.

First complete public evidence scan.

Select live-test candidates only when:

1. the product makes a concrete execution-enforcement claim;
2. the mechanism is publicly accessible;
3. a reproducible test environment can be created;
4. testing does not require unauthorized access;
5. the test can distinguish enforcement from mere UI approval.

Priority:

1. representative Agent CLI
2. representative sandbox
3. representative OS-level enforcement
4. representative MCP arbitrary-execution capability
5. representative MCP semantic capability

---

# 16. Minimum Live Test Set

If live testing is required:

### LT-01

Direct execution

### LT-02

Child execution

### LT-03

Interpreter-mediated execution

### LT-04

Alternate executable resolution

### LT-05

Script execution

### LT-06

Configuration/hook-triggered execution

### LT-07

Execution through alternate process path

### LT-08

Authorization state unavailable

### LT-09

Authorization revoked/expired

### LT-10

Process attribution

Each test must record:

```text
test_id
solution
version
environment
execution_surface
execution_path
expected
observed
process_created
enforcement_layer
authorization_context
attribution
audit
evidence_path
timestamp
```

---

# 17. Safety / Ethics Boundary

Only test:

* local owned environments
* disposable VMs
* authorized installations
* intentionally created test repositories
* synthetic credentials
* synthetic targets

Never:

* attack production systems
* bypass third-party access controls
* exfiltrate real secrets
* test against systems without authorization
* publish operational exploit instructions unless independently necessary and responsibly disclosed.

---

# 18. Reproducibility Requirements

All live tests must provide:

* exact version
* OS/kernel version
* runtime version
* configuration
* policy
* test command
* expected result
* observed result
* machine-readable result
* SHA-256
* timestamp

Evidence must be immutable after closure.

Canonical artifacts MUST NOT be silently overwritten.

Corrections require a new evidence version.

---

# 19. Research Evidence Directory

Create:

```text
reports/evidence/agent_cli_complete_mediation/
├── protocol/
│   └── PROTO-AGENT-CLI-COMPLETE-MEDIATION-2026-v1.0.md
├── sources/
│   ├── sources.json
│   └── source_notes.md
├── matrix/
│   ├── AGENT_CLI_EXECUTION_TOPOLOGY_MATRIX.md
│   └── agent_cli_execution_topology_matrix.json
├── tests/
│   ├── live/
│   └── fixtures/
├── reports/
│   └── COMPLETE_MEDIATION_LANDSCAPE_REPORT.md
└── manifests/
    └── ARTIFACT_MANIFEST.json
```

---

# 20. Source Registry

Create:

`agent_cli_complete_mediation_sources.json`

Each source:

```json
{
  "source_id": "",
  "title": "",
  "publisher": "",
  "url": "",
  "publication_date": "",
  "access_date": "",
  "product": "",
  "version": "",
  "evidence_level": "",
  "execution_paths": [],
  "claims_supported": [],
  "claims_not_supported": [],
  "limitations": ""
}
```

Every matrix assertion must map to at least one source_id.

---

# 21. Source Quality Rules

Prefer:

1. official security documentation
2. official source code
3. CVE / security advisory
4. peer-reviewed research
5. reputable independent security research
6. technical analysis
7. community discussion

Marketing claims alone cannot establish complete mediation.

---

# 22. Required Literature Anchors

At minimum investigate:

* Saltzer & Schroeder, 1975 — The Protection of Information in Computer Systems
* Lampson, 1973 — A Note on the Confinement Problem
* relevant formal work on confinement
* relevant work on complete mediation/reference monitors
* relevant work on program-analysis limitations / undecidability where needed
* contemporary Agent CLI security research
* contemporary sandbox escape research
* Agent security / prompt injection research relevant to execution authority

Do not attribute claims to classical papers that they do not actually establish.

---

# 23. Expected Research Output

Produce:

## A. Protocol

Frozen research methodology.

## B. Landscape Matrix

Machine-readable and human-readable.

## C. Evidence Report

A factual summary of what each solution publicly establishes.

## D. Live-Test Report

Only for selected candidates.

## E. Complete-Mediation Assessment

No overall product ranking.

## F. Capability-Minimization Analysis

Compare:

```text
arbitrary shell capability
vs
semantically bounded capability
```

without claiming protocol-level security merely from the protocol name.

---

# 24. Final Claim Template

If evidence supports the expected result, use:

> Across the publicly available evidence reviewed in this study, contemporary AI-agent CLI environments demonstrate multiple layers of execution control, including sandboxing, approval mechanisms, filesystem restrictions, process controls, and operating-system enforcement. However, we found insufficient public evidence to establish complete mediation across all reachable execution paths for a generally applicable AI-agent CLI architecture.

Then:

> This finding should not be interpreted as evidence that the examined systems are insecure. Rather, it indicates that the stronger property—complete mediation across the declared execution topology—requires a substantially stronger evidence standard than demonstrating individual sandbox or process controls.

For capability minimization:

> Where an agent's business objective can be expressed through a semantically bounded capability, exposing that capability instead of arbitrary shell execution may reduce the reachable execution topology and therefore the scope of execution governance required.

---

# 25. Strong Prohibition on Overclaiming

Never transform:

```text
unknown
```

into:

```text
bypass
```

Never transform:

```text
one bypass
```

into:

```text
system-wide insecurity
```

Never transform:

```text
sandbox enforcement
```

into:

```text
complete mediation
```

Never transform:

```text
MCP
```

into:

```text
secure
```

Never transform:

```text
no public proof
```

into:

```text
impossible
```

---

# 26. Decision Gate

After public evidence scan:

### Gate A

If one or more candidates have sufficient evidence for complete mediation:

→ document exactly which topology and conditions establish it.

### Gate B

If no candidate satisfies the criteria:

→ proceed to representative live tests.

### Gate C

If live tests still cannot establish complete mediation:

→ report:

`COMPLETE_MEDIATION_NOT_ESTABLISHED`

not:

`COMPLETE_MEDIATION_IMPOSSIBLE`

### Gate D

If evidence is too incomplete:

→ report:

`INSUFFICIENT_PUBLIC_EVIDENCE`

---

# 27. Definition of Done

The study is complete only when:

* protocol frozen
* literature anchors verified
* candidate set declared
* source registry complete
* execution taxonomy frozen
* coverage matrix populated
* every matrix assertion has evidence provenance
* unknowns remain explicitly unknown
* selected live tests completed or formally marked blocked
* machine-readable evidence generated
* hashes generated
* final report generated
* claim boundaries reviewed
* no canonical artifact silently modified

Final status must be one of:

```text
COMPLETE_MEDIATION_ESTABLISHED
COMPLETE_MEDIATION_NOT_ESTABLISHED
INSUFFICIENT_PUBLIC_EVIDENCE
```

with scope and topology explicitly stated.

---

# 28. First Execution Instruction for Codex

Do NOT begin by modifying DROS implementation.

Do NOT begin by creating live exploits.

Do NOT begin by testing every candidate.

First execute:

1. Create protocol directory.
2. Freeze this protocol.
3. Build source registry.
4. Conduct public evidence scan.
5. Populate initial topology matrix.
6. Identify claims that can and cannot be established from public evidence.
7. Only then propose the minimum live-test set.
8. Wait for architecture/research gate before modifying existing canonical DROS/VEP artifacts.

The research must remain independent of whether DROS itself succeeds or fails at universal CLI governance.

---

# 29. Research Principle

> **The subject of this study is not whether a particular product is secure. The subject is whether complete mediation of autonomous-agent CLI execution can be publicly established under an explicit execution-topology boundary.**

This distinction is mandatory throughout the study.


