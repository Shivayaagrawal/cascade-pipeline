"""Median, mean, and p95. These summaries are not model scores."""

from __future__ import annotations

import math


def summarize_seconds(samples: list[float]) -> dict[str, float | int | None]:
    """Nearest-rank p95. Even-count median is the mean of the two central values."""

    if not samples:
        return {"n": 0, "mean": None, "median": None, "p95": None}
    ordered = sorted(samples)
    count = len(ordered)
    midpoint = count // 2
    if count % 2 == 1:
        median = ordered[midpoint]
    else:
        median = (ordered[midpoint - 1] + ordered[midpoint]) / 2
    rank = min(count - 1, max(0, math.ceil(0.95 * count) - 1))
    return {
        "n": count,
        "mean": sum(ordered) / count,
        "median": median,
        "p95": ordered[rank],
    }
