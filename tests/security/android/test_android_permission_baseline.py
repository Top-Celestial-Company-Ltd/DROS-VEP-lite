"""Android native-permission baseline contract.

This test defines the public result seam for the first comparative baseline
slice.  It intentionally does not reuse DROS authorization logic: the
baseline decision must be owned by Android's declared permission state.
"""

from vep.android_permission_baseline import AndroidPermissionBaselineController


def test_permission_baseline_denies_without_read_contacts_permission() -> None:
    controller = AndroidPermissionBaselineController(permission_granted=False)

    result = controller.evaluate(
        {
            "request_id": "ANDROID-PERM-01-000001",
            "action": "READ_CONTACTS",
        }
    )

    assert result == {
        "request_id": "ANDROID-PERM-01-000001",
        "authority": "ANDROID_PERMISSION_READ_CONTACTS",
        "decision": "DENY",
        "execution_started": False,
        "execution_completed": False,
        "execution_effect": "NONE",
        "reason": "ANDROID_PERMISSION_DENIED",
    }
