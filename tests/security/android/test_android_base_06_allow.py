"""ANDROID-BASE-06-ALLOW: allow-path measurement request contract."""

from pathlib import Path

from vep.android_baseline import AndroidBaselineController


def test_android_base_06_allow_request_reaches_bounded_fixture(tmp_path: Path) -> None:
    effect_marker = tmp_path / "fixture-effects.jsonl"
    controller = AndroidBaselineController(effect_marker_path=effect_marker)

    result = controller.submit(
        {
            "request_id": "ANDROID-BASE-06-ALLOW-000001",
            "principal": "measurement-agent",
            "action": "READ_CONTACTS",
            "capability": "CAP_CONTACTS",
            "policy_version": "android-baseline-policy-v1",
            "revocation_epoch": 0,
            "arguments_hash": "sha256:android-base-06-allow-args",
        }
    )

    assert result["decision"] == "ALLOW"
    assert result["execution_started"] is True
    assert result["execution_completed"] is True
    assert result["execution_effect"] == "BOUNDED_FIXTURE"
    assert effect_marker.read_text(encoding="utf-8").count("\n") == 1
