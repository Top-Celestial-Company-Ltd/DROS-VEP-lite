"""ANDROID-BASE-03: authorized execution produces the bounded fixture effect."""

from pathlib import Path

from benchmark.run_tmc_android_base_03_avd import build_authorized_request
from vep.android_baseline import AndroidBaselineController


def test_android_base_03_authorized_request_produces_bounded_effect(
    tmp_path: Path,
) -> None:
    effect_marker = tmp_path / "fixture-effects.jsonl"
    controller = AndroidBaselineController(effect_marker_path=effect_marker)

    result = controller.submit(build_authorized_request())

    assert result["decision"] == "ALLOW"
    assert result["execution_started"] is True
    assert result["execution_completed"] is True
    assert result["execution_effect"] == "BOUNDED_FIXTURE"
    assert effect_marker.exists()
    assert '"effect": "BOUNDED_FIXTURE"' in effect_marker.read_text(encoding="utf-8")
