from __future__ import annotations

from ortools.math_opt.python import mathopt


def row_report(model: mathopt.Model, result: mathopt.SolveResult, tol: float = 1e-6) -> dict:
    """For each row of a solved LP: its slack, whether it binds, and its price."""
    report = {}
    for row in model.linear_constraints():
        activity = sum(t.coefficient * result.variable_values(t.variable) for t in row.terms())
        slack = min(row.upper_bound - activity, activity - row.lower_bound)   # an infinite bound never wins
        report[row.name] = {"slack": slack, "binding": abs(slack) <= tol, "price": result.dual_values(row)}
    return report


if __name__ == "__main__":
    m = mathopt.Model()
    x = m.add_variable(lb=0, name="chlorine")
    m.add_linear_constraint(x <= 40, name="stock")
    m.maximize(x)
    print(row_report(m, mathopt.solve(m, mathopt.SolverType.GLOP)))
