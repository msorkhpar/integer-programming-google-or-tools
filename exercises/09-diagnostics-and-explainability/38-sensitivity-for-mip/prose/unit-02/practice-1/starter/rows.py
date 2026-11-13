from __future__ import annotations

from ortools.math_opt.python import mathopt


def row_report(model: mathopt.Model, result: mathopt.SolveResult, tol: float = 1e-6) -> dict:
    """For each row of a solved LP: its slack, whether it binds, and its price."""
    # TODO: define "binding" from the row's two sides, then fill in each row's three entries.
    return {row.name: {"slack": 0.0, "binding": False, "price": 0.0} for row in model.linear_constraints()}


if __name__ == "__main__":
    m = mathopt.Model()
    x = m.add_variable(lb=0, name="chlorine")
    m.add_linear_constraint(x <= 40, name="stock")
    m.maximize(x)
    print(row_report(m, mathopt.solve(m, mathopt.SolverType.GLOP)))
