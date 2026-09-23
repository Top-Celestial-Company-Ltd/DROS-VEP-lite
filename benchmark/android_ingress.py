"""Deterministic accounting helpers for the Android ingress seam."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


def verify_ingress_records(
    submitted_request_ids: Sequence[str],
    observed_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    submitted = list(submitted_request_ids)
    observed = [str(record.get("request_id", "")) for record in observed_records]
    submitted_set = set(submitted)
    observed_set = set(observed)
    duplicates = sorted(
        request_id
        for request_id, count in Counter(observed).items()
        if count > 1
    )
    missing = sorted(submitted_set - observed_set)
    unexpected = sorted(observed_set - submitted_set)
    return {
        "submitted_count": len(submitted),
        "observed_count": len(observed),
        "missing_request_ids": missing,
        "duplicate_request_ids": duplicates,
        "unexpected_request_ids": unexpected,
        "complete": not missing and not duplicates and not unexpected and len(submitted) == len(observed),
    }


def verify_pipeline_records(
    submitted_request_ids: Sequence[str],
    received_records: Sequence[Mapping[str, Any]],
    dispatched_records: Sequence[Mapping[str, Any]],
    result_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    received = verify_ingress_records(submitted_request_ids, received_records)
    dispatched = verify_ingress_records(submitted_request_ids, dispatched_records)
    results = verify_ingress_records(submitted_request_ids, result_records)
    return {
        "submitted_count": len(submitted_request_ids),
        "received_complete": received["complete"],
        "dispatched_complete": dispatched["complete"],
        "result_complete": results["complete"],
        "complete": received["complete"] and dispatched["complete"] and results["complete"],
    }
