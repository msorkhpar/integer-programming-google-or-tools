"""Lesson 4.7.1: a GridCap selection script in the style of older pywraplp code, to be read and ported.

The model is lesson 1.1.1's: fund projects to maximize value within one capital budget, with
must-do, parent and alternative-group rules. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

from ortools.linear_solver import pywraplp

from gridcap import Portfolio


def solve_legacy(portfolio: Portfolio, backend: str = "SCIP", time_limit_ms: int = 60_000,
                 relative_gap: float | None = None):
    """Return (status, value, funded project ids, solver)."""
    solver = pywraplp.Solver.CreateSolver(backend)
    solver.SetTimeLimit(time_limit_ms)                    # milliseconds

    x = {}
    for p in portfolio.projects:
        x[p.project_id] = solver.BoolVar("x_" + p.project_id)

    budget = solver.RowConstraint(-solver.infinity(), portfolio.capital_budget, "budget")
    for p in portfolio.projects:
        budget.SetCoefficient(x[p.project_id], p.capex)

    for p in portfolio.projects:
        if p.must_do:
            x[p.project_id].SetBounds(1, 1)               # must-do: fixed at 1
        if p.parent:
            solver.Add(x[p.project_id] <= x[p.parent], "parent_" + p.project_id)

    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g, members in groups.items():
        solver.Add(solver.Sum(members) <= 1, "alt_" + g)

    objective = solver.Objective()
    for p in portfolio.projects:
        objective.SetCoefficient(x[p.project_id], p.value)
    objective.SetMaximization()

    params = pywraplp.MPSolverParameters()
    if relative_gap is not None:
        params.SetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP, relative_gap)
    status = solver.Solve(params)
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return status, None, [], solver
    funded = [pid for pid, var in x.items() if var.solution_value() > 0.5]
    return status, objective.Value(), funded, solver
