from __future__ import annotations

import itertools

EPS = 1e-6


def rins(values: dict[str, float], costs: dict[str, float], budget: float,
         incumbent: dict[str, int], x: dict[str, float]) -> list[str] | None:
    """The best plan among those that keep every variable the incumbent and the LP agree on."""
    # TODO: fix the items where |x_j - incumbent_j| < EPS; try every 0-1 choice of the free items
    # with itertools.product; keep the best one within the budget.
    return []


if __name__ == "__main__":
    values, costs = {"A": 7, "B": 6, "C": 5, "D": 2}, {"A": 5, "B": 4, "C": 3, "D": 1}
    print(rins(values, costs, 9, {"A": 1, "B": 0, "C": 0, "D": 1}, {"A": 0.2, "B": 1, "C": 1, "D": 1}))
