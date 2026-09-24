# -*- coding: utf-8 -*-
"""
T0 Clean Installation and Dependency Reproducibility Test Suite.
Verifies schemas, environment manifests, and adapter bootstrapping without undocumented dependencies.
"""

import os
import json
import pytest
from drone.validator import (
    EXECUTION_REQUEST_SCHEMA,
    DRONE_POSTURE_SCHEMA,
    PROVENANCE_SCHEMA,
    SAFETY_STATE_SCHEMA,
    validate_execution_request
)
from drone.sitl.engine import PX4SITLEngine, ExternalNavigationIntegrityService
from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_t0_01_baseline_manifest_frozen():
    manifest_path = os.path.join(BASE_DIR, "DRONE_BASELINE_MANIFEST.json")
    assert os.path.exists(manifest_path), "DRONE_BASELINE_MANIFEST.json must exist"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("frozen") is True, "Baseline manifest must be frozen"
    assert data.get("px4_version"), "PX4 version must be documented"
    assert data.get("mavlink_version"), "MAVLink version must be documented"
    assert data.get("python_version"), "Python version must be documented"

def test_t0_02_schemas_validity():
    assert EXECUTION_REQUEST_SCHEMA["title"] == "DroneExecutionRequest"
    assert DRONE_POSTURE_SCHEMA["title"] == "DroneRuntimePosture"
    assert PROVENANCE_SCHEMA["title"] == "DroneProvenance"
    assert SAFETY_STATE_SCHEMA["title"] == "DroneSafetyState"

def test_t0_03_clean_adapter_bootstrap():
    sitl = PX4SITLEngine()
    adapter = DroneExecutionAdapter(sitl_engine=sitl)
    assert adapter is not None
    assert sitl.armed is False
    assert sitl.flight_mode == "STANDBY"
