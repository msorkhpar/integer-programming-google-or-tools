from __future__ import annotations

from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt


def legacy_plan(data: dict):
    """The old pywraplp script: returns (status name, cost, {variable name: value}) or (status name, None, None)."""
    solver = pywraplp.Solver.CreateSolver("SCIP")
    crews = {}
    for kind, (hours, cost, most, least) in data["crews"].items():
        crews[kind] = solver.IntVar(0, most, "crews_" + kind)
        crews[kind].SetBounds(least, most)                       # the union's minimum
    overtime = solver.NumVar(0, data["overtime_max"], "overtime")

    cover = solver.RowConstraint(data["need_low"], data["need_high"], "cover")
    for kind, (hours, cost, most, least) in data["crews"].items():
        cover.SetCoefficient(crews[kind], hours)
    cover.SetCoefficient(overtime, 1)

    spend = sum(cost * crews[k] for k, (hours, cost, most, least) in data["crews"].items())
    solver.Minimize(spend + data["overtime_rate"] * overtime)

    status = solver.Solve()
    names = {pywraplp.Solver.OPTIMAL: "OPTIMAL", pywraplp.Solver.FEASIBLE: "FEASIBLE",
             pywraplp.Solver.INFEASIBLE: "INFEASIBLE", pywraplp.Solver.UNBOUNDED: "UNBOUNDED"}
    if status != pywraplp.Solver.OPTIMAL:
        return names.get(status, "OTHER"), None, None
    plan = {v.name(): v.solution_value() for v in solver.variables()}
    return "OPTIMAL", solver.Objective().Value(), plan


def mathopt_plan(data: dict):
    """The same model in MathOpt, solved by SCIP; returns what legacy_plan returns."""
    # TODO: build the model of legacy_plan in MathOpt, solve it with SCIP, and return the same shape.
    return "", None, None


if __name__ == "__main__":
    depot = {"crews": {"line": (40, 30, 6, 1), "tree": (30, 20, 6, 0), "contract": (50, 45, 4, 0)},
             "need_low": 200, "need_high": 240, "overtime_max": 40, "overtime_rate": 0.5}
    print(legacy_plan(depot))
    print(mathopt_plan(depot))
