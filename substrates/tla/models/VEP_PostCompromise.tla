--------------------------- MODULE VEP_PostCompromise ---------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS 
    Principals,
    Tasks,
    Tools,
    Resources,
    Capabilities

VARIABLES
    authorized_principal,
    authorized_tool,
    authorized_resource,
    is_revoked,
    is_expired,
    executed

TypeOK ==
    /\ is_revoked \in BOOLEAN
    /\ is_expired \in BOOLEAN
    /\ executed \in BOOLEAN

Init ==
    /\ is_revoked = FALSE
    /\ is_expired = FALSE
    /\ executed = FALSE

AttemptExecution(p, t, r) ==
    /\ p = authorized_principal
    /\ t = authorized_tool
    /\ r = authorized_resource
    /\ ~is_revoked
    /\ ~is_expired
    /\ executed' = TRUE
    /\ UNCHANGED <<authorized_principal, authorized_tool, authorized_resource, is_revoked, is_expired>>

Revoke ==
    /\ is_revoked' = TRUE
    /\ UNCHANGED <<authorized_principal, authorized_tool, authorized_resource, is_expired, executed>>

Expire ==
    /\ is_expired' = TRUE
    /\ UNCHANGED <<authorized_principal, authorized_tool, authorized_resource, is_revoked, executed>>

Next ==
    \/ \E p \in Principals, t \in Tools, r \in Resources : AttemptExecution(p, t, r)
    \/ Revoke
    \/ Expire

\* Safety Invariants:
\* Invariant 1: No execution occurs after revocation
NoExecutionWhenRevoked ==
    is_revoked => ~executed

\* Invariant 2: No execution occurs after expiration
NoExecutionWhenExpired ==
    is_expired => ~executed

=============================================================================
