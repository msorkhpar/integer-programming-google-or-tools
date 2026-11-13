from __future__ import annotations

from ortools.linear_solver import pywraplp


def pick_backend(preferences: list[str]) -> str | None:
    """The first solver ID in `preferences` that is present and solves MIPs, or None."""
    for solver_id in preferences:
        solver = pywraplp.Solver.CreateSolver(solver_id)
        if solver is not None and solver.IsMip():
            return solver_id
    return None


if __name__ == "__main__":
    print(pick_backend(["GUROBI", "GLOP", "SCIP"]))
