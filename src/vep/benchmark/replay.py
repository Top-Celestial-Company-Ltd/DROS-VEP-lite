# -*- coding: utf-8 -*-
"""
VEP Deterministic Replay Engine.
Replays a recorded execution request from an experiment artifact.
Validates decision, arguments_hash, and deterministic matching without re-sampling random inputs.
"""

import os
import json
from typing import Dict, Any, Optional

from vep.schema import CanonicalExecutionRequest, CanonicalExecutionResult
from vep.adapters.base import BaseSubstrateAdapter


class VepReplayEngine:
    def __init__(self, reports_base_dir: str = "reports/benchmarks/post_compromise"):
        self.reports_base_dir = reports_base_dir

    def replay_experiment(
        self,
        experiment_id: str,
        adapter_map: Dict[str, BaseSubstrateAdapter],
        target_request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        exp_dir = os.path.join(self.reports_base_dir, experiment_id)
        if not os.path.exists(exp_dir):
            raise FileNotFoundError(f"Experiment artifact not found at {exp_dir}")

        log_path = os.path.join(exp_dir, "execution.jsonl")
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"Execution trace not found at {log_path}")

        records = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))

        replay_results = []
        all_matched = True

        for rec in records:
            req_data = rec["request"]
            res_data = rec["result"]
            sub_name = res_data["substrate"]

            if target_request_id and req_data["request_id"] != target_request_id:
                continue

            adapter = adapter_map.get(sub_name)
            if not adapter:
                continue

            # Reconstruct canonical request
            req = CanonicalExecutionRequest.from_dict(req_data)

            # Replay evaluation
            replayed_result = adapter.replay(req, res_data.get("evidence", {}))

            # Match decisions
            is_decision_match = (replayed_result.decision.value == res_data["decision"])
            is_exec_match = (replayed_result.execution.value == res_data["execution"])
            is_hash_match = (req.arguments_hash == res_data["evidence"].get("arguments_hash"))

            match = is_decision_match and is_exec_match and is_hash_match
            if not match:
                all_matched = False

            replay_results.append({
                "request_id": req.request_id,
                "substrate": sub_name,
                "recorded_decision": res_data["decision"],
                "replayed_decision": replayed_result.decision.value,
                "recorded_execution": res_data["execution"],
                "replayed_execution": replayed_result.execution.value,
                "arguments_hash": req.arguments_hash,
                "deterministic_match": match,
            })

        return {
            "experiment_id": experiment_id,
            "total_replayed": len(replay_results),
            "deterministic_match_all": all_matched,
            "replays": replay_results,
        }
