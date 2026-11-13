from __future__ import annotations

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def build(costs: list[int], values: list[int], budget: float, integer: bool):
    """The selection model and its budget row; integer=False gives the LP relaxation."""
    model = mathopt.Model()
    x = [model.add_variable(lb=0, ub=1, is_integer=integer) for _ in costs]
    row = model.add_linear_constraint(sum(c * xi for c, xi in zip(costs, x)) <= budget, name="budget")
    model.maximize(sum(v * xi for v, xi in zip(values, x)))
    return model, row


def forecast_and_gain(costs: list[int], values: list[int], budget: float, extra: float) -> dict:
    """The relaxation's price x extra, beside the MILP's real gain for the same extra money."""
    relaxation, row = build(costs, values, budget, integer=False)
    price = mathopt.solve(relaxation, mathopt.SolverType.GLOP).dual_values(row)

    def best(b: float) -> float:
        return mathopt.solve(build(costs, values, b, integer=True)[0], mathopt.SolverType.HIGHS,
                             params=EXACT).objective_value()

    return {"forecast": price * extra, "gain": best(budget + extra) - best(budget)}


if __name__ == "__main__":
    print(forecast_and_gain([2, 4], [6, 4], 1, 3))
