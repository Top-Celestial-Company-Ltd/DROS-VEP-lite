package vep.authz

import future.keywords.if
import future.keywords.in

default allow := false
default deny_reason := "DEFAULT_DENY"

is_valid_principal if {
    input.authorization_context.authorized_principal
    input.principal == input.authorization_context.authorized_principal
}
is_valid_principal if {
    not input.authorization_context.authorized_principal
}

is_not_revoked if {
    not input.authorization_context.is_revoked
}

is_not_expired if {
    not input.authorization_context.is_expired
    input.authorization_context.ttl > 0
}

# Scope checking
is_in_scope if {
    "admin" in input.authorization_context.scope
}
is_in_scope if {
    "workspace" in input.authorization_context.scope
    startswith(input.resource, "/workspace")
}
is_in_scope if {
    "billing" in input.authorization_context.scope
    startswith(input.resource, "rate_card_")
}
is_in_scope if {
    "banking" in input.authorization_context.scope
    startswith(input.resource, "bank_account_")
}
is_in_scope if {
    "finance" in input.authorization_context.scope
    input.resource == "account-ledger"
}

is_not_replayed if {
    not input.authorization_context.replayed
}

# Tool checking
is_tool_authorized if {
    not input.authorization_context.authorized_tools
}
is_tool_authorized if {
    input.tool in input.authorization_context.authorized_tools
}

# Argument checking
are_args_valid if {
    not input.authorization_context.argument_constraints
}
are_args_valid if {
    prefix := input.authorization_context.argument_constraints.path_prefix
    startswith(input.arguments.path, prefix)
}

# Network Egress checking
is_egress_allowed if {
    input.tool != "network.connect"
}
is_egress_allowed if {
    input.tool == "network.connect"
    "external" in input.authorization_context.scope
}

# Privilege boundary checking
is_privilege_allowed if {
    not input.tool in ["system.admin", "database.drop"]
}
is_privilege_allowed if {
    input.tool in ["system.admin", "database.drop"]
    "cluster-admin" in input.authorization_context.scope
}

# Overall Allow
allow if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    is_in_scope
    is_tool_authorized
    are_args_valid
    is_egress_allowed
    is_privilege_allowed
    is_not_replayed
}

# Granular Deny Reasons
deny_reason := "PRINCIPAL_ATTRIBUTION_MISMATCH" if {
    not is_valid_principal
}

deny_reason := "AUTHORIZATION_REVOKED" if {
    is_valid_principal
    not is_not_revoked
}

deny_reason := "AUTHORIZATION_EXPIRED" if {
    is_valid_principal
    is_not_revoked
    not is_not_expired
}

deny_reason := "PRIVILEGE_ESCALATION_DENIED" if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    not is_privilege_allowed
}

deny_reason := "UNAUTHORIZED_EGRESS" if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    is_privilege_allowed
    not is_egress_allowed
}

deny_reason := "SCOPE_VIOLATION" if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    is_privilege_allowed
    is_egress_allowed
    not is_in_scope
}

deny_reason := "TOOL_NOT_AUTHORIZED" if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    is_privilege_allowed
    is_egress_allowed
    is_in_scope
    not is_tool_authorized
}

deny_reason := "ARGUMENT_CONSTRAINTS_VIOLATED" if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    is_privilege_allowed
    is_egress_allowed
    is_in_scope
    is_tool_authorized
    not are_args_valid
}

deny_reason := "REPLAY_DETECTED" if {
    is_valid_principal
    is_not_revoked
    is_not_expired
    is_privilege_allowed
    is_egress_allowed
    is_in_scope
    is_tool_authorized
    are_args_valid
    not is_not_replayed
}
