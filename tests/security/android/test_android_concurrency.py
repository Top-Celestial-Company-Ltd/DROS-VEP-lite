"""First concurrency slice contract at the controller public seam."""

from pathlib import Path

from benchmark.android_concurrency import dispatch_waves
from vep.android_baseline import AndroidBaselineController


def test_concurrency_wave_preserves_one_result_per_request_and_deny_invariant(
    tmp_path: Path,
) -> None:
    controller = AndroidBaselineController(
        effect_marker_path=tmp_path / "fixture-effects.jsonl"
    )
    requests = [
        {
            "request_id": f"ANDROID-CONCURRENCY-{index:06d}",
            "principal": "concurrency-agent",
            "action": "READ_CONTACTS",
            "capability": "CAP_CAMERA",
            "policy_version": "android-baseline-policy-v1",
            "revocation_epoch": 0,
            "arguments_hash": "sha256:android-concurrency-args",
        }
        for index in range(1, 9)
    ]

    results = dispatch_waves(controller.submit, requests, concurrency=2)

    assert [request_id for request_id, _ in results] == [
        request["request_id"] for request in requests
    ]
    assert len(results) == len(requests)
    assert all(result["decision"] == "DENY" for _, result in results)
    assert all(result["execution_started"] is False for _, result in results)
    assert all(result["execution_completed"] is False for _, result in results)
    assert all(result["execution_effect"] == "NONE" for _, result in results)
