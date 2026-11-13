from __future__ import annotations

from ortools.sat.python import cp_model

SCALE = 100          # hundredths of a million: every cost and the budget is a whole number of these


def pick(values: list[float], costs: list[float], budget: float) -> list[int]:
    """Indices of the repairs to fund, in increasing order: most value with total cost <= budget."""
    # TODO: one Boolean per repair, the budget row in hundredths, maximize the value, solve.
    return []


if __name__ == "__main__":
    print(pick([3, 4, 5], [0.5, 0.65, 1.2], 1.15))
