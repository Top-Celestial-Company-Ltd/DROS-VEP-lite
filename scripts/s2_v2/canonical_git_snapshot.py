#!/usr/bin/env python3
"""Canonical Git snapshot verifier for DROS Drone evidence artifacts.

Validates that artifacts match both local disk state and the exact Git blob
from a specified frozen commit.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _find_git_root(start_path: Path) -> Path:
    """Find the root of the Git working tree."""
    resolved = start_path.resolve()
    for parent in [resolved] + list(resolved.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError(f"Git root not found from {start_path}")


def _git_show_blob(git_root: Path, commit_sha: str, repo_rel_path: str) -> bytes:
    """Read an exact file snapshot from a Git commit using git show."""
    # Normalize path separators for Git
    git_path = repo_rel_path.replace("\\", "/")
    cmd = ["git", "show", f"{commit_sha}:{git_path}"]
    proc = subprocess.run(
        cmd,
        cwd=str(git_root),
        capture_output=True,
        text=False,  # Raw bytes to prevent CRLF corruption
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Failed to read {git_path} at {commit_sha} from git: {err}"
        )
    return proc.stdout


def _git_rev_parse_blob(git_root: Path, commit_sha: str, repo_rel_path: str) -> str:
    """Get the Git object SHA-1 for a path at a specific commit."""
    git_path = repo_rel_path.replace("\\", "/")
    cmd = ["git", "rev-parse", f"{commit_sha}:{git_path}"]
    proc = subprocess.run(
        cmd,
        cwd=str(git_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip()
        raise RuntimeError(
            f"Failed to rev-parse {git_path} at {commit_sha}: {err}"
        )
    return proc.stdout.strip()


def canonical_endpoint_key(key: Any) -> str:
    """Convert an endpoint key (e.g. [pid, local_addr, peer_addr, state]) to a canonical string representation."""
    if isinstance(key, list):
        return "|".join(str(x) for x in key)
    return str(key)


def build_authority_index(
    authority_data: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Build strict 1-to-1 endpoint-key -> authority-record index.

    Every authority evaluation MUST contain endpoint_key.
    Duplicate or missing keys are fatal.
    """
    evaluations = authority_data.get("endpoint_authority_evaluations")

    if not isinstance(evaluations, list):
        raise ValueError(
            "authority_data.endpoint_authority_evaluations must be a list"
        )

    index: Dict[str, Dict[str, Any]] = {}

    for idx, record in enumerate(evaluations):
        if not isinstance(record, dict):
            raise ValueError(
                f"Authority evaluation at index {idx} must be an object"
            )

        if "endpoint_key" not in record or record["endpoint_key"] is None:
            raise ValueError(
                f"Authority evaluation at index {idx} is missing endpoint_key"
            )

        c_key = canonical_endpoint_key(record["endpoint_key"])

        if not c_key:
            raise ValueError(
                f"Authority evaluation at index {idx} has empty endpoint_key"
            )

        if c_key in index:
            raise ValueError(
                f"Duplicate endpoint_key in authority evaluations: {c_key}"
            )

        index[c_key] = record

    if len(index) != len(evaluations):
        raise ValueError(
            "Authority index cardinality mismatch: every authority evaluation "
            "must map to exactly one unique endpoint_key"
        )

    return index


def extract_route_identity(route_or_ep: Dict[str, Any]) -> Dict[str, Any]:
    """Extract strict structured canonical route identity.

    Missing protocol/ingress/tap/target is an error.
    No synthetic default values are permitted.
    """
    if "route_identity" in route_or_ep:
        inner = route_or_ep["route_identity"]
        if not isinstance(inner, dict):
            raise ValueError(
                f"route_identity must be a dict, got {type(inner)}"
            )

        protocol = inner.get("protocol")
        ingress = inner.get("pep_ingress_port")
        tap = inner.get("downstream_tap_port")
        target = inner.get("target_port")
    else:
        protocol = route_or_ep.get("protocol")
        ingress = route_or_ep.get("pep_ingress_port")
        if ingress is None:
            ingress = route_or_ep.get("ingress_port")

        tap = route_or_ep.get("downstream_tap_port")

        target = route_or_ep.get("target_port")
        if target is None:
            target = route_or_ep.get("forward_port")

    if protocol is None:
        raise ValueError(
            f"Missing protocol in route identity: {route_or_ep}"
        )

    if ingress is None:
        raise ValueError(
            f"Missing pep_ingress_port in route identity: {route_or_ep}"
        )

    if tap is None:
        raise ValueError(
            f"Missing downstream_tap_port in route identity: {route_or_ep}"
        )

    if target is None:
        raise ValueError(
            f"Missing target_port in route identity: {route_or_ep}"
        )

    try:
        ingress_i = int(ingress)
        tap_i = int(tap)
        target_i = int(target)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Non-integer route identity field: {route_or_ep}"
        ) from exc

    return {
        "protocol": str(protocol).upper(),
        "pep_ingress_port": ingress_i,
        "downstream_tap_port": tap_i,
        "target_port": target_i,
    }


def match_route_identity(
    s2_b_path_identity: Any,
    s1_route: Dict[str, Any],
) -> bool:
    """Strict equality comparison between S2-B authority path identity and S1 governed route identity."""
    if not s2_b_path_identity or not isinstance(s2_b_path_identity, dict):
        return False
    try:
        s2b_id = extract_route_identity(s2_b_path_identity)
        s1_id = extract_route_identity(s1_route)
        return s2b_id == s1_id
    except (KeyError, ValueError, TypeError):
        return False


def extract_normalized_endpoint_surface(
    summary: Dict[str, Any],
    authority_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Extract and normalize endpoint surface from S2-B authority summary and detail.

    Consumes BOTH s2_v2_b_authority_summary.json and s2_v2_b_authority.json.
    Enforces strict 1-to-1 endpoint correspondence and rejects duplicates.
    Returns sorted list by target_port.
    """
    raw_surface = summary.get("classified_endpoint_surface") or summary.get(
        "classified_surface", []
    )
    auth_index: Dict[str, Dict[str, Any]] = {}
    if authority_data:
        auth_index = build_authority_index(authority_data)
        if len(auth_index) != len(raw_surface):
            raise ValueError(
                f"Cardinality mismatch between summary ({len(raw_surface)}) "
                f"and authority evaluations ({len(auth_index)})"
            )

    normalized: List[Dict[str, Any]] = []

    for ep in raw_surface:
        raw_key = ep.get("endpoint_key")
        canonical_id = canonical_endpoint_key(raw_key)

        # Ingest from authority_data record if available
        if authority_data and canonical_id not in auth_index:
            raise ValueError(
                f"Endpoint {canonical_id} in summary missing from authority evaluations"
            )
        auth_record = auth_index.get(canonical_id, {})

        if "target_port" in ep:
            port = int(ep["target_port"])
        elif "probe_target" in ep:
            port = int(ep["probe_target"].split(":")[-1])
        elif raw_key and len(raw_key) > 1:
            port = int(raw_key[1].split(":")[-1])
        else:
            raise ValueError(f"Cannot extract port from endpoint: {ep}")

        # Authority verdict and reachability from detail (with summary fallback)
        auth_verdict = (
            auth_record.get("authority_verdict")
            or ep.get("authority_verdict")
            or ep.get("authority_classification")
            or "UNKNOWN"
        )

        reachability = ep.get("reachability_classification")
        if not reachability:
            reachability = (
                "UNREACHABLE"
                if auth_verdict in ("UNREACHABLE", "NON_REACHABLE")
                else "REACHABLE"
            )

        # Authority path identity: must be structured dict if present, None otherwise.
        # STRICT: NO SYNTHETIC FILLING.
        auth_path = auth_record.get("authority_path_identity") or ep.get(
            "authority_path_identity"
        )
        if auth_path is not None and not isinstance(auth_path, dict):
            # Reject non-dict representations as unverified/non-structured
            auth_path = None

        tx_dict = auth_record.get("transactions") or {}
        atk_mut = tx_dict.get("attack_mutation") or {}
        tx_provenance = (
            auth_record.get("transaction_route_provenance")
            or atk_mut.get("route_provenance")
        )

        target_ip = ep.get("target_ip")
        if not target_ip:
            probe_tgt = auth_record.get("probe_target") or ep.get("probe_target")
            if probe_tgt:
                target_ip = probe_tgt.split(":")[0]
            else:
                target_ip = "127.0.0.1"

        entry = {
            "canonical_endpoint_id": canonical_id,
            "endpoint_key": raw_key,
            "target_port": port,
            "target_ip": target_ip,
            "reachability_classification": reachability,
            "authority_classification": auth_verdict,
            "authority_path_identity": auth_path,  # None if missing, NEVER synthetic
            "transaction_route_provenance": tx_provenance,
            "attack_mutation_recorded": bool(atk_mut),
        }
        normalized.append(entry)

    return sorted(normalized, key=lambda x: int(x["target_port"]))


def endpoint_surface_digest(surface: List[Dict[str, Any]]) -> str:
    """Compute a deterministic digest over the normalized endpoint surface.

    Sorts by target_port to ensure exact order invariance.
    Projects the immutable classification core fields.
    """
    projected = [
        {
            "target_port": int(x["target_port"]),
            "target_ip": x.get("target_ip", "127.0.0.1"),
            "reachability_classification": x.get("reachability_classification"),
            "authority_classification": x.get("authority_classification"),
            "authority_path_identity": x.get("authority_path_identity"),
        }
        for x in surface
    ]
    sorted_surface = sorted(projected, key=lambda x: int(x["target_port"]))
    payload = json.dumps(
        sorted_surface,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_canonical_git_snapshot(
    anchor_path: Path,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Verify that all tracked artifacts match their Git commit snapshot.

    Returns:
        (is_valid, reason, audit_details)
    """
    anchor_file = Path(anchor_path).resolve()
    if not anchor_file.exists():
        return False, f"Anchor file does not exist: {anchor_file}", {}

    try:
        anchor_data = json.loads(anchor_file.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Malformed anchor JSON: {e}", {}

    provenance_class = anchor_data.get("provenance_class")
    if provenance_class != "CANONICAL_GIT_SNAPSHOT":
        return (
            False,
            f"Invalid provenance_class: {provenance_class} (expected CANONICAL_GIT_SNAPSHOT)",
            {},
        )

    frozen_commit = anchor_data.get("frozen_commit")
    if not frozen_commit:
        return False, "Missing frozen_commit in anchor", {}

    tracked_artifacts = anchor_data.get("tracked_artifacts", {})
    if not tracked_artifacts:
        return False, "No tracked_artifacts defined in anchor", {}

    try:
        git_root = _find_git_root(anchor_file)
    except Exception as e:
        return False, f"Git repository discovery failed: {e}", {}

    audit_records: Dict[str, Any] = {}

    for repo_rel_path, spec in tracked_artifacts.items():
        expected_sha256 = spec.get("sha256")
        expected_blob_sha = spec.get("git_blob_sha1")
        if not expected_sha256 or not expected_blob_sha:
            return (
                False,
                f"Missing expected hashes for artifact: {repo_rel_path}",
                {},
            )

        disk_file = git_root / repo_rel_path
        if not disk_file.exists():
            return False, f"Tracked artifact missing on disk: {disk_file}", {}

        # 1. Disk bytes verification
        disk_bytes = disk_file.read_bytes()
        disk_sha256 = hashlib.sha256(disk_bytes).hexdigest()
        if disk_sha256 != expected_sha256:
            return (
                False,
                f"Disk SHA-256 mismatch for {repo_rel_path}: got {disk_sha256}, expected {expected_sha256}",
                {},
            )

        # 2. Git commit snapshot verification
        try:
            git_bytes = _git_show_blob(git_root, frozen_commit, repo_rel_path)
        except Exception as e:
            return False, f"Git snapshot read failed for {repo_rel_path}: {e}", {}

        git_sha256 = hashlib.sha256(git_bytes).hexdigest()
        if git_sha256 != expected_sha256:
            return (
                False,
                f"Git snapshot SHA-256 mismatch for {repo_rel_path}: got {git_sha256}, expected {expected_sha256}",
                {},
            )

        # 3. Git blob SHA-1 verification
        try:
            actual_blob_sha = _git_rev_parse_blob(
                git_root, frozen_commit, repo_rel_path
            )
        except Exception as e:
            return (
                False,
                f"Git blob rev-parse failed for {repo_rel_path}: {e}",
                {},
            )

        if actual_blob_sha != expected_blob_sha:
            return (
                False,
                f"Git blob SHA-1 mismatch for {repo_rel_path}: got {actual_blob_sha}, expected {expected_blob_sha}",
                {},
            )

        # 4. Working tree vs Git commit byte-for-byte exact equality
        if disk_bytes != git_bytes:
            return (
                False,
                f"Working-tree byte mismatch against Git snapshot for {repo_rel_path}",
                {},
            )

        audit_records[repo_rel_path] = {
            "status": "CANONICAL_GIT_VERIFIED",
            "disk_sha256": disk_sha256,
            "git_blob_sha1": actual_blob_sha,
            "byte_count": len(disk_bytes),
        }

    return (
        True,
        "All tracked artifacts match Git snapshot and local disk identically",
        {
            "frozen_commit": frozen_commit,
            "provenance_class": provenance_class,
            "artifacts_verified": audit_records,
        },
    )
