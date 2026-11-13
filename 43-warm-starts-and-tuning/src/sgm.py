"""The shifted geometric mean of lesson 5.4.2, and the paired comparison of two settings built on it."""

from __future__ import annotations

import math


def shifted_geometric_mean(values: list[float], shift: float) -> float:
    """exp(mean of ln(max(1, v + shift))) - shift, for nonnegative values and a nonnegative shift."""
    if not values:
        raise ValueError("no values")
    logs = [math.log(max(1.0, v + shift)) for v in values]
    return math.exp(sum(logs) / len(logs)) - shift


def compare(new: list[float], old: list[float], shift: float) -> tuple[float, int, int]:
    """Paired observations of two settings: (SGM of new / SGM of old, new wins, new losses)."""
    if len(new) != len(old):
        raise ValueError("the observations must be paired")
    ratio = shifted_geometric_mean(new, shift) / shifted_geometric_mean(old, shift)
    return ratio, sum(a < b for a, b in zip(new, old)), sum(a > b for a, b in zip(new, old))
