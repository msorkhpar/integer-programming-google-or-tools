from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def room(model: mathopt.Model, result: mathopt.SolveResult) -> dict[str, float]:
    """Each row's room at the solution: slack on a <= row, surplus on a >= row, the nearer side of a range."""
    # TODO: each row's room from its activity and its stored bounds. For now every row reports 0.
    return {row.name: 0.0 for row in model.linear_constraints()}


def binding(model: mathopt.Model, result: mathopt.SolveResult, tol: float = 1e-6) -> list[str]:
    """Names of the rows with no room left (within tol), in the order the model holds them."""
    # TODO: the rows whose room is at most tol.
    return []


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_variable(lb=0, ub=4, name="x")
    model.add_linear_constraint(x <= 10, name="cap")
    model.maximize(x)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(room(model, result), binding(model, result))
