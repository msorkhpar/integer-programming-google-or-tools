from __future__ import annotations

EPS = 1e-6


def round_and_fill(values: dict[str, float], costs: dict[str, float], budget: float,
                   x: dict[str, float]) -> list[str]:
    """Round the LP point down, then add items by value per unit of cost while they fit."""
    plan = [j for j in values if x[j] >= 1 - EPS]
    left = budget - sum(costs[j] for j in plan)
    for j in sorted((j for j in values if j not in plan), key=lambda j: (-values[j] / costs[j], j)):
        if costs[j] <= left:
            plan.append(j)
            left -= costs[j]
    return sorted(plan)


if __name__ == "__main__":
    print(round_and_fill({"A": 9, "B": 5, "C": 1}, {"A": 6, "B": 5, "C": 2}, 10, {"A": 1, "B": 0.8, "C": 0}))
