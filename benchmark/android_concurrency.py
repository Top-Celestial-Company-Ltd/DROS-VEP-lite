"""Small fixed-wave dispatcher for the Android concurrency baseline."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Any


def dispatch_waves(
    submit: Callable[[Mapping[str, Any]], dict[str, Any]],
    requests: Sequence[Mapping[str, Any]],
    *,
    concurrency: int,
) -> list[tuple[str, dict[str, Any]]]:
    """Submit fixed-size waves and return results in request order."""

    if concurrency < 1:
        raise ValueError("concurrency must be positive")
    ordered: list[tuple[str, dict[str, Any]]] = []
    for offset in range(0, len(requests), concurrency):
        wave = requests[offset : offset + concurrency]
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(submit, request) for request in wave]
            for request, future in zip(wave, futures):
                ordered.append((str(request["request_id"]), future.result()))
    return ordered
