# -*- coding: utf-8 -*-
"""
Canonical Runner for Milestone M1.1 S2-A (Canonical v2.1).
Purpose:
  - Execute exactly one canonical S2-A test.
  - Preserve runner/test stdout and exit status.
  - Independently verify raw kernel observation integrity.
  - Independently verify canonical stage and discovery method.
  - Avoid hardcoded ingress topology.
  - Avoid synthesizing discovered inventory.
  - Produce a machine-generated audit summary.
The runner does NOT determine which ports "should" exist.
"""
import hashlib
import json
import os
import subprocess
import time
REPO_DIR = "/home/ai_user/dros_drone_real"
TEST_FILE = (
    "tests/drone/s2_v2/"
    "test_s2_v2_a_discovery.py"
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
ARTIFACT_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_discovery.json",
)
RAW_LOG_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_kernel_ss_raw.log",
)
STDOUT_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_discovery.stdout.log",
)
EXIT_CODE_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_discovery.exit_code",
)
INVENTORY_PATH = os.path.join(
    EVIDENCE_DIR,
    "s2_v2_a_discovery_inventory.json",
)
CANONICAL_STAGE = (
    "M1.1-S2-A (Canonical v2.1)"
)
CANONICAL_DISCOVERY_METHOD = (
    "DYNAMIC_KERNEL_AUDIT_WITHOUT_PREDEFINED_PORT_LIST"
)
os.makedirs(
    EVIDENCE_DIR,
    exist_ok=True,
)
def utc_timestamp():
    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(),
    )
def compute_sha256(filepath: str) -> str:
    digest = hashlib.sha256()
    with open(
        filepath,
        "rb",
    ) as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
def remove_stale_artifact(path: str):
    """
    Stale canonical artifacts must never silently survive
    into a new run.
    """
    if os.path.exists(path):
        os.remove(path)
# Remove only this stage's generated outputs.
for stale_path in [
    ARTIFACT_PATH,
    RAW_LOG_PATH,
    STDOUT_PATH,
    EXIT_CODE_PATH,
    INVENTORY_PATH,
]:
    remove_stale_artifact(stale_path)
test_path = os.path.join(
    REPO_DIR,
    TEST_FILE,
)
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
software_attestation = {
    "test_suite_path": test_path,
    "test_suite_sha256": compute_sha256(
        test_path
    ),
    "runner_path": runner_path,
    "runner_sha256": compute_sha256(
        runner_path
    ),
}
px4_binary_attestation = {
    "path": PX4_BIN_PATH,
    "sha256": compute_sha256(
        PX4_BIN_PATH
    ),
}
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
with open(
    STDOUT_PATH,
    "w",
    encoding="utf-8",
) as f:
    f.write(res.stdout)
    if res.stderr:
        f.write(
            "\n=== STDERR ===\n"
        )
        f.write(res.stderr)
with open(
    EXIT_CODE_PATH,
    "w",
    encoding="utf-8",
) as f:
    f.write(
        f"{res.returncode}\n"
    )
artifact_data = {}
if os.path.exists(
    ARTIFACT_PATH
):
    try:
        with open(
            ARTIFACT_PATH,
            "r",
            encoding="utf-8",
        ) as f:
            artifact_data = json.load(f)
    except Exception:
        artifact_data = {}
kernel_obs = artifact_data.get(
    "kernel_observation",
    {},
)
recorded_raw_file = kernel_obs.get(
    "raw_stdout_file",
    "",
)
recorded_raw_hash = kernel_obs.get(
    "raw_stdout_sha256",
    "")
recorded_raw_returncode = kernel_obs.get(
    "returncode",
    None,
)
raw_file_exists = os.path.exists(
    RAW_LOG_PATH
)
raw_hash_matches = False
if (
    raw_file_exists
    and recorded_raw_hash
):
    raw_hash_matches = (
        compute_sha256(
            RAW_LOG_PATH
        )
        == recorded_raw_hash
    )
raw_file_path_matches = (
    recorded_raw_file
    == RAW_LOG_PATH
)
raw_observation_valid = (
    raw_file_exists
    and raw_hash_matches
    and raw_file_path_matches
    and recorded_raw_returncode == 0
)
discovered_endpoints = artifact_data.get(
    "discovered_endpoints",
    [],
)
discovered_count = len(
    discovered_endpoints
)
artifact_count = artifact_data.get(
    "discovered_endpoints_count"
)
count_consistent = (
    isinstance(
        artifact_count,
        int,
    )
    and artifact_count
    == discovered_count
    and discovered_count > 0
)
stage_valid = (
    artifact_data.get("stage")
    == CANONICAL_STAGE
)
method_valid = (
    artifact_data.get(
        "discovery_method"
    )
    == CANONICAL_DISCOVERY_METHOD
)
px4_pid_valid = isinstance(
    artifact_data.get(
        "px4_pid"
    ),
    int,
)
epistemic_boundary_valid = (
    "execution authority"
    in artifact_data.get(
        "epistemic_boundary",
        ""
    ).lower()
    and "S2-B"
    in artifact_data.get(
        "epistemic_boundary",
        ""
    )
)
pytest_pass = (
    res.returncode == 0
)
p_dynamic_discovery = all(
    [
        pytest_pass,
        os.path.exists(
            ARTIFACT_PATH
        ),
        raw_observation_valid,
        stage_valid,
        method_valid,
        px4_pid_valid,
        count_consistent,
        epistemic_boundary_valid,
    ]
)
summary = {
    "evidence_type": (
        "machine_generated_dynamic_discovery_summary"
    ),
    "milestone_stage": CANONICAL_STAGE,
    "timestamp_iso": utc_timestamp(),
    "execution_window": {
        "started_at_iso": started_at,
        "finished_at_iso": finished_at,
        "duration_seconds": round(
            duration,
            3,
        ),
    },
    "test_suite": TEST_FILE,
    "software_attestation": software_attestation,
    "px4_binary_attestation": (
        px4_binary_attestation
    ),
    "runner_execution": {
        "exit_code": res.returncode,
        "status": (
            "PASS"
            if p_dynamic_discovery
            else "FAIL"
        ),
    },
    "provenance_attestation": {
        "raw_kernel_observation_file": (
            RAW_LOG_PATH
        ),
        "raw_kernel_observation_file_recorded": (
            recorded_raw_file
        ),
        "raw_kernel_observation_sha256": (
            recorded_raw_hash
        ),
        "raw_hash_verified_by_runner": (
            raw_hash_matches
        ),
        "raw_file_path_verified_by_runner": (
            raw_file_path_matches
        ),
        "kernel_command": kernel_obs.get(
            "command"
        ),
        "kernel_returncode": (
            recorded_raw_returncode
        ),
        "kernel_stderr": kernel_obs.get(
            "stderr",
            "",
        ),
        "raw_observation_valid": (
            raw_observation_valid
        ),
    },
    "dynamic_discovery_predicate": {
        "predicate_name": (
            "P_DYNAMIC_KERNEL_SOCKET_DISCOVERY"
        ),
        "stage_valid": stage_valid,
        "discovery_method_valid": method_valid,
        "px4_pid_valid": px4_pid_valid,
        "count_consistent": count_consistent,
        "epistemic_boundary_valid": (
            epistemic_boundary_valid
        ),
        "discovered_endpoints_count": (
            discovered_count
        ),
        "protocol_observed_count": sum(
            1
            for endpoint
            in discovered_endpoints
            if endpoint.get(
                "protocol_observed"
            )
            is True
        ),
        "derived_verdict": (
            "PASS"
            if p_dynamic_discovery
            else "FAIL"
        ),
    },
    "empirically_discovered_surface": [
        {
            "endpoint_key": endpoint.get(
                "endpoint_key"
            ),
            "discovered_local_endpoint": (
                endpoint.get(
                    "discovered_local_endpoint"
                )
            ),
            "discovered_peer_endpoint": (
                endpoint.get(
                    "discovered_peer_endpoint"
                )
            ),
            "host": endpoint.get(
                "host"
            ),
            "port": endpoint.get(
                "port"
            ),
            "state": endpoint.get(
                "state"
            ),
            "owner_pid": endpoint.get(
                "owner_pid"
            ),
            "protocol_observed": endpoint.get(
                "protocol_observed"
            ),
            "probe_target": endpoint.get(
                "protocol_liveness",
                {},
            ).get(
                "probe_target"
            ),
            "address_family": endpoint.get(
                "protocol_liveness",
                {},
            ).get(
                "address_family"
            ),
            "observed_message_types": endpoint.get(
                "protocol_liveness",
                {},
            ).get(
                "observed_message_types",
                [],
            ),
        }
        for endpoint
        in discovered_endpoints
    ],
    "claim_boundary": (
        "Within the tested PX4 SITL execution surface, "
        "PX4-attributed UDP endpoints were dynamically "
        "identified from a complete kernel `ss` observation "
        "without a predefined ingress-port list. "
        "Protocol liveness observations are reported "
        "separately; execution authority is not inferred "
        "by S2-A and is reserved for S2-B."
    ),
}
with open(
    INVENTORY_PATH,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        summary,
        f,
        indent=2,
        ensure_ascii=False,
    )
print(
    "S2_V2_A_DISCOVERY_COMPLETED: "
    f"returncode={res.returncode}, "
    f"discovered_count={discovered_count}, "
    f"duration={duration:.3f}s, "
    f"predicate="
    f"{'PASS' if p_dynamic_discovery else 'FAIL'}"
)
