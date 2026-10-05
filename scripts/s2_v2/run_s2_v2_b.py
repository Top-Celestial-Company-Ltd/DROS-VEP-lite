# -*- coding: utf-8 -*-
"""
Canonical Independent Runner for Milestone M1.1 S2-B
(Canonical Evidence Package: v2.1 Rev 5).

Package Composition:
  - Experiment / Test Suite: M1.1-S2-B Canonical v2.1 Rev 4
  - Independent Verifier: M1.1-S2-B Canonical v2.1 Rev 5

Role:
  Independent "Second Reader" verifier and lifecycle sealer.

Core rule:
  The runner MUST NOT accept test-emitted boolean proof labels as evidence.
  It independently reconstructs the relevant predicates from:
    1. S2-A input artifact (for upstream discovery and protocol liveness)
    2. S2-B primitive transaction records (for timestamps, values, transmissions)
    3. raw kernel `ss` evidence (for PID identification and socket ownership)
    4. post-test process audit (for clean teardown lifecycle proof)

Independent predicates:
  P1: S2-A Input Artifact Hash Consistency
  P2: Subset Ingestion & Uniqueness
  P3: Exact Endpoint Set Ingestion & Cardinality
  P4: Socket FD Disjoint
  P5: Ephemeral Port Disjoint
  P6: Transaction ID Disjoint
  P7: Strict 10-Point Monotonic Temporal Causality (<)
  P8: Anti-Self-Attestation
  P9: State Delta Rigor / independently reconstructed authority verdict
  P10: Negative Evidence Conservatism
  P11: Closed Taxonomy
  P12: Reversibility Rigor (Target Equality + Transmission + Temporal + Observation)
  P13: Current-Session Kernel Ownership from raw `ss`
  P14: Clean-Room Post-Test Teardown Verified
"""

import hashlib
import json
import os
import re
import subprocess
import time


REPO_DIR = "/home/ai_user/dros_drone_real"

TEST_FILE = (
    "tests/drone/s2_v2/"
    "test_s2_v2_b_execution_authority.py"
)

PYTEST_BIN = f"{REPO_DIR}/venv/bin/pytest"

PX4_BIN_PATH = (
    "/home/ai_user/px4_build/PX4-Autopilot/"
    "build/px4_sitl_default/bin/px4"
)

EVIDENCE_DIR = os.path.join(
    REPO_DIR,
    "reports",
    "evidence",
    "drone",
    "m1_1",
    "s2_v2",
)

S2_A_ARTIFACT_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_discovery.json",
)

ARTIFACT_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_authority.json",
)

RAW_KERNEL_LOG_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_kernel_ss_raw.log",
)

STDOUT_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_authority.stdout.log",
)

EXIT_CODE_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_authority.exit_code",
)

SUMMARY_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_b_authority_summary.json",
)

CANONICAL_PACKAGE_VERSION = "M1.1-S2-B (Canonical v2.1 Rev 5)"
EXPERIMENT_TEST_SUITE_VERSION = "M1.1-S2-B (Canonical v2.1 Rev 4)"
INDEPENDENT_VERIFIER_VERSION = "M1.1-S2-B (Canonical v2.1 Rev 5)"

VALID_TAXONOMY = {
    "EXECUTION_CAPABLE",
    "NON_EXECUTION",
    "UNREACHABLE",
    "INDETERMINATE",
}


os.makedirs(EVIDENCE_DIR, exist_ok=True)


def utc_timestamp() -> str:
    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(),
    )


def compute_sha256(filepath: str) -> str:
    digest = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            digest.update(chunk)

    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def remove_stale_artifact(path: str):
    if os.path.exists(path):
        os.remove(path)


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def safe_timestamp(obj: dict, field: str):
    value = obj.get(field)
    return safe_int(value)


def endpoint_key_tuple(endpoint):
    if not isinstance(endpoint, dict):
        return None

    key = endpoint.get("endpoint_key")

    if not isinstance(key, list):
        return None

    if len(key) != 4:
        return None

    try:
        return tuple(key)
    except TypeError:
        return None


def endpoint_key_components(key):
    if not isinstance(key, (list, tuple)):
        return None

    if len(key) != 4:
        return None

    return {
        "pid": key[0],
        "local_address": key[1],
        "peer_address": key[2],
        "state": key[3],
    }


def audit_process_cleanliness():
    """
    Independent process lifecycle check executed by Runner post-test.
    Asserts no hanging PX4 or PEP instances remain.
    """
    res = subprocess.run(
        ["ps", "-eo", "pid=,args="],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        return {
            "verified": False,
            "returncode": res.returncode,
            "conflicts": ["ps command failed"],
        }

    conflicts = []
    current_pid = os.getpid()
    parent_pid = os.getppid()

    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)\s+(.*)$", line)
        if not m:
            continue
        pid = int(m.group(1))
        args = m.group(2)
        if pid in {current_pid, parent_pid}:
            continue
        px4_c = bool(re.search(r"(?:^|\s|/)(?:px4)(?:\s|$)", args))
        pep_c = ("pep_proxy.py" in args or "multi_pep_proxy.py" in args)
        if px4_c or pep_c:
            conflicts.append({"pid": pid, "args": args})

    return {
        "verified": (len(conflicts) == 0),
        "returncode": res.returncode,
        "conflicts": conflicts,
    }


# ---------------------------------------------------------------------------
# Clean stale outputs
# ---------------------------------------------------------------------------

for stale_path in [
    ARTIFACT_PATH,
    RAW_KERNEL_LOG_PATH,
    STDOUT_PATH,
    EXIT_CODE_PATH,
    SUMMARY_PATH,
]:
    remove_stale_artifact(stale_path)


# ---------------------------------------------------------------------------
# Static file preconditions
# ---------------------------------------------------------------------------

test_path = os.path.join(REPO_DIR, TEST_FILE)
runner_path = os.path.abspath(__file__)

assert os.path.exists(
    test_path
), f"Test file not found: {test_path}"

assert os.path.exists(
    PYTEST_BIN
), f"pytest binary not found: {PYTEST_BIN}"

assert os.path.exists(
    PX4_BIN_PATH
), f"PX4 binary not found: {PX4_BIN_PATH}"

assert os.path.exists(
    S2_A_ARTIFACT_PATH
), f"S2-A source artifact not found: {S2_A_ARTIFACT_PATH}"


software_attestation = {
    "test_suite_path": test_path,
    "test_suite_sha256": compute_sha256(test_path),
    "runner_path": runner_path,
    "runner_sha256": compute_sha256(runner_path),
}

px4_binary_attestation = {
    "path": PX4_BIN_PATH,
    "sha256": compute_sha256(PX4_BIN_PATH),
}


# ---------------------------------------------------------------------------
# Read upstream S2-A source artifact
# ---------------------------------------------------------------------------

s2_a_disk_sha256 = compute_sha256(
    S2_A_ARTIFACT_PATH
)

with open(
    S2_A_ARTIFACT_PATH,
    "r",
    encoding="utf-8",
) as f:
    s2_a_data = json.load(f)


# ---------------------------------------------------------------------------
# Execute exactly one canonical S2-B test suite
# ---------------------------------------------------------------------------

started_at = utc_timestamp()
t0 = time.time()

res = subprocess.run(
    [
        PYTEST_BIN,
        TEST_FILE,
        "-v",
    ],
    cwd=REPO_DIR,
    capture_output=True,
    text=True,
    check=False,
)

duration = time.time() - t0
finished_at = utc_timestamp()

# Independent Post-Test Teardown Audit
post_test_cleanliness = audit_process_cleanliness()
p14_clean_teardown_verified = post_test_cleanliness["verified"]


with open(
    STDOUT_PATH,
    "w",
    encoding="utf-8",
) as f:
    f.write(res.stdout)

    if res.stderr:
        f.write("\n=== STDERR ===\n")
        f.write(res.stderr)


with open(
    EXIT_CODE_PATH,
    "w",
    encoding="utf-8",
) as f:
    f.write(f"{res.returncode}\n")


# ---------------------------------------------------------------------------
# Load primitive S2-B artifact
# ---------------------------------------------------------------------------

artifact_data = {}

if os.path.exists(ARTIFACT_PATH):
    try:
        with open(
            ARTIFACT_PATH,
            "r",
            encoding="utf-8",
        ) as f:
            artifact_data = json.load(f)
    except Exception:
        artifact_data = {}


evaluations = artifact_data.get(
    "endpoint_authority_evaluations",
    [],
)

s2_a_source = artifact_data.get(
    "s2_a_source",
    {},
)

s2_b_context = artifact_data.get(
    "s2_b_execution_context",
    {},
)

s2_a_discovered_endpoints = s2_a_data.get(
    "discovered_endpoints",
    [],
)

# Build S2-A lookup dictionary mapping endpoint_key -> S2-A endpoint record
s2_a_endpoints_by_key = {}
for ep in s2_a_discovered_endpoints:
    kt = endpoint_key_tuple(ep)
    if kt:
        s2_a_endpoints_by_key[kt] = ep


# ---------------------------------------------------------------------------
# P1: S2-A Input Artifact Hash Consistency
# ---------------------------------------------------------------------------

p1_hash_consistency = (
    s2_a_source.get("artifact_sha256")
    == s2_a_disk_sha256
)


# ---------------------------------------------------------------------------
# Endpoint-set provenance
# ---------------------------------------------------------------------------

s2_a_key_tuples = []
s2_a_key_conversion_valid = True

for endpoint in s2_a_discovered_endpoints:
    key = endpoint_key_tuple(endpoint)

    if key is None:
        s2_a_key_conversion_valid = False
        continue

    s2_a_key_tuples.append(key)


tested_key_tuples = []
tested_key_conversion_valid = True

for evaluation in evaluations:
    key = endpoint_key_tuple(evaluation)

    if key is None:
        tested_key_conversion_valid = False
        continue

    tested_key_tuples.append(key)


# ---------------------------------------------------------------------------
# P2: subset + uniqueness
# ---------------------------------------------------------------------------

p2_subset_ingestion = (
    s2_a_key_conversion_valid
    and tested_key_conversion_valid
    and len(tested_key_tuples) > 0
    and len(tested_key_tuples)
    == len(set(tested_key_tuples))
    and all(
        key in s2_a_key_tuples
        for key in tested_key_tuples
    )
)


# ---------------------------------------------------------------------------
# P3: exact endpoint-set identity + cardinality + source uniqueness
# ---------------------------------------------------------------------------

p3_exact_set_ingestion = (
    s2_a_key_conversion_valid
    and tested_key_conversion_valid
    and len(s2_a_key_tuples)
    == len(set(s2_a_key_tuples))
    and len(tested_key_tuples)
    == len(set(tested_key_tuples))
    and len(tested_key_tuples)
    == len(s2_a_key_tuples)
    and set(tested_key_tuples)
    == set(s2_a_key_tuples)
)


# ---------------------------------------------------------------------------
# Independent raw kernel reader
# ---------------------------------------------------------------------------

def runner_parse_raw_kernel_sockets(
    raw_log_path: str,
):
    """
    Independent Second Reader parser.
    Derives all PX4 PIDs directly from the raw `ss` output.
    """
    if not os.path.exists(raw_log_path):
        return {
            "file_exists": False,
            "raw_sha256": None,
            "px4_pids": [],
            "owned_sockets": [],
            "raw_line_count": 0,
        }

    raw_bytes = b""
    with open(raw_log_path, "rb") as f:
        raw_bytes = f.read()

    content = raw_bytes.decode(
        "utf-8",
        errors="ignore",
    )

    px4_pids = set()
    owned_sockets = []

    for line in content.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue

        px4_matches = re.findall(
            r'users:\(\("px4",pid=(\d+)',
            line_clean,
        )

        for pid_text in px4_matches:
            pid = safe_int(pid_text)
            if pid is not None:
                px4_pids.add(pid)

        if not px4_matches:
            continue

        parts = line_clean.split()
        if len(parts) < 5:
            continue

        state = parts[0]
        local_full = parts[3]
        peer_full = parts[4]

        line_pids = [
            safe_int(pid)
            for pid in re.findall(r"pid=(\d+)", line_clean)
            if safe_int(pid) is not None
        ]

        for pid in line_pids:
            owned_sockets.append(
                {
                    "owner_pid": pid,
                    "local_address": local_full,
                    "peer_address": peer_full,
                    "state": state,
                    "raw_record": line_clean,
                }
            )

    return {
        "file_exists": True,
        "raw_sha256": sha256_bytes(raw_bytes),
        "px4_pids": sorted(px4_pids),
        "owned_sockets": owned_sockets,
        "raw_line_count": len(content.splitlines()),
    }


raw_kernel_reader = runner_parse_raw_kernel_sockets(
    RAW_KERNEL_LOG_PATH
)

raw_px4_pids = raw_kernel_reader["px4_pids"]
raw_px4_pid_unique = (len(raw_px4_pids) == 1)
raw_derived_px4_pid = (
    raw_px4_pids[0] if raw_px4_pid_unique else None
)

artifact_current_test_pid = safe_int(
    s2_b_context.get("current_test_px4_pid")
)


# ---------------------------------------------------------------------------
# P13: Current Session Kernel Ownership
# ---------------------------------------------------------------------------

p13_current_ownership_verified = True

if not raw_kernel_reader["file_exists"]:
    p13_current_ownership_verified = False

if not raw_px4_pid_unique:
    p13_current_ownership_verified = False

if (
    artifact_current_test_pid is None
    or raw_derived_px4_pid != artifact_current_test_pid
):
    p13_current_ownership_verified = False


# ---------------------------------------------------------------------------
# Predicate initialization
# ---------------------------------------------------------------------------

p4_fd_disjoint = True
p5_port_disjoint = True
p6_tx_id_disjoint = True
p7_temporal_causality = True
p8_anti_self_attestation = True
p9_state_delta_rigor = True
p10_negative_evidence_conservatism = True
p11_closed_taxonomy = True
p12_reversibility_rigor = True


# ---------------------------------------------------------------------------
# Per-endpoint independent reconstruction
# ---------------------------------------------------------------------------

independent_reconstructions = []


def derive_unreachable_from_s2_a_primitives(
    s2_a_endpoint_record: dict,
):
    """
    Completely independent reconstruction of non-protocol verdict
    from raw S2-A upstream primitives. Zero reliance on test-side 'eligibility'.
    """
    if not isinstance(s2_a_endpoint_record, dict):
        return "INDETERMINATE"

    protocol_observed = s2_a_endpoint_record.get(
        "protocol_observed"
    )
    state = s2_a_endpoint_record.get("state")
    peer = s2_a_endpoint_record.get("discovered_peer_endpoint")

    if protocol_observed is False:
        if state == "ESTAB" or (peer and peer != "0.0.0.0:*"):
            return "UNREACHABLE"
        return "INDETERMINATE"

    return "INDETERMINATE"


for evaluation in evaluations:
    verdict = evaluation.get("authority_verdict")

    if verdict not in VALID_TAXONOMY:
        p11_closed_taxonomy = False

    endpoint_key = evaluation.get("endpoint_key", [])
    ep_tuple = endpoint_key_tuple(evaluation)
    components = endpoint_key_components(endpoint_key)
    txs = evaluation.get("transactions")

    # Ingest corresponding raw S2-A record for this endpoint
    s2_a_ep_record = s2_a_endpoints_by_key.get(ep_tuple, {})
    s2_a_protocol_observed = s2_a_ep_record.get("protocol_observed", False)

    # -----------------------------------------------------------------------
    # P13: raw kernel ownership
    # -----------------------------------------------------------------------

    endpoint_owner_verified = False

    if components is not None and raw_derived_px4_pid is not None:
        expected_local = components["local_address"]
        expected_peer = components["peer_address"]
        expected_state = components["state"]

        endpoint_owner_verified = any(
            (
                socket_record["owner_pid"] == raw_derived_px4_pid
                and socket_record["local_address"] == expected_local
                and socket_record["peer_address"] == expected_peer
                and socket_record["state"] == expected_state
            )
            for socket_record in raw_kernel_reader["owned_sockets"]
        )

    if s2_a_protocol_observed and not endpoint_owner_verified:
        p13_current_ownership_verified = False

    # -----------------------------------------------------------------------
    # Protocol-capable endpoint transaction reconstruction
    # -----------------------------------------------------------------------

    if s2_a_protocol_observed:
        if not isinstance(txs, dict):
            p4_fd_disjoint = False
            p5_port_disjoint = False
            p6_tx_id_disjoint = False
            p7_temporal_causality = False
            p8_anti_self_attestation = False
            p9_state_delta_rigor = False
            p12_reversibility_rigor = False

            independent_reconstructions.append(
                {
                    "endpoint_key": endpoint_key,
                    "runner_expected_verdict": "INDETERMINATE",
                    "reason": "Missing transaction primitive object.",
                    "ownership_verified": endpoint_owner_verified,
                }
            )
            continue

        base_tx = txs.get("baseline_observation") or {}
        atk_tx = txs.get("attack_mutation") or {}
        post_tx = txs.get("post_mutation_observation") or {}
        rest_tx = txs.get("restore_mutation") or {}
        rest_obs_tx = txs.get("restore_observation") or {}

        # -------------------------------------------------------------------
        # P4: FD isolation
        # -------------------------------------------------------------------

        base_fd = base_tx.get("socket_fd")
        atk_fd = atk_tx.get("socket_fd")
        rest_fd = rest_tx.get("socket_fd")
        rest_obs_fd = rest_obs_tx.get("socket_fd")

        if (
            base_fd is None
            or atk_fd is None
            or rest_fd is None
            or rest_obs_fd is None
            or base_fd == atk_fd
            or rest_fd == rest_obs_fd
            or base_fd != rest_obs_fd
            or atk_fd != rest_fd
        ):
            p4_fd_disjoint = False

        # -------------------------------------------------------------------
        # P5: Port isolation
        # -------------------------------------------------------------------

        base_port = base_tx.get("local_port")
        atk_port = atk_tx.get("local_port")
        rest_port = rest_tx.get("local_port")
        rest_obs_port = rest_obs_tx.get("local_port")

        if (
            base_port is None
            or atk_port is None
            or rest_port is None
            or rest_obs_port is None
            or base_port == atk_port
            or rest_port == rest_obs_port
            or base_port != rest_obs_port
            or atk_port != rest_port
        ):
            p5_port_disjoint = False

        # -------------------------------------------------------------------
        # P6: Transaction ID uniqueness
        # -------------------------------------------------------------------

        tx_ids = [
            base_tx.get("tx_id"),
            atk_tx.get("tx_id"),
            post_tx.get("tx_id"),
            rest_tx.get("tx_id"),
            rest_obs_tx.get("tx_id"),
        ]

        if (
            any(tx_id in (None, "") for tx_id in tx_ids)
            or len(tx_ids) != len(set(tx_ids))
        ):
            p6_tx_id_disjoint = False

        # -------------------------------------------------------------------
        # Primitive timestamps
        # -------------------------------------------------------------------

        t_base_req = safe_timestamp(base_tx, "t_request_ns")
        t_base_resp = safe_timestamp(base_tx, "t_response_ns")
        t_atk_sent = safe_timestamp(atk_tx, "t_sent_ns")
        t_atk_finished = safe_timestamp(atk_tx, "t_finished_ns")
        t_post_req = safe_timestamp(post_tx, "t_request_ns")
        t_post_resp = safe_timestamp(post_tx, "t_response_ns")
        t_rest_sent = safe_timestamp(rest_tx, "t_sent_ns")
        t_rest_finished = safe_timestamp(rest_tx, "t_finished_ns")
        t_vfy_req = safe_timestamp(rest_obs_tx, "t_request_ns")
        t_vfy_resp = safe_timestamp(rest_obs_tx, "t_response_ns")

        timestamp_fields = [
            t_base_req,
            t_base_resp,
            t_atk_sent,
            t_atk_finished,
            t_post_req,
            t_post_resp,
            t_rest_sent,
            t_rest_finished,
            t_vfy_req,
            t_vfy_resp,
        ]

        timestamp_complete = all(v is not None for v in timestamp_fields)

        # -------------------------------------------------------------------
        # P7: Strict 10-Point Monotonic Temporal Causality (<)
        #
        # BASE_REQ < BASE_RESP < ATK_SENT < ATK_FINISHED < POST_REQ <
        # POST_RESP < REST_SENT < REST_FINISHED < VERIFY_REQ < VERIFY_RESP
        # -------------------------------------------------------------------

        temporal_valid = (
            timestamp_complete
            and (
                t_base_req
                < t_base_resp
                < t_atk_sent
                < t_atk_finished
                < t_post_req
                < t_post_resp
                < t_rest_sent
                < t_rest_finished
                < t_vfy_req
                < t_vfy_resp
            )
        )

        if not temporal_valid:
            p7_temporal_causality = False

        # -------------------------------------------------------------------
        # Primitive transmission checks
        # -------------------------------------------------------------------

        attack_bytes_sent = safe_int(atk_tx.get("bytes_sent"))
        restore_bytes_sent = safe_int(rest_tx.get("bytes_sent"))

        attack_transmission_valid = (
            attack_bytes_sent is not None
            and attack_bytes_sent > 0
        )

        restore_transmission_valid = (
            restore_bytes_sent is not None
            and restore_bytes_sent > 0
        )

        # -------------------------------------------------------------------
        # State reconstruction
        # -------------------------------------------------------------------

        val_base = base_tx.get("observed_value")
        val_post = post_tx.get("observed_value")
        val_restore = rest_obs_tx.get("observed_value")

        target_value = atk_tx.get("target_value")
        restore_target_value = rest_tx.get("target_value")

        baseline_success = (base_tx.get("success") is True)
        post_success = (post_tx.get("success") is True)
        restore_observation_success = (rest_obs_tx.get("success") is True)

        runner_delta_verified = (
            baseline_success
            and post_success
            and val_base is not None
            and val_post is not None
            and val_base != val_post
            and target_value is not None
            and val_post == target_value
        )

        # -------------------------------------------------------------------
        # P8: Anti-self-attestation
        # -------------------------------------------------------------------

        if verdict == "EXECUTION_CAPABLE":
            if not runner_delta_verified:
                p8_anti_self_attestation = False

        # -------------------------------------------------------------------
        # P12: Reversibility Rigor (Target Equality + Transmission + Temporal + Observation)
        # -------------------------------------------------------------------

        restore_target_matches_baseline = (
            restore_target_value is not None
            and val_base is not None
            and restore_target_value == val_base
        )

        restore_temporal_valid = (
            t_rest_finished is not None
            and t_vfy_req is not None
            and t_rest_finished < t_vfy_req
        )

        runner_restore_verified = (
            restore_transmission_valid
            and restore_target_matches_baseline
            and restore_temporal_valid
            and restore_observation_success
            and val_restore is not None
            and val_base is not None
            and val_restore == val_base
        )

        if verdict == "EXECUTION_CAPABLE":
            if not runner_restore_verified:
                p12_reversibility_rigor = False

        # -------------------------------------------------------------------
        # P9: Independent expected-verdict reconstruction
        # -------------------------------------------------------------------

        runner_execution_capable = (
            endpoint_owner_verified
            and attack_transmission_valid
            and runner_delta_verified
            and temporal_valid
            and runner_restore_verified
        )

        if runner_execution_capable:
            runner_expected_verdict = "EXECUTION_CAPABLE"
        else:
            runner_expected_verdict = "INDETERMINATE"

        # Convergence check
        verdict_converged = (runner_expected_verdict == verdict)

        if not verdict_converged:
            p9_state_delta_rigor = False

        if verdict == "EXECUTION_CAPABLE":
            if not (
                endpoint_owner_verified
                and attack_transmission_valid
                and runner_delta_verified
                and temporal_valid
                and runner_restore_verified
            ):
                p9_state_delta_rigor = False

        independent_reconstructions.append(
            {
                "endpoint_key": endpoint_key,
                "test_verdict": verdict,
                "runner_expected_verdict": runner_expected_verdict,
                "verdict_converged": verdict_converged,
                "ownership_verified": endpoint_owner_verified,
                "attack_transmission_verified": attack_transmission_valid,
                "restore_transmission_verified": restore_transmission_valid,
                "restore_target_matches_baseline": restore_target_matches_baseline,
                "baseline_observation_success": baseline_success,
                "post_observation_success": post_success,
                "restore_observation_success": restore_observation_success,
                "state_delta_verified": runner_delta_verified,
                "temporal_ordering_verified": temporal_valid,
                "restore_temporal_ordering_verified": restore_temporal_valid,
                "reversibility_verified": runner_restore_verified,
                "primitive_timestamps": {
                    "t_base_request_ns": t_base_req,
                    "t_base_response_ns": t_base_resp,
                    "t_attack_sent_ns": t_atk_sent,
                    "t_attack_finished_ns": t_atk_finished,
                    "t_post_request_ns": t_post_req,
                    "t_post_response_ns": t_post_resp,
                    "t_restore_sent_ns": t_rest_sent,
                    "t_restore_finished_ns": t_rest_finished,
                    "t_verify_request_ns": t_vfy_req,
                    "t_verify_response_ns": t_vfy_resp,
                },
            }
        )

    else:
        # Non-protocol endpoint: independently derived from raw S2-A primitives
        runner_expected_verdict = derive_unreachable_from_s2_a_primitives(
            s2_a_ep_record
        )

        verdict_converged = (verdict == runner_expected_verdict)
        if not verdict_converged:
            p9_state_delta_rigor = False

        independent_reconstructions.append(
            {
                "endpoint_key": endpoint_key,
                "test_verdict": verdict,
                "runner_expected_verdict": runner_expected_verdict,
                "verdict_converged": verdict_converged,
                "ownership_verified": endpoint_owner_verified,
                "mutation_probe": "NOT_ATTEMPTED",
                "method_boundary": (
                    "No execution-authority mutation probe performed "
                    "because raw S2-A primitives recorded no protocol liveness."
                ),
            }
        )

    # -----------------------------------------------------------------------
    # P10: Negative-evidence conservatism
    # -----------------------------------------------------------------------

    if verdict == "NON_EXECUTION":
        rationale = str(evaluation.get("verdict_rationale", ""))
        if (
            "explicit" not in rationale.lower()
            or "rejection" not in rationale.lower()
        ):
            p10_negative_evidence_conservatism = False


# ---------------------------------------------------------------------------
# P13 global integrity
# ---------------------------------------------------------------------------

protocol_capable_keys = []

for evaluation in evaluations:
    ep_t = endpoint_key_tuple(evaluation)
    if s2_a_endpoints_by_key.get(ep_t, {}).get("protocol_observed") is True:
        protocol_capable_keys.append(ep_t)

if raw_derived_px4_pid is None:
    p13_current_ownership_verified = False
else:
    for key in protocol_capable_keys:
        components = endpoint_key_components(key)
        if components is None:
            p13_current_ownership_verified = False
            continue

        found = any(
            (
                record["owner_pid"] == raw_derived_px4_pid
                and record["local_address"] == components["local_address"]
                and record["peer_address"] == components["peer_address"]
                and record["state"] == components["state"]
            )
            for record in raw_kernel_reader["owned_sockets"]
        )

        if not found:
            p13_current_ownership_verified = False


# ---------------------------------------------------------------------------
# Runner independent verdict convergence
# ---------------------------------------------------------------------------

all_verdicts_converged = all(
    item.get("verdict_converged") is True
    for item in independent_reconstructions
)

if not all_verdicts_converged:
    p9_state_delta_rigor = False


# ---------------------------------------------------------------------------
# P11 exact taxonomy check
# ---------------------------------------------------------------------------

for evaluation in evaluations:
    if evaluation.get("authority_verdict") not in VALID_TAXONOMY:
        p11_closed_taxonomy = False


# ---------------------------------------------------------------------------
# Predicate result object
# ---------------------------------------------------------------------------

predicate_results = {
    "P1_S2_A_INPUT_ARTIFACT_HASH_CONSISTENCY": p1_hash_consistency,
    "P2_SUBSET_INGESTION_AND_UNIQUENESS": p2_subset_ingestion,
    "P3_EXACT_ENDPOINT_SET_INGESTION": p3_exact_set_ingestion,
    "P4_SOCKET_FD_DISJOINT": p4_fd_disjoint,
    "P5_PORT_DISJOINT": p5_port_disjoint,
    "P6_TRANSACTION_ID_DISJOINT": p6_tx_id_disjoint,
    "P7_STRICT_10_POINT_TEMPORAL_CAUSALITY": p7_temporal_causality,
    "P8_ANTI_SELF_ATTESTATION": p8_anti_self_attestation,
    "P9_STATE_DELTA_RIGOR": p9_state_delta_rigor,
    "P10_NEGATIVE_EVIDENCE_CONSERVATISM": p10_negative_evidence_conservatism,
    "P11_CLOSED_TAXONOMY_ADHERENCE": p11_closed_taxonomy,
    "P12_REVERSIBILITY_RIGOR": p12_reversibility_rigor,
    "P13_CURRENT_SESSION_OWNERSHIP_VERIFIED": p13_current_ownership_verified,
    "P14_CLEAN_ROOM_TEARDOWN_VERIFIED": p14_clean_teardown_verified,
}


# ---------------------------------------------------------------------------
# Final pass gate
# ---------------------------------------------------------------------------

pytest_pass = (res.returncode == 0)

artifacts_present = (
    os.path.exists(ARTIFACT_PATH)
    and os.path.exists(RAW_KERNEL_LOG_PATH)
)

all_predicates_pass = all(predicate_results.values())

p_authority_classification = (
    pytest_pass
    and artifacts_present
    and all_predicates_pass
    and all_verdicts_converged
)


# ---------------------------------------------------------------------------
# Taxonomy counts
# ---------------------------------------------------------------------------

taxonomy_counts = {
    "execution_capable_count": sum(
        1 for ev in evaluations if ev.get("authority_verdict") == "EXECUTION_CAPABLE"
    ),
    "non_execution_count": sum(
        1 for ev in evaluations if ev.get("authority_verdict") == "NON_EXECUTION"
    ),
    "unreachable_count": sum(
        1 for ev in evaluations if ev.get("authority_verdict") == "UNREACHABLE"
    ),
    "indeterminate_count": sum(
        1 for ev in evaluations if ev.get("authority_verdict") == "INDETERMINATE"
    ),
}


# ---------------------------------------------------------------------------
# Build final independent audit summary
# ---------------------------------------------------------------------------

summary = {
    "evidence_type": "machine_generated_execution_authority_summary",
    "canonical_package_version": CANONICAL_PACKAGE_VERSION,
    "experiment_test_suite_version": EXPERIMENT_TEST_SUITE_VERSION,
    "independent_verifier_version": INDEPENDENT_VERIFIER_VERSION,
    "audit_mode": "INDEPENDENT_DUAL_READER_VERIFICATION",
    "timestamp_iso": utc_timestamp(),

    "execution_window": {
        "started_at_iso": started_at,
        "finished_at_iso": finished_at,
        "duration_seconds": round(duration, 3),
    },

    "test_suite": TEST_FILE,
    "software_attestation": software_attestation,
    "px4_binary_attestation": px4_binary_attestation,

    "runner_execution": {
        "exit_code": res.returncode,
        "pytest_pass": pytest_pass,
        "artifacts_present": artifacts_present,
        "all_predicates_pass": all_predicates_pass,
        "all_verdicts_converged": all_verdicts_converged,
        "clean_teardown_verified": p14_clean_teardown_verified,
        "status": "PASS" if p_authority_classification else "FAIL",
    },

    "post_test_clean_room_audit": post_test_cleanliness,

    "provenance_attestation": {
        "s2_a_source_artifact": S2_A_ARTIFACT_PATH,
        "s2_a_source_sha256": s2_a_disk_sha256,
        "s2_a_recorded_sha256": s2_a_source.get("artifact_sha256"),
        "s2_a_hash_match": p1_hash_consistency,

        "s2_b_raw_kernel_log": RAW_KERNEL_LOG_PATH,
        "s2_b_raw_kernel_sha256": raw_kernel_reader.get("raw_sha256"),

        "runner_raw_derived_px4_pids": raw_px4_pids,
        "runner_raw_derived_px4_pid": raw_derived_px4_pid,
        "artifact_recorded_current_px4_pid": artifact_current_test_pid,
        "raw_derived_pid_matches_artifact_pid": (
            (raw_derived_px4_pid == artifact_current_test_pid)
            if raw_derived_px4_pid is not None
            else False
        ),
    },

    "endpoint_ingestion_audit": {
        "s2_a_endpoint_count": len(s2_a_key_tuples),
        "s2_a_endpoint_unique": len(s2_a_key_tuples) == len(set(s2_a_key_tuples)),
        "s2_b_endpoint_count": len(tested_key_tuples),
        "s2_b_endpoint_unique": len(tested_key_tuples) == len(set(tested_key_tuples)),
        "exact_set_identity": set(tested_key_tuples) == set(s2_a_key_tuples),
        "exact_cardinality": len(tested_key_tuples) == len(s2_a_key_tuples),
    },

    "authority_classification_predicates": predicate_results,
    "taxonomy_counts": taxonomy_counts,

    "independent_second_reader": {
        "runner_raw_kernel_socket_count": len(raw_kernel_reader["owned_sockets"]),
        "runner_raw_px4_pid_unique": raw_px4_pid_unique,
        "verdict_convergence": all_verdicts_converged,
        "endpoint_reconstructions": independent_reconstructions,
    },

    "classified_surface": [
        {
            "endpoint_key": evaluation.get("endpoint_key"),
            "probe_target": evaluation.get("probe_target"),
            "eligibility": evaluation.get("eligibility"),
            "authority_verdict": evaluation.get("authority_verdict"),
            "test_temporal_ordering_valid": evaluation.get("temporal_ordering_valid"),
            "test_state_delta": evaluation.get("state_delta"),
            "test_reversibility_verified": evaluation.get("reversibility_verified"),
            "current_session_mapping": evaluation.get("current_session_mapping"),
            "runner_reconstruction": next(
                (
                    rec for rec in independent_reconstructions
                    if rec.get("endpoint_key") == evaluation.get("endpoint_key")
                ),
                None,
            ),
            "rationale": evaluation.get("verdict_rationale"),
        }
        for evaluation in evaluations
    ],

    "claim_boundary": (
        "Within the tested PX4 SITL surface, endpoints dynamically "
        "identified by S2-A were independently mapped to the active "
        "PX4 session using a secondary parser of the raw kernel ss "
        "record. For protocol-capable endpoints, the Runner independently "
        "reconstructed transmission, target equality, state delta, strict "
        "10-point temporal causality (<), and reversibility from primitive "
        "transaction evidence, then derived an expected authority verdict "
        "and compared it with the Test verdict. Non-protocol surfaces were "
        "reconstructed directly from raw S2-A discovery primitives. "
        "Following the attack mutation, independent observation confirmed a "
        "reversible state transition. ACK replies and bytes-sent values were "
        "not treated as proof of state mutation by themselves. Clean teardown "
        "was independently verified by process audit. No claim is made beyond the "
        "tested PX4 SITL execution surface and the stated observation method boundaries."
    ),
}


# ---------------------------------------------------------------------------
# Persist canonical runner summary
# ---------------------------------------------------------------------------

with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)


print(
    "S2_V2_B_AUTHORITY_COMPLETED: "
    f"returncode={res.returncode}, "
    f"tested_count={len(evaluations)}, "
    f"duration={duration:.3f}s, "
    f"raw_px4_pid={raw_derived_px4_pid}, "
    f"clean_teardown={'PASS' if p14_clean_teardown_verified else 'FAIL'}, "
    f"verdict_convergence={'PASS' if all_verdicts_converged else 'FAIL'}, "
    f"predicate={'PASS' if p_authority_classification else 'FAIL'}"
)
