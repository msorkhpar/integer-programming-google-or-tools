from __future__ import annotations

import math


def share(absolute: float, of: float) -> float:
    """absolute / |of|, with 0 for no gap and infinity for a gap over nothing."""
    if absolute == 0:
        return 0.0
    if of == 0:
        return math.inf
    return absolute / abs(of)


def true_gap(incumbent: float, bound: float, constant: float) -> dict:
    """The gap the solver saw, and the gap on the value the decisions control."""
    absolute = abs(bound - incumbent)
    decisions = incumbent - constant
    return {"absolute": absolute, "seen": share(absolute, incumbent), "on_decisions": share(absolute, decisions)}


if __name__ == "__main__":
    print(true_gap(incumbent=2_224_000, bound=2_224_200, constant=2_000_000))
