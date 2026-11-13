from __future__ import annotations

import math


def true_gap(incumbent: float, bound: float, constant: float) -> dict:
    """The gap the solver saw, and the gap on the value the decisions control."""
    # TODO: the absolute gap, then the two ratios with their different denominators.
    return {"absolute": 0.0, "seen": 0.0, "on_decisions": 0.0}


if __name__ == "__main__":
    print(true_gap(incumbent=2_224_000, bound=2_224_200, constant=2_000_000))
