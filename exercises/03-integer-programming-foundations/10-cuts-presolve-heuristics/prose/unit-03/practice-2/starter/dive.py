from __future__ import annotations

from typing import Callable

EPS = 1e-6
LP = Callable[[dict[str, int]], "dict[str, float] | None"]


def dive(lp: LP) -> tuple[dict[str, int] | None, list[tuple[str, int]]]:
    """Fix the least fractional variable to its nearest value, re-solve, repeat until the point is 0-1."""
    # TODO: start from lp({}); while a variable is fractional, fix the least fractional one to its
    # nearest value (the other value if that LP is None), keeping every earlier fixing.
    return None, []


if __name__ == "__main__":
    answers = {(): {"a": 1, "b": 0.9, "c": 0.4}, (("b", 1),): {"a": 1, "b": 1, "c": 0}}
    print(dive(lambda fixed: answers[tuple(sorted(fixed.items()))]))
