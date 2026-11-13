from __future__ import annotations

import math


def sgm(values: list[float], shift: float) -> float:
    """The shifted geometric mean of lesson 5.4.2: exp(mean of ln(max(1, v + shift))) - shift."""
    return math.exp(sum(math.log(max(1.0, v + shift)) for v in values) / len(values)) - shift


def judge(new: list[float], old: list[float], shift: float, margin: float) -> str:
    """'better', 'worse' or 'same' for one measure, from paired work with the new and the old setting."""
    ratio = sgm(new, shift) / sgm(old, shift)
    wins = sum(a < b for a, b in zip(new, old))
    losses = sum(a > b for a, b in zip(new, old))
    if ratio <= 1 - margin and wins > losses:
        return "better"
    if ratio >= 1 + margin and losses > wins:
        return "worse"
    return "same"


def verdict(plan_new: list[float], plan_old: list[float], proof_new: list[float], proof_old: list[float],
            shift: float, margin: float = 0.05) -> str:
    """'adopt', 'reject', 'trade-off' or 'no effect' for a setting, from both measures."""
    marks = {judge(plan_new, plan_old, shift, margin), judge(proof_new, proof_old, shift, margin)}
    if marks == {"better", "worse"}:
        return "trade-off"
    if "better" in marks:
        return "adopt"
    if "worse" in marks:
        return "reject"
    return "no effect"


if __name__ == "__main__":
    print(verdict([300, 200], [600, 500], [9000, 8000], [9100, 8100], shift=100))
