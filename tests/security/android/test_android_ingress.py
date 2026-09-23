"""Ingress accounting contract for the future Android concurrency seam."""

from benchmark.android_ingress import verify_ingress_records, verify_pipeline_records


def test_ingress_accounting_requires_one_observation_per_submitted_request() -> None:
    submitted = ["ANDROID-INGRESS-000011", "ANDROID-INGRESS-000012"]
    observed = [
        {"request_id": "ANDROID-INGRESS-000011", "event": "RECEIVED"},
        {"request_id": "ANDROID-INGRESS-000012", "event": "RECEIVED"},
    ]

    result = verify_ingress_records(submitted, observed)

    assert result == {
        "submitted_count": 2,
        "observed_count": 2,
        "missing_request_ids": [],
        "duplicate_request_ids": [],
        "unexpected_request_ids": [],
        "complete": True,
    }


def test_c1_pipeline_requires_received_dispatched_and_result_for_each_request() -> None:
    request_ids = ["ANDROID-C1-000011", "ANDROID-C1-000012"]
    stage_records = [
        [{"request_id": request_id, "event": stage} for request_id in request_ids]
        for stage in ("RECEIVED", "DISPATCHED", "RESULT")
    ]

    result = verify_pipeline_records(request_ids, *stage_records)

    assert result == {
        "submitted_count": 2,
        "received_complete": True,
        "dispatched_complete": True,
        "result_complete": True,
        "complete": True,
    }
