from __future__ import annotations

from ortools.linear_solver import pywraplp


def add_rows(solver: pywraplp.Solver, x: dict, rows: list) -> None:
    """Add each (name, lower, coefficients, upper) row; a bound of None means there is none."""
    for name, lower, coefficients, upper in rows:
        lb = -solver.infinity() if lower is None else lower
        ub = solver.infinity() if upper is None else upper
        row = solver.RowConstraint(lb, ub, name)
        for var_name, a in coefficients.items():
            row.SetCoefficient(x[var_name], a)


def best(rows: list, objective: dict, names=("x0", "x1")) -> float | None:
    """Maximize the objective over integers 0..10 under the rows; None unless optimal."""
    solver = pywraplp.Solver.CreateSolver("SCIP")
    x = {n: solver.IntVar(0, 10, n) for n in names}
    add_rows(solver, x, rows)
    solver.Maximize(sum(c * x[n] for n, c in objective.items()))
    if solver.Solve() != pywraplp.Solver.OPTIMAL:
        return None
    return round(solver.Objective().Value(), 6)


if __name__ == "__main__":
    print(best([("cap", None, {"x0": 1, "x1": 2}, 8)], {"x0": 1, "x1": 3}))
