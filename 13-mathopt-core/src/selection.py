"""GridCap's project-selection model in MathOpt, and a solve that keeps solver noise off the output.

Every program of module 13 builds its GridCap model here, so each lesson states the formulation
once and the code follows it row by row.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class Selection:
    model: mathopt.Model
    x: dict[str, mathopt.Variable]                        # x[i] = 1: project i is in the plan
    budget: dict[int, mathopt.LinearConstraint]          # budget_y, one row per year


def build(portfolio: Portfolio, integer: bool = True) -> Selection:
    """Fund projects, each starting at its earliest start, to maximize NPV within each year's budget.

    With `integer=False` every x[i] may take any value from 0 to 1: the LP relaxation.
    """
    model = mathopt.Model(name=f"{portfolio.name}-selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(mathopt.fast_sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    for p in portfolio.projects:
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"needs_{p.project_id}")
    budget = {}
    for y in portfolio.years:
        spend = mathopt.fast_sum(p.spend(p.earliest_start).get(y, 0) * x[p.project_id]
                                 for p in portfolio.projects)
        budget[y] = model.add_linear_constraint(spend <= portfolio.budget[y], name=f"budget_{y}")
    model.maximize(mathopt.fast_sum(p.value * x[p.project_id] for p in portfolio.projects))
    return Selection(model, x, budget)


def plan(sel: Selection, result: mathopt.SolveResult) -> list[str]:
    """The projects the result's best plan funds, in id order."""
    return sorted(i for i, v in sel.x.items() if result.variable_values(v) > 0.5)


def solve(model: mathopt.Model, solver: mathopt.SolverType,
          params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """`mathopt.solve`, with the process's standard output sent to /dev/null while the solver runs.

    The HiGHS bundled in OR-Tools 9.15.6755 can print a stray debug line on a MIP solve even with no
    log requested. It is buffered C output, so this flushes it where it goes.
    Python's own `print` is unaffected outside the call.
    """
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
