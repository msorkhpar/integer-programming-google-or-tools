from __future__ import annotations

import math


def classify(status: str, bound: float, integral: bool, incumbent: float | None, whole_values: bool = False) -> str:
    """What the search does with a solved node: "infeasible", "bound", "incumbent" or "branch"."""
    # TODO: test infeasible first, then the bound against the incumbent (rounded down when
    # whole_values), then integrality; branch on anything left.
    return "undecided"


if __name__ == "__main__":
    print(classify("optimal", 412.5, False, 400))
    print(classify("optimal", 400.7, False, 400, whole_values=True))
