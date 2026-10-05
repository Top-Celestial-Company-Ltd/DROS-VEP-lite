#!/usr/bin/env python3
"""Host perimeter containment manager for Milestone M1.1-S2-D.

Enforces containment rules strictly against the 3 S2-C unmediated bypass ports.
DEFAULT MODE IS DRY_RUN (SAFE, NON-INVASIVE). Live execution requires explicit opt-in.
"""
from __future__ import annotations

import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("s2_d.firewall")

# Mandatory target ports from S2-C empirical baseline
TARGET_BYPASS_PORTS: Set[int] = {18570, 13030, 14280}

# Strictly prohibited port to drop
PROHIBITED_DROP_PORTS: Set[int] = {14580, 14540, 14588}


class FirewallManager:
    """Manages host packet filter containment rules with strict fail-closed guards."""

    def __init__(self, dry_run: bool = True):
        # Default is strictly DRY_RUN
        self.dry_run: bool = dry_run
        self.applied_rules: List[Dict[str, Any]] = []
        self._simulated_counters: Dict[int, int] = {p: 0 for p in TARGET_BYPASS_PORTS}

    def validate_target_ports(self, ports: Set[int]) -> None:
        """Enforce strict port containment boundaries."""
        for p in ports:
            if p in PROHIBITED_DROP_PORTS:
                raise ValueError(
                    f"VIOLATION: Port {p} is in PROHIBITED_DROP_PORTS. "
                    "Dropping this port would sever DROS PEP delivery or induce self-inflicted DoS!"
                )
        if not ports.issubset(TARGET_BYPASS_PORTS):
            unexpected = ports - TARGET_BYPASS_PORTS
            raise ValueError(
                f"VIOLATION: Unexpected ports {unexpected}. "
                f"S2-D containment targets are strictly restricted to {TARGET_BYPASS_PORTS}."
            )

    def plan_containment_rules(self, ports: Optional[Set[int]] = None) -> List[Dict[str, Any]]:
        """Plan the exact iptables commands to contain target bypass ports."""
        target_ports = ports or TARGET_BYPASS_PORTS
        self.validate_target_ports(target_ports)

        planned = []
        for port in sorted(target_ports):
            rule = {
                "port": port,
                "protocol": "udp",
                "action": "DROP",
                "chain": "INPUT",
                "cmd_add": ["iptables", "-I", "INPUT", "1", "-p", "udp", "--dport", str(port), "-j", "DROP"],
                "cmd_del": ["iptables", "-D", "INPUT", "-p", "udp", "--dport", str(port), "-j", "DROP"],
                "cmd_check": ["iptables", "-L", "INPUT", "-v", "-n"],
            }
            planned.append(rule)
        return planned

    def apply_containment(self, ports: Optional[Set[int]] = None) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Apply containment rules to the host perimeter.

        In DRY_RUN mode, validates commands without system modification.
        """
        planned_rules = self.plan_containment_rules(ports)

        if self.dry_run:
            logger.info("[DRY_RUN] Simulating perimeter containment rule application (NO SYSTEM MUTATION)")
            self.applied_rules = planned_rules
            # Reset simulated counters
            self._simulated_counters = {r["port"]: 0 for r in planned_rules}
            return True, "DRY_RUN: Perimeter containment planned and validated (0 rules actually injected)", planned_rules

        # LIVE MODE (Requires explicit opt-in and sudo privileges)
        if not sys.platform.startswith("linux"):
            return False, "Live firewall containment is only supported on Linux hosts", []

        applied = []
        for rule in planned_rules:
            try:
                cmd = ["sudo"] + rule["cmd_add"]
                proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
                applied.append(rule)
            except Exception as exc:
                # Rollback on partial failure
                self.rollback_containment(applied)
                return False, f"Failed applying live rule for port {rule['port']}: {exc}", applied

        self.applied_rules = applied
        return True, f"Live containment active: {len(applied)} rules injected", applied

    def read_rule_counters(self) -> Dict[int, int]:
        """Read drop packet counters for target ports."""
        if self.dry_run:
            # Return current simulated counters
            return dict(self._simulated_counters)

        if not sys.platform.startswith("linux"):
            return {p: 0 for p in TARGET_BYPASS_PORTS}

        counters: Dict[int, int] = {p: 0 for p in TARGET_BYPASS_PORTS}
        try:
            proc = subprocess.run(
                ["sudo", "iptables", "-L", "INPUT", "-v", "-n", "-x"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in proc.stdout.splitlines():
                # Look for lines with DROP udp dpt:<port>
                for port in TARGET_BYPASS_PORTS:
                    if f"dpt:{port}" in line and "DROP" in line:
                        parts = line.split()
                        if parts and parts[0].isdigit():
                            counters[port] = int(parts[0])
        except Exception as exc:
            logger.error(f"Error reading live rule counters: {exc}")

        return counters

    def simulate_packet_drop(self, port: int, packet_count: int = 1) -> None:
        """Increment simulated counters in dry-run mode for test harness verification."""
        if self.dry_run and port in self._simulated_counters:
            self._simulated_counters[port] += packet_count

    def rollback_containment(self, rules_to_remove: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, str]:
        """Remove containment rules and restore previous firewall state."""
        rules = rules_to_remove if rules_to_remove is not None else self.applied_rules

        if self.dry_run:
            logger.info("[DRY_RUN] Simulating perimeter containment rollback (NO SYSTEM MUTATION)")
            self.applied_rules = []
            self._simulated_counters = {p: 0 for p in TARGET_BYPASS_PORTS}
            return True, "DRY_RUN: Perimeter containment rolled back cleanly"

        if not sys.platform.startswith("linux"):
            return True, "Non-Linux host; nothing to roll back"

        errors = []
        for rule in reversed(rules):
            try:
                cmd = ["sudo"] + rule["cmd_del"]
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            except Exception as exc:
                errors.append(f"Port {rule['port']}: {exc}")

        self.applied_rules = []
        if errors:
            return False, f"Rollback completed with errors: {'; '.join(errors)}"
        return True, "Live perimeter containment rolled back successfully"
