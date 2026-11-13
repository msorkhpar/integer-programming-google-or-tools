from __future__ import annotations

EPS = 1e-6


def round_and_fill(values: dict[str, float], costs: dict[str, float], budget: float,
                   x: dict[str, float]) -> list[str]:
    """Round the LP point down, then add items by value per unit of cost while they fit."""
    # TODO: keep the items at 1 (within EPS); then try every other item, best value per cost first,
    # and add it when its cost fits in what is left.
    return []


if __name__ == "__main__":
    print(round_and_fill({"A": 9, "B": 5, "C": 1}, {"A": 6, "B": 5, "C": 2}, 10, {"A": 1, "B": 0.8, "C": 0}))
