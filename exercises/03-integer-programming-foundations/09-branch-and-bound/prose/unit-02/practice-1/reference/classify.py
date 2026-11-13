from __future__ import annotations

import math


def classify(status: str, bound: float, integral: bool, incumbent: float | None, whole_values: bool = False) -> str:
    """What the search does with a solved node: "infeasible", "bound", "incumbent" or "branch"."""
    if status == "infeasible":
        return "infeasible"
    if whole_values:
        bound = math.floor(bound + 1e-9)
    if incumbent is not None and bound <= incumbent:
        return "bound"
    if integral:
        return "incumbent"
    return "branch"


if __name__ == "__main__":
    print(classify("optimal", 412.5, False, 400))
    print(classify("optimal", 400.7, False, 400, whole_values=True))
