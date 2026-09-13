# Multi-Substrate Post-Compromise Benchmark Methodology

<!-- dros_component: dros-vep-standards -->
<!-- dros_description: Scientific Methodology for Evaluating Post-Compromise Agent Security -->
<!-- dros_status: Active -->

## 1. Overview & Objective

This benchmark evaluates how various security architectures behave when an AI Agent has already been subverted (Post-Compromise).

```text
                 VEP Testbed
                      │
              Canonical Scenario
                      │
            Canonical Execution Request
                      │
           ┌──────────┼──────────┐
           │          │          │
          DROS       WASI       TLA+
        RUNTIME     RUNTIME   ASSURANCE
           │          │          │
           ▼          ▼          ▼
        Runtime    Runtime    Formal
        Result     Result     Result
           │          │          │
           └──────────┼──────────┘
                      ▼
              Canonical Evidence
                      │
                    Replay
```

## 2. Canonical Scenarios

1. **PC-001**: Unauthorized File Write (`execution_boundary`)
2. **PC-002**: Unauthorized Network Egress (`network_capability`)
3. **PC-003**: Privilege Escalation (`privilege_boundary`)
4. **PC-004**: Tool Substitution (`tool_identity_binding`)
5. **PC-005**: Argument Substitution (`argument_level_authority_binding`)
6. **PC-006**: Scope Expansion (`scope_containment`)
7. **PC-007**: Expired Authorization (`temporal_expiry`)
8. **PC-008**: Revoked Authorization (`hot_revocation`)
9. **PC-009**: Replay / Duplicate Execution (`replay_protection`)
10. **PC-010**: Cross-Principal Action (`principal_attribution`)

## 3. Usage & CLI

### List Substrates
```bash
python vep.py substrate list
```

### Run Benchmark
```bash
python vep.py benchmark post-compromise --substrate dros,wasi,tla
```

### Compare Results
```bash
python vep.py compare
```

### Deterministic Replay
```bash
python vep.py replay
```
