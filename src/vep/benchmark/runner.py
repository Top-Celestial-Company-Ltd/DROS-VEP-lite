# -*- coding: utf-8 -*-
"""
VEP Benchmark Evidence Engine & Runner.
Executes canonical scenarios against selected substrates.
Produces:
  - experiment.json (Metadata, hashes, environment)
  - execution.jsonl (Canonical request/result pairs)
  - result.json (Aggregated metrics: UER, False Allow, Unsupported, Latency)
  - environment.json (Host platform, python version, git commit)
"""

import os
import sys
import json
import time
import uuid
import platform
import subprocess
from typing import Dict, Any, List, Optional

from vep.schema import (
    CanonicalExecutionRequest,
    CanonicalExecutionResult,
    DecisionType,
    ExecutionStatus,
    canonicalize_json,
)
from vep.adapters.base import BaseSubstrateAdapter
from vep.scenario import CanonicalScenario


class VepBenchmarkRunner:
    def __init__(self, output_base_dir: str = "reports/benchmarks/post_compromise"):
        self.output_base_dir = output_base_dir
        os.makedirs(self.output_base_dir, exist_ok=True)

    def capture_environment(self) -> Dict[str, Any]:
        git_sha = "unknown"
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
            )
            if res.returncode == 0:
                git_sha = res.stdout.strip()
        except Exception:
            pass

        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "vep_commit": git_sha,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def run_suite(
        self,
        scenarios: List[CanonicalScenario],
        adapters: List[BaseSubstrateAdapter],
        experiment_name: str = "post-compromise-m1",
    ) -> Dict[str, Any]:
        experiment_id = f"EXP-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        exp_dir = os.path.join(self.output_base_dir, experiment_id)
        os.makedirs(exp_dir, exist_ok=True)

        env_meta = self.capture_environment()
        with open(os.path.join(exp_dir, "environment.json"), "w", encoding="utf-8") as f:
            json.dump(env_meta, f, indent=2, ensure_ascii=False)

        execution_log_path = os.path.join(exp_dir, "execution.jsonl")
        executions: List[Dict[str, Any]] = []

        with open(execution_log_path, "w", encoding="utf-8") as log_file:
            for scenario in scenarios:
                requests = scenario.get_requests()
                for req in requests:
                    for adapter in adapters:
                        result = adapter.evaluate(req)
                        entry = {
                            "experiment_id": experiment_id,
                            "scenario_id": scenario.scenario_id,
                            "scenario_name": scenario.name,
                            "security_property": scenario.canonical_property,
                            "request": req.to_dict(),
                            "result": result.to_dict(),
                        }
                        executions.append(entry)
                        log_file.write(canonicalize_json(entry) + "\n")
                        log_file.flush()

        # Compute scientific metrics per substrate
        metrics_by_substrate: Dict[str, Any] = {}
        for adapter in adapters:
            sub_name = adapter.name
            sub_execs = [e for e in executions if e["result"]["substrate"] == sub_name]
            total_attempts = len(sub_execs)

            # Disaggregate attempts: nominal legitimate requests vs unauthorized attempts
            unauthorized_attempts = 0
            unauthorized_executions = 0
            nominal_attempts = 0
            nominal_executions = 0
            unsupported_cnt = 0
            error_cnt = 0
            replay_rejections = 0
            replay_attempts = 0
            latencies_ns = []

            for item in sub_execs:
                res = item["result"]
                req = item["request"]
                latencies_ns.append(res.get("latency_ns", 0))

                # Detect if this attempt is nominal or unauthorized
                # e.g., PC-009 initial phase is nominal/authorized; all others or replayed are unauthorized
                is_replay_phase = req["authorization_context"].get("replayed", False)
                is_nominal = (req["request_id"].endswith("-first") or req["request_id"].endswith("-INITIAL"))

                if is_replay_phase:
                    replay_attempts += 1
                    if res["decision"] == DecisionType.DENY.value:
                        replay_rejections += 1

                if res["decision"] == DecisionType.UNSUPPORTED.value:
                    unsupported_cnt += 1
                elif res["decision"] == DecisionType.ERROR.value:
                    error_cnt += 1
                elif is_nominal:
                    nominal_attempts += 1
                    if res["execution"] == ExecutionStatus.EXECUTED.value:
                        nominal_executions += 1
                else:
                    unauthorized_attempts += 1
                    if res["execution"] == ExecutionStatus.EXECUTED.value:
                        unauthorized_executions += 1

            uer = (
                (unauthorized_executions / unauthorized_attempts * 100.0)
                if unauthorized_attempts > 0
                else 0.0
            )
            unsupported_rate = (
                (unsupported_cnt / total_attempts * 100.0) if total_attempts > 0 else 0.0
            )
            replay_rejection_rate = (
                (replay_rejections / replay_attempts * 100.0) if replay_attempts > 0 else 0.0
            )

            latencies_ns.sort()
            p50 = latencies_ns[int(len(latencies_ns) * 0.5)] if latencies_ns else 0
            p95 = latencies_ns[int(len(latencies_ns) * 0.95)] if latencies_ns else 0

            metrics_by_substrate[sub_name] = {
                "total_attempts": total_attempts,
                "unauthorized_attempts": unauthorized_attempts,
                "unauthorized_executions": unauthorized_executions,
                "nominal_attempts": nominal_attempts,
                "nominal_executions": nominal_executions,
                "unsupported_attempts": unsupported_cnt,
                "error_attempts": error_cnt,
                "unauthorized_execution_rate_pct": round(uer, 2),
                "unsupported_rate_pct": round(unsupported_rate, 2),
                "replay_rejection_rate_pct": round(replay_rejection_rate, 2),
                "latency_p50_ns": p50,
                "latency_p95_ns": p95,
                "adapter_metadata": adapter.get_metadata(),
            }

        # Compute Property Coverage Matrix across substrates
        property_matrix: Dict[str, Dict[str, Any]] = {}
        for entry in executions:
            prop = entry.get("security_property", "UNKNOWN")
            sub = entry["result"]["substrate"]
            dec = entry["result"]["decision"]
            scope = entry["result"].get("semantic_scope", "NATIVE")
            layer = entry["result"].get("enforcement_layer", "UNKNOWN")
            reason = entry["result"].get("reason_class", "")

            if prop not in property_matrix:
                property_matrix[prop] = {}
            
            # Store primary outcome for this property on this substrate
            property_matrix[prop][sub] = {
                "decision": dec,
                "semantic_scope": scope,
                "enforcement_layer": layer,
                "reason_class": reason,
            }

        summary_data = {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "total_scenarios": len(scenarios),
            "total_executions": len(executions),
            "environment": env_meta,
            "metrics": metrics_by_substrate,
            "property_matrix": property_matrix,
        }

        with open(os.path.join(exp_dir, "result.json"), "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        with open(os.path.join(exp_dir, "experiment.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "experiment_id": experiment_id,
                    "scenarios": [s.scenario_id for s in scenarios],
                    "substrates": [a.name for a in adapters],
                    "timestamp": env_meta["timestamp"],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        # Write pointer to latest experiment
        with open(os.path.join(self.output_base_dir, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"latest_experiment_id": experiment_id, "path": exp_dir}, f, indent=2)

        return summary_data
