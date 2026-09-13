# -*- coding: utf-8 -*-
"""
VEP Canonical Scenario Definition and Loader.
Supports single-attempt scenarios and two-phase scenarios (e.g. PC-009 Replay).
Automatically computes arguments_hash and transforms YAML into CanonicalExecutionRequest.
"""

import os
import yaml
import uuid
import time
from typing import Dict, Any, List, Optional
from vep.schema import CanonicalExecutionRequest


SCENARIO_TO_PROPERTY = {
    "PC-001": "RESOURCE_AUTHORITY",
    "PC-002": "RESOURCE_AUTHORITY",
    "PC-003": "PRIVILEGE_ESCALATION",
    "PC-004": "TOOL_ATTRIBUTION",
    "PC-005": "ARGUMENT_INTEGRITY",
    "PC-006": "SCOPE_NON_EXPANSION",
    "PC-007": "TEMPORAL_AUTHORITY",
    "PC-008": "TEMPORAL_AUTHORITY",
    "PC-009": "EXECUTION_UNIQUENESS",
    "PC-010": "PRINCIPAL_ATTRIBUTION",
}


class CanonicalScenario:
    def __init__(self, raw_data: Dict[str, Any], filepath: str):
        self.raw_data = raw_data
        self.filepath = filepath
        self.scenario_id = raw_data.get("id", os.path.splitext(os.path.basename(filepath))[0])
        self.name = raw_data.get("name", self.scenario_id)
        self.description = raw_data.get("description", "")
        self.target_property = raw_data.get("target_property", "")
        self.canonical_property = SCENARIO_TO_PROPERTY.get(self.scenario_id, "GENERAL_EXECUTION_GOVERNANCE")
        self.mitre_atlas = raw_data.get("mitre_atlas", "")
        self.is_two_phase = "first_request" in raw_data and "replay_request" in raw_data

    def get_requests(self) -> List[CanonicalExecutionRequest]:
        """Converts the scenario specification into canonical execution requests."""
        if self.is_two_phase:
            req1 = self._build_request(self.raw_data["first_request"], suffix="-first")
            req2 = self._build_request(self.raw_data["replay_request"], suffix="-replay")
            return [req1, req2]
        else:
            req = self._build_request(self.raw_data.get("attempt", self.raw_data))
            return [req]

    def _build_request(self, data: Dict[str, Any], suffix: str = "") -> CanonicalExecutionRequest:
        req_id = data.get("request_id") or f"{self.scenario_id}-{uuid.uuid4().hex[:8]}{suffix}"
        principal = data.get("principal", "agent-support")
        task = data.get("task", f"task-{self.scenario_id}")
        tool = data.get("tool", "unknown_tool")
        action = data.get("action", "execute")
        resource = data.get("resource", "")
        arguments = data.get("arguments", {})
        requested_capability = data.get("requested_capability", f"{tool}.{action}")
        auth_context = data.get("authorization_context", {})
        timestamp = data.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        compromise_state = data.get("compromise_state", "POST_COMPROMISE")

        return CanonicalExecutionRequest(
            request_id=req_id,
            principal=principal,
            task=task,
            tool=tool,
            action=action,
            resource=resource,
            arguments=arguments,
            requested_capability=requested_capability,
            authorization_context=auth_context,
            timestamp=timestamp,
            compromise_state=compromise_state,
        )


def load_scenario(filepath: str) -> CanonicalScenario:
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return CanonicalScenario(data, filepath)


def load_all_scenarios(scenarios_dir: str) -> List[CanonicalScenario]:
    scenarios = []
    if not os.path.exists(scenarios_dir):
        return scenarios
    for root, _, files in os.walk(scenarios_dir):
        for f in sorted(files):
            if f.endswith(".yaml") or f.endswith(".yml"):
                p = os.path.join(root, f)
                try:
                    scenarios.append(load_scenario(p))
                except Exception as e:
                    print(f"[!] Warning: failed to parse scenario {p}: {e}")
    return scenarios
