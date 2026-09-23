"""Android Binder protected-service baseline contract."""

from vep.android_binder_baseline import AndroidBinderBaselineController


def test_binder_baseline_denies_without_service_permission() -> None:
    controller = AndroidBinderBaselineController(binder_permission_granted=False)

    result = controller.evaluate({"request_id": "ANDROID-BINDER-01-000001"})

    assert result == {
        "request_id": "ANDROID-BINDER-01-000001",
        "authority": "ANDROID_BINDER_SERVICE_PERMISSION",
        "decision": "DENY",
        "execution_started": False,
        "execution_completed": False,
        "execution_effect": "NONE",
        "reason": "BINDER_SERVICE_PERMISSION_DENIED",
    }
