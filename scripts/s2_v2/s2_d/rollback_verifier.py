#!/usr/bin/env python3
"""Phase 4 rollback and re-demonstration verifier for Milestone M1.1-S2-D.

Verifies that containment rules are cleanly removed, host firewall state is
restored to pre-test baseline (F_post == F_pre), and previously observed bypass
behavior is re-demonstrated under identical test conditions.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from .firewall_manager import FirewallManager, TARGET_BYPASS_PORTS
from .models import HostFirewallSnapshot, Verdict
from .probe_executor import ProbeExecutor
from .snapshot import acquire_firewall_state

logger = logging.getLogger("s2_d.rollback")


class RollbackVerifier:
    """Verifies Phase 4 perimeter containment removal and bypass re-demonstration."""

    def __init__(
        self,
        firewall_mgr: FirewallManager,
        probe_exec: ProbeExecutor,
        dry_run: bool = True,
    ):
        self.firewall_mgr = firewall_mgr
        self.probe_exec = probe_exec
        self.dry_run = dry_run

    def verify_rollback(
        self,
        pre_firewall_snap: HostFirewallSnapshot,
        target_host: str = "127.0.0.1",
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute Phase 4 rollback and re-demonstration verification.

        Returns: (success, reason, audit_details)
        """
        audit_details: Dict[str, Any] = {
            "dry_run": self.dry_run,
            "rules_removed": False,
            "firewall_hash_restored": False,
            "re_probe_results": {},
            "verdict": Verdict.INDETERMINATE.value,
        }

        # Step 1: Remove perimeter rules
        ok, msg = self.firewall_mgr.rollback_containment()
        if not ok:
            audit_details["verdict"] = Verdict.FAIL.value
            return False, f"Firewall rollback execution failed: {msg}", audit_details
        audit_details["rules_removed"] = True
        audit_details["rollback_msg"] = msg

        # Step 2: Verify post-rollback firewall state matches pre-test baseline
        post_firewall_snap = acquire_firewall_state(mode="DRY_RUN" if self.dry_run else "LIVE")
        audit_details["pre_hash"] = pre_firewall_snap.rules_hash
        audit_details["post_hash"] = post_firewall_snap.rules_hash

        if pre_firewall_snap.rules_hash != post_firewall_snap.rules_hash:
            audit_details["verdict"] = Verdict.FAIL.value
            return (
                False,
                f"Firewall state hash mismatch after rollback: pre={pre_firewall_snap.rules_hash[:12]} "
                f"!= post={post_firewall_snap.rules_hash[:12]}",
                audit_details,
            )
        audit_details["firewall_hash_restored"] = True

        # Step 3: Re-probe target bypass ports to re-demonstrate bypass capability
        all_reprobed = True
        for port in sorted(TARGET_BYPASS_PORTS):
            res = self.probe_exec.send_probe(target_host, port)
            audit_details["re_probe_results"][str(port)] = res
            if not res.get("sent", False) and not self.dry_run:
                all_reprobed = False

        if not all_reprobed and not self.dry_run:
            audit_details["verdict"] = Verdict.INDETERMINATE.value
            return False, "Failed transmitting re-demonstration probes after rollback", audit_details

        audit_details["verdict"] = Verdict.PASS.value
        return (
            True,
            "Reversibility is demonstrated under the defined test procedure and observed execution conditions.",
            audit_details,
        )
