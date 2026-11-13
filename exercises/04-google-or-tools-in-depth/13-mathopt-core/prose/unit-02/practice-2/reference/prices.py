from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def activity(row: mathopt.LinearConstraint, result: mathopt.SolveResult) -> float:
    """sum of coefficient * value over the row's terms, at the result's best plan."""
    return sum(t.coefficient * result.variable_values(t.variable) for t in row.terms())


def binding_prices(result: mathopt.SolveResult, rows: list[mathopt.LinearConstraint],
                   tol: float = 1e-6) -> dict[str, float] | None:
    """Row name -> dual value for every binding row, or None when the result has no duals."""
    if not result.has_dual_feasible_solution():
        return None
    prices = {}
    for row in rows:
        level = activity(row, result)
        bounds = [b for b in (row.lower_bound, row.upper_bound) if not math.isinf(b)]
        if any(abs(level - b) <= tol for b in bounds):
            prices[row.name] = result.dual_values(row)
    return prices


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=10, name="x")
    row = model.add_linear_constraint(x <= 4, name="cap")
    model.maximize(x)
    print(binding_prices(mathopt.solve(model, mathopt.SolverType.GLOP), [row]))
