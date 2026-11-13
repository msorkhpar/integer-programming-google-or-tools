from __future__ import annotations

from ortools.linear_solver import pywraplp


def allowed(solver: pywraplp.Solver, values: dict, tol: float = 1e-6) -> bool:
    """Does the plan {variable name: value} keep every bound, integrality and row of the model?"""
    for var in solver.variables():
        value = values[var.name()]
        if value < var.lb() - tol or value > var.ub() + tol:
            return False
        if var.Integer() and abs(value - round(value)) > tol:
            return False
    for row in solver.constraints():
        activity = sum(row.GetCoefficient(var) * values[var.name()] for var in solver.variables())
        if activity < row.lb() - tol or activity > row.ub() + tol:
            return False
    return True


def depot_model() -> pywraplp.Solver:
    """A small model to try allowed() on."""
    solver = pywraplp.Solver.CreateSolver("SCIP")
    line = solver.IntVar(0, 6, "line")
    tree = solver.IntVar(0, 6, "tree")
    overtime = solver.NumVar(0, 40, "overtime")
    cover = solver.RowConstraint(200, 240, "cover")
    cover.SetCoefficient(line, 40)
    cover.SetCoefficient(tree, 30)
    cover.SetCoefficient(overtime, 1)
    solver.Add(30 * line + 20 * tree <= 200, "budget")
    return solver


if __name__ == "__main__":
    print(allowed(depot_model(), {"line": 2, "tree": 4, "overtime": 0}))
