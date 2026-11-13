from __future__ import annotations

import math


def max_epsilon(primary: dict[str, int], secondary: dict[str, float]) -> float:
    """A weight for the bonus that can never change the order of two plans' main scores."""
    # TODO: work out g and S, then return g / (S + 1).
    return 1.0


if __name__ == "__main__":
    print(max_epsilon({"R1": 4, "R2": 6}, {"R1": 3.0, "R2": 1.0}))
