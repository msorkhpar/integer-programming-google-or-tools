from __future__ import annotations

import math


def max_epsilon(primary: dict[str, int], secondary: dict[str, float]) -> float:
    """A weight for the bonus that can never change the order of two plans' main scores."""
    gap = math.gcd(*primary.values())          # every difference of two totals is a multiple of it
    bonus = sum(secondary.values())            # a plan may take every route, so every bonus
    return gap / (bonus + 1)


if __name__ == "__main__":
    print(max_epsilon({"R1": 4, "R2": 6}, {"R1": 3.0, "R2": 1.0}))
