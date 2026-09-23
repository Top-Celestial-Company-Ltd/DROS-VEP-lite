"""Android AppOps baseline contract."""

from vep.android_appops_baseline import AndroidAppOpsBaselineController


def test_appops_baseline_denies_when_read_contacts_appop_is_ignored() -> None:
    controller = AndroidAppOpsBaselineController(appops_allowed=False)

    result = controller.evaluate(
        {"request_id": "ANDROID-APPOPS-01-000001", "action": "READ_CONTACTS"}
    )

    assert result == {
        "request_id": "ANDROID-APPOPS-01-000001",
        "authority": "ANDROID_APPOPS_READ_CONTACTS",
        "decision": "DENY",
        "execution_started": False,
        "execution_completed": False,
        "execution_effect": "NONE",
        "reason": "ANDROID_APPOPS_DENIED",
    }
