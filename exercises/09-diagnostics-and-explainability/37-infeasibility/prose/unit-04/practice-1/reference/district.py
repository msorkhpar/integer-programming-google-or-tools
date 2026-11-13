from __future__ import annotations

from ortools.math_opt.python import mathopt


def least_overspend(projects: dict, budget: dict, required: set[str]) -> dict[int, int]:
    """The smallest overspend in each year that lets every required project be funded."""
    model = mathopt.Model(name="district")
    fund = {p: model.add_binary_variable(name=f"fund_{p}") for p in projects}
    over = {y: model.add_variable(lb=0, name=f"over_{y}") for y in budget}
    for p in required:
        model.add_linear_constraint(fund[p] == 1, name=f"required_{p}")
    for y, limit in budget.items():
        spend = mathopt.fast_sum(cost.get(y, 0) * fund[p] for p, cost in projects.items())
        model.add_linear_constraint(spend - over[y] <= limit, name=f"budget_{y}")
    model.minimize(mathopt.fast_sum(over.values()))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS,
                            params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    return {y: round(result.variable_values(over[y])) for y in budget}


if __name__ == "__main__":
    projects = {"roof": {2027: 300}, "boilers": {2027: 200, 2028: 400}}
    print(least_overspend(projects, {2027: 450, 2028: 450}, {"roof", "boilers"}))
