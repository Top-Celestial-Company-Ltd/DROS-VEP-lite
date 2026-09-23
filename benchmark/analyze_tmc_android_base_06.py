"""Reconstruct BASE-06 decision-latency summary from immutable raw samples."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


def nearest_rank(values: list[int], percentile: float) -> int:
    if not values:
        raise ValueError("at least one latency sample is required")
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(percentile * len(ordered))))
    return ordered[rank - 1]


def analyze_results(raw_path: Path) -> dict[str, Any]:
    records = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not records:
        raise ValueError("results.jsonl contains no samples")

    latencies: list[int] = []
    decisions: Counter[str] = Counter()
    effects: Counter[str] = Counter()
    started = 0
    completed = 0
    for record in records:
        if not isinstance(record.get("request_id"), str) or not record["request_id"]:
            raise ValueError("each sample requires a request_id")
        latency = record.get("decision_latency_ns")
        if not isinstance(latency, int) or isinstance(latency, bool) or latency < 0:
            raise ValueError("decision_latency_ns must be a non-negative integer")
        if not isinstance(record.get("app_elapsed_ns"), int):
            raise ValueError("each sample requires integer app_elapsed_ns")
        latencies.append(latency)
        decisions[str(record.get("decision", ""))] += 1
        effects[str(record.get("execution_effect", ""))] += 1
        started += int(record.get("execution_started") is True)
        completed += int(record.get("execution_completed") is True)

    return {
        "analysis_schema": "TMC-ANDROID-BASE-06-SUMMARY-v1",
        "source_raw_file": raw_path.name,
        "sample_count": len(records),
        "decision_latency_ns": {
            "p50": nearest_rank(latencies, 0.50),
            "p95": nearest_rank(latencies, 0.95),
            "p99": nearest_rank(latencies, 0.99),
            "algorithm": "nearest-rank; rank=ceil(p*n), clamped to [1,n]",
        },
        "decision_counts": dict(sorted(decisions.items())),
        "execution_started_count": started,
        "execution_completed_count": completed,
        "effect_counts": dict(sorted(effects.items())),
        "measurement_boundary": "app-observed request-to-authorization-decision interval only; ADB transport, framework launch, fixture execution, and energy excluded",
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    summary = analyze_results(args.raw)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
