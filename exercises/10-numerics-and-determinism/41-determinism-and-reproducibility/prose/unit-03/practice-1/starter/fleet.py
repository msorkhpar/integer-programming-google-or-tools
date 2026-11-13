from __future__ import annotations

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def replacement_plan(costs: dict[str, int], budget: int) -> list[str]:
    """The cheapest of the plans that replace the most buses within the budget, as sorted ids."""
    model = mathopt.Model(name="buses")
    x = {b: model.add_binary_variable(name=f"x_{b}") for b in sorted(costs)}
    model.add_linear_constraint(sum(costs[b] * x[b] for b in x) <= budget, name="budget")
    # TODO: pass 1, the row that keeps its count, pass 2.
    return sorted(costs)


if __name__ == "__main__":
    print(replacement_plan({"B1": 300, "B2": 250, "B3": 420, "B4": 260}, 820))
