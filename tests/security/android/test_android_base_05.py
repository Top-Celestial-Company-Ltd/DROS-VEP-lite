"""ANDROID-BASE-05: revocation removes subsequent execution authority."""

from pathlib import Path

from benchmark.run_tmc_android_base_05_avd import build_revocation_request
from vep.android_baseline import AndroidBaselineController


def test_android_base_05_revoked_authority_cannot_create_new_effect(
    tmp_path: Path,
) -> None:
    effect_marker = tmp_path / "fixture-effects.jsonl"
    controller = AndroidBaselineController(effect_marker_path=effect_marker)
    request = build_revocation_request()

    before = controller.submit(request)
    assert before["decision"] == "ALLOW"
    assert before["execution_started"] is True
    assert before["execution_completed"] is True
    assert before["execution_effect"] == "BOUNDED_FIXTURE"
    assert effect_marker.exists()
    effect_count_before = len(effect_marker.read_text(encoding="utf-8").splitlines())

    controller.revoke(request["principal"])
    after = controller.submit(request)

    assert after["decision"] == "DENY"
    assert after["execution_started"] is False
    assert after["execution_completed"] is False
    assert after["execution_effect"] == "NONE"
    assert len(effect_marker.read_text(encoding="utf-8").splitlines()) == effect_count_before
