"""ANDROID-BASE-04: unauthorized execution must not produce a fixture effect.

This is the first TMC Android baseline red slice.  It observes only the
AndroidBaselineController public boundary and the externally visible fixture
effect marker.  The host controller must not make the authorization decision;
the app-side action boundary is responsible for returning the decision.
"""

from pathlib import Path

from vep.android_baseline import AndroidBaselineController


def test_android_base_04_denies_before_bounded_fixture_effect(
    tmp_path: Path,
) -> None:
    effect_marker = tmp_path / "fixture-effects.jsonl"
    controller = AndroidBaselineController(effect_marker_path=effect_marker)

    result = controller.submit(
        {
            "request_id": "ANDROID-BASE-04-000001",
            "principal": "compromised-agent",
            "action": "READ_CONTACTS",
            "capability": "CAP_CAMERA",
            "policy_version": "policy-test-v1",
            "revocation_epoch": 0,
            "arguments_hash": "sha256:test-args",
        }
    )

    assert result["decision"] == "DENY"
    assert result["execution_started"] is False
    assert result["execution_completed"] is False
    assert result["execution_effect"] == "NONE"

    # The result object is not trusted as proof.  The bounded fixture must
    # leave no externally observable effect marker on the deny path.
    assert not effect_marker.exists() or effect_marker.read_text(encoding="utf-8") == ""
