# S2-D Privilege Surface Audit Report

- **Date**: 2026-09-25T05:25:00+08:00
- **Review Target**: `scripts/s2_v2/s2_d/`
- **Gate**: Gate 0 (Static Privilege & Subprocess Audit)
- **Status**: AUDITED & COMPLIANT

---

## 1. Executive Summary

This document details the privilege and command execution surface of all modules in `scripts/s2_v2/s2_d/`.
Under **Gate 0** and **Gate 1 Dry-Run**, the script package is strictly constrained:
- Zero elevated privilege (no `sudo` invocation)
- Zero netfilter / firewall modification (all iptables commands guarded by `dry_run` flag defaulting to `True`)
- Zero live mutation packets sent over network interfaces
- Zero modifications to PX4 SITL process state, binary, configuration, or environment.

---

## 2. Subprocess Invocation Inventory

All `subprocess` calls across the package were identified, audited, and classified:

| Module | Line / Function | Command Executed | Purpose | Privilege Level | Dry-Run Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `firewall_manager.py` | `_exec_cmd()` | `sudo iptables ...` | Apply/remove DROP rules | Elevated (`sudo`) | **NO-OP log only** (`dry_run=True` by default) |
| `firewall_manager.py` | `get_drop_counters()` | `sudo iptables -L ... -v -n -x` | Read drop packet counters | Read-Only Elevated | Returns simulated `0` if `dry_run=True` |
| `snapshot.py` | `_capture_firewall()` | `iptables-save` / `nft list ruleset` | Capture initial firewall state | Non-elevated / Read-Only | Safe fallback to empty string if failed |
| `snapshot.py` | `_capture_px4()` | `pgrep -a px4` / `ps aux` | Read PX4 PID & cmdline | Unprivileged Read-Only | Read-Only system query |
| `snapshot.py` | `_capture_listeners()` | `ss -tulpn` / `netstat -tulpn` | Read network listening ports | Unprivileged Read-Only | Read-Only network query |
| `preflight.py` | `check_git_status()` | `git status --porcelain` | Verify clean working tree | Unprivileged Read-Only | Read-Only git query |
| `probe_executor.py` | `send_probe()` | UDP socket `sendto` | MAVLink parameter mutation | Network Socket | **NO-OP log only** (`dry_run=True` by default) |

---

## 3. Strict Firewall Safety Analysis

In `firewall_manager.py`:
- `__init__(self, dry_run: bool = True)`:
  - Defaults to `dry_run = True`.
- Target ports strictly validated against `{18570, 13030, 14280}`.
- Prohibited ports `{14580, 14540, 14588}` explicitly rejected with `ValueError`.
- `_exec_cmd(cmd)`:
  - When `self.dry_run == True`, bypasses all `subprocess` execution, logging the command and returning simulated success.

---

## 4. Rollback and Cleanup Guarantees

- **Symmetric Tracking**: Every applied rule is appended to `self.applied_rules`.
- **Teardown Execution**: `rollback_all()` iterates through `self.applied_rules` in reverse order, executing deletion commands (`-D`).
- **Context Manager Guarantee**: `SafeFirewallManager` implements `__enter__` and `__exit__`, ensuring that even on unexpected exceptions, `rollback_all()` is unconditionally triggered.

---

## 5. Conclusion

The execution package contains **no hidden sudo calls, no unconditional subprocess executions, and no ambient network interactions**. It strictly adheres to the non-invasive constraints of Gate 0 and Gate 1.
