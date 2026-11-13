from __future__ import annotations

from typing import Callable

EPS = 1e-6
LP = Callable[[dict[str, int]], "dict[str, float] | None"]


def dive(lp: LP) -> tuple[dict[str, int] | None, list[tuple[str, int]]]:
    """Fix the least fractional variable to its nearest value, re-solve, repeat until the point is 0-1."""
    fixed: dict[str, int] = {}
    steps: list[tuple[str, int]] = []
    x = lp(fixed)
    while True:
        fractional = [j for j, v in x.items() if EPS < v < 1 - EPS]
        if not fractional:
            return {j: round(v) for j, v in x.items()}, steps
        j = min(fractional, key=lambda j: (min(x[j], 1 - x[j]), j))
        target = 1 if x[j] >= 0.5 else 0
        new = lp({**fixed, j: target})
        if new is None:
            target = 1 - target
            new = lp({**fixed, j: target})
            if new is None:
                return None, steps
        fixed[j] = target
        steps.append((j, target))
        x = new


if __name__ == "__main__":
    answers = {(): {"a": 1, "b": 0.9, "c": 0.4}, (("b", 1),): {"a": 1, "b": 1, "c": 0}}
    print(dive(lambda fixed: answers[tuple(sorted(fixed.items()))]))
