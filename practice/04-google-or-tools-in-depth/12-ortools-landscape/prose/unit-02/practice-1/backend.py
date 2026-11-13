from __future__ import annotations

from ortools.linear_solver import pywraplp


def pick_backend(preferences: list[str]) -> str | None:
    """The first solver ID in `preferences` that is present and solves MIPs, or None."""
    # TODO: try each ID in order with CreateSolver; keep the first that exists and is a MIP solver.
    return "NONE"


if __name__ == "__main__":
    print(pick_backend(["GUROBI", "GLOP", "SCIP"]))
