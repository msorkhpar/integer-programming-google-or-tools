from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def binding_prices(result: mathopt.SolveResult, rows: list[mathopt.LinearConstraint],
                   tol: float = 1e-6) -> dict[str, float] | None:
    """Row name -> dual value for every binding row, or None when the result has no duals."""
    # TODO: None without duals; otherwise the dual value of each row whose activity sits on a finite bound.
    return {}


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=10, name="x")
    row = model.add_linear_constraint(x <= 4, name="cap")
    model.maximize(x)
    print(binding_prices(mathopt.solve(model, mathopt.SolverType.GLOP), [row]))
