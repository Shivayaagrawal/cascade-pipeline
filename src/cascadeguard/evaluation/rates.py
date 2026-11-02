"""Ratios that stay undefined when the denominator is zero."""

from __future__ import annotations


def rate(numerator: int, denominator: int, empty_reason: str) -> dict[str, float | int | str | None]:
    """Return a ratio, or value null with a reason. Never substitute zero."""

    if denominator == 0:
        return {
            "value": None,
            "numerator": numerator,
            "denominator": 0,
            "reason": empty_reason,
        }
    return {
        "value": numerator / denominator,
        "numerator": numerator,
        "denominator": denominator,
        "reason": None,
    }
