"""BASE-06 measurement contract: raw samples must reconstruct the summary."""

import json
from pathlib import Path

from benchmark.analyze_tmc_android_base_06 import analyze_results


def test_base_06_summary_is_reconstructable_from_raw_results(tmp_path: Path) -> None:
    raw = tmp_path / "results.jsonl"
    samples = [10, 20, 30, 40]
    raw.write_text(
        "\n".join(
            json.dumps(
                {
                    "sample_index": index,
                    "request_id": f"ANDROID-BASE-06-{index:06d}",
                    "decision": "DENY",
                    "execution_started": False,
                    "execution_completed": False,
                    "execution_effect": "NONE",
                    "decision_latency_ns": latency,
                    "app_elapsed_ns": latency + 1,
                }
            )
            for index, latency in enumerate(samples, start=1)
        )
        + "\n",
        encoding="utf-8",
    )

    summary = analyze_results(raw)

    assert summary["sample_count"] == 4
    assert summary["decision_latency_ns"] == {
        "p50": 20,
        "p95": 40,
        "p99": 40,
        "algorithm": "nearest-rank; rank=ceil(p*n), clamped to [1,n]",
    }
    assert summary["decision_counts"] == {"DENY": 4}
    assert summary["execution_started_count"] == 0
    assert summary["execution_completed_count"] == 0
    assert summary["effect_counts"] == {"NONE": 4}
