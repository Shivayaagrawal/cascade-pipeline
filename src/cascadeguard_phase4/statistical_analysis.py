"""Wilson intervals and parent-cluster bootstrap. Cases that share a parent stay together."""

from __future__ import annotations

import random
from collections import defaultdict

from cascadeguard_phase4.phase4_metrics import proportion


def _groups(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["parent_id"])].append(row)
    return grouped


def _mean(rows: list[dict[str, object]], key: str) -> float | None:
    if not rows:
        return None
    return sum(int(bool(row[key])) for row in rows) / len(rows)


def paired_cluster_difference(
    left: list[dict[str, object]],
    right: list[dict[str, object]],
    key: str,
    *,
    seed: int,
    draws: int = 1000,
) -> dict[str, object]:
    """Difference left minus right on a per-case indicator, resampled by parent id."""

    left_group = _groups(left)
    right_group = _groups(right)
    parents = sorted(set(left_group) & set(right_group))
    observed_left = [row for parent in parents for row in left_group[parent]]
    observed_right = [row for parent in parents for row in right_group[parent]]
    observed = None
    if observed_left and observed_right:
        left_mean = _mean(observed_left, key)
        right_mean = _mean(observed_right, key)
        if left_mean is not None and right_mean is not None:
            observed = left_mean - right_mean
    rng = random.Random(seed)
    samples: list[float] = []
    if parents and observed is not None:
        for _ in range(draws):
            draw = [rng.choice(parents) for _ in parents]
            left_rows = [row for parent in draw for row in left_group[parent]]
            right_rows = [row for parent in draw for row in right_group[parent]]
            left_mean = _mean(left_rows, key)
            right_mean = _mean(right_rows, key)
            if left_mean is None or right_mean is None:
                continue
            samples.append(left_mean - right_mean)
    samples.sort()
    if not samples:
        low = high = None
    else:
        low = samples[int(0.025 * (len(samples) - 1))]
        high = samples[int(0.975 * (len(samples) - 1))]
    return {
        "contrast": "left_minus_right",
        "indicator": key,
        "estimate": observed,
        "ci95": None if low is None else {"low": low, "high": high},
        "draws": len(samples),
        "parents": len(parents),
        "method": "parent_cluster_bootstrap",
    }


def commit_rate(rows: list[dict[str, object]], key: str, empty_reason: str) -> dict[str, object]:
    commits = [row for row in rows if row["committed"]]
    return proportion(sum(bool(row[key]) for row in commits), len(commits), empty_reason)
