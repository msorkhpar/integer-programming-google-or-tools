from __future__ import annotations

from ortools.linear_solver import pywraplp

NAMES = {pywraplp.Solver.OPTIMAL: "OPTIMAL", pywraplp.Solver.FEASIBLE: "FEASIBLE",
         pywraplp.Solver.INFEASIBLE: "INFEASIBLE", pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
         pywraplp.Solver.ABNORMAL: "ABNORMAL", pywraplp.Solver.MODEL_INVALID: "MODEL_INVALID",
         pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED"}


def outcome(solver: pywraplp.Solver, status: int, x: dict) -> dict:
    """What a report may say about a solve: the status by name, and a value and plan only if there is one."""
    has_solution = status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE)
    return {
        "status": NAMES[status],
        "value": solver.Objective().Value() if has_solution else None,
        "plan": {name: var.solution_value() for name, var in x.items()} if has_solution else None,
    }


def crews_model(need: int, most: int):
    """Hire crews of two kinds, at most `most` of each, to cover `need`; a small model to try outcome() on."""
    solver = pywraplp.Solver.CreateSolver("SCIP")
    x = {"line": solver.IntVar(0, most, "line"), "field": solver.IntVar(0, most, "field")}
    solver.Add(2 * x["line"] + x["field"] >= need, "cover")
    solver.Minimize(5 * x["line"] + 3 * x["field"])
    return solver, x


if __name__ == "__main__":
    solver, x = crews_model(need=7, most=5)
    print(outcome(solver, solver.Solve(), x))
