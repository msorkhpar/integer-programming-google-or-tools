from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def room(model: mathopt.Model, result: mathopt.SolveResult) -> dict[str, float]:
    """Each row's room at the solution: slack on a <= row, surplus on a >= row, the nearer side of a range."""
    values = result.variable_values()
    rooms = {}
    for row in model.linear_constraints():
        a = sum(term.coefficient * values[term.variable] for term in row.terms())
        lo, hi = row.lower_bound, row.upper_bound
        if math.isfinite(lo) and math.isfinite(hi):
            rooms[row.name] = min(hi - a, a - lo)
        elif math.isfinite(hi):
            rooms[row.name] = hi - a
        else:
            rooms[row.name] = a - lo
    return rooms


def binding(model: mathopt.Model, result: mathopt.SolveResult, tol: float = 1e-6) -> list[str]:
    """Names of the rows with no room left (within tol), in the order the model holds them."""
    return [name for name, r in room(model, result).items() if r <= tol]


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=4, name="x")
    model.add_linear_constraint(x <= 10, name="cap")
    model.maximize(x)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(room(model, result), binding(model, result))
