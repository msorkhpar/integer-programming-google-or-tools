from __future__ import annotations

import math


def sgm(values: list[float], shift: float) -> float:
    """The shifted geometric mean of lesson 5.4.2: exp(mean of ln(max(1, v + shift))) - shift."""
    return math.exp(sum(math.log(max(1.0, v + shift)) for v in values) / len(values)) - shift


def judge(new: list[float], old: list[float], shift: float, margin: float) -> str:
    """'better', 'worse' or 'same' for one measure, from paired work with the new and the old setting."""
    # TODO: the ratio of shifted geometric means, the wins and the losses, then the rule.
    return ""


def verdict(plan_new: list[float], plan_old: list[float], proof_new: list[float], proof_old: list[float],
            shift: float, margin: float = 0.05) -> str:
    """'adopt', 'reject', 'trade-off' or 'no effect' for a setting, from both measures."""
    # TODO: judge each measure, then combine the two judgements.
    return "undecided"


if __name__ == "__main__":
    print(verdict([300, 200], [600, 500], [9000, 8000], [9100, 8100], shift=100))
