"""The one-period GridCap selection model that module 28 adds its curves to, and the helpers its programs share.

GridCap is a fictional utility's portfolio. `build` writes the model of lesson 1.1.1: one binary per
project, one capital budget, and the must-do, parent and alternative rules. Each program of this
module builds it, puts a piecewise-linear curve into its budget row or objective, and solves.
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
    portfolio: Portfolio
    model: mathopt.Model
    x: dict[str, mathopt.Variable]          # x[i] = 1: project i is funded
    budget: mathopt.LinearConstraint


def build(portfolio: Portfolio, *, integer: bool = True) -> Selection:
    """The selection model; integer=False gives its LP relaxation (same rows, 0 <= x <= 1)."""
    model = mathopt.Model(name=f"{portfolio.name} selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    budget = model.add_linear_constraint(
        sum(p.capex * x[p.project_id] for p in portfolio.projects) <= portfolio.capital_budget, name="budget")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return Selection(portfolio, model, x, budget)


def ids(portfolio: Portfolio, *, program: str | None = None) -> list[str]:
    """The projects of one program, in portfolio order."""
    return [p.project_id for p in portfolio.projects if program is None or p.program == program]


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints a debug line on some MIP solves with no log
    requested. Standard output points at /dev/null for the solve, and the C
    buffer is flushed before it is restored.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def funded(sel: Selection, result: mathopt.SolveResult) -> list[str]:
    """The projects a solution funds, in portfolio order."""
    return [pid for pid, v in sel.x.items() if result.variable_values(v) > 0.5]
