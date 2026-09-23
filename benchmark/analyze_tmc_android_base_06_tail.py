"""Characterize the existing BASE-06 tail without rerunning the AVD."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any


def nearest_rank(values: list[int], percentile: float) -> int:
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(percentile * len(ordered))))
    return ordered[rank - 1]


def characterize(raw_path: Path, summary_path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    latencies = [int(row["decision_latency_ns"]) for row in rows]
    thresholds = [
        ("lt_1ms", 0, 1_000_000),
        ("1ms_to_lt_2ms", 1_000_000, 2_000_000),
        ("2ms_to_lt_5ms", 2_000_000, 5_000_000),
        ("5ms_to_lt_10ms", 5_000_000, 10_000_000),
        ("10ms_to_lt_25ms", 10_000_000, 25_000_000),
        ("25ms_to_lt_50ms", 25_000_000, 50_000_000),
        ("gte_50ms", 50_000_000, None),
    ]
    distribution = {}
    for name, lower, upper in thresholds:
        distribution[name] = sum(
            latency >= lower and (upper is None or latency < upper)
            for latency in latencies
        )
    top_tail = sorted(
        (
            {
                "sample_index": row["sample_index"],
                "request_id": row["request_id"],
                "decision_latency_ns": row["decision_latency_ns"],
                "app_elapsed_ns": row["app_elapsed_ns"],
            }
            for row in rows
        ),
        key=lambda row: row["decision_latency_ns"],
        reverse=True,
    )[:10]
    return {
        "analysis_schema": "TMC-ANDROID-BASE-06-TAIL-ANALYSIS-v1",
        "source_raw_file": raw_path.name,
        "source_summary_file": summary_path.name,
        "source_hashes": {
            "results.jsonl": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
            "summary.json": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        },
        "sample_count": len(rows),
        "latency_ns": {
            "min": min(latencies),
            "max": max(latencies),
            "mean": mean(latencies),
            "p50": nearest_rank(latencies, 0.50),
            "p90": nearest_rank(latencies, 0.90),
            "p95": nearest_rank(latencies, 0.95),
            "p99": nearest_rank(latencies, 0.99),
            "algorithm": "nearest-rank; rank=ceil(p*n), clamped to [1,n]",
        },
        "distribution": distribution,
        "top_10_tail_samples": top_tail,
        "ordering": {
            "sequence_position_available": all("sample_index" in row for row in rows),
            "tail_sample_indices": [row["sample_index"] for row in top_tail],
            "raw_timestamp_available": False,
            "runtime_event_correlation": "not assessed; T9 contains no raw timestamp or logcat artifact",
        },
        "interpretation_boundary": "Descriptive characterization of the preserved T9 app-observed decision-latency samples only; no causal attribution and no outlier removal.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis = characterize(args.raw, args.summary)
    args.output.write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
