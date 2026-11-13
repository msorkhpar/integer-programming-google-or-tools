"""Lesson 4.7.2: the legacy pywraplp selection script of lesson 4.7.1, ported to MathOpt.

Same rows, same names, same answer; the model no longer belongs to a solver. GridCap is a
fictional utility's portfolio.
"""

from __future__ import annotations

import ctypes
import datetime
import os
import sys

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


def build(portfolio: Portfolio) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    model = mathopt.Model(name="selection")
    x = {}
    for p in portfolio.projects:
        x[p.project_id] = model.add_binary_variable(name="x_" + p.project_id)

    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")

    for p in portfolio.projects:
        if p.must_do:
            x[p.project_id].lower_bound = 1                       # must-do: fixed at 1
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name="parent_" + p.project_id)

    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g, members in groups.items():
        model.add_linear_constraint(sum(members) <= 1, name="alt_" + g)

    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return model, x


def quiet_solve(model: mathopt.Model, solver: mathopt.SolverType, params=None) -> mathopt.SolveResult:
    """Solve with standard output pointed at /dev/null, so a back end's stray lines stay out."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, solver, params=params)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def solve_ported(portfolio: Portfolio, solver: mathopt.SolverType = mathopt.SolverType.GSCIP,
                 time_limit_ms: int = 60_000, relative_gap: float | None = None):
    """Return (termination reason, value, funded project ids, model)."""
    model, x = build(portfolio)
    params = mathopt.SolveParameters(time_limit=datetime.timedelta(milliseconds=time_limit_ms),
                                     relative_gap_tolerance=relative_gap)
    result = quiet_solve(model, solver, params)
    reason = result.termination.reason
    if reason not in (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE):
        return reason, None, [], model
    funded = [pid for pid, var in x.items() if result.variable_values(var) > 0.5]
    return reason, result.objective_value(), funded, model
