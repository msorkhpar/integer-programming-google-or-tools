"""GridCap's project-selection MILP in MathOpt, and a quiet HiGHS solve that can keep the log."""

from __future__ import annotations

import ctypes
import os
import re
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class Selection:
    model: mathopt.Model
    x: dict[str, mathopt.Variable]                       # x[i] = 1: project i is in the plan
    budget: dict[int, mathopt.LinearConstraint]         # one budget row per year


def build(portfolio: Portfolio, integer: bool = True) -> Selection:
    """Pick projects, each starting at its earliest start, to maximize NPV within each year's budget.

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
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    for p in portfolio.projects:
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"needs_{p.project_id}")
    budget = {}
    for y in portfolio.years:
        spend = sum(p.spend(p.earliest_start).get(y, 0) * x[p.project_id] for p in portfolio.projects)
        budget[y] = model.add_linear_constraint(spend <= portfolio.budget[y], name=f"budget_{y}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return Selection(model, x, budget)


def plan(sel: Selection, result: mathopt.SolveResult) -> set[str]:
    """The projects the result's best plan selects."""
    return {i for i, v in sel.x.items() if result.variable_values(v) > 0.5}


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None,
                log: list[str] | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints `HighsMipSolverData::transformNewIntegerFeasible
    Solution tmpSolver.run();` on some MIP solves, with no log requested, as buffered C output. The
    process's standard output points at /dev/null for the solve, and that C buffer is flushed there.
    Pass a list as `log` to collect the solver's own log lines in it.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params,
                             msg_cb=log.extend if log is not None else None)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


TIME = re.compile(r"(\s)\d+\.\d+s$")


def mask_time(line: str) -> str:
    """A HiGHS progress line ends in the wall-clock time, which changes on every run."""
    return TIME.sub(r"\1<t>s", line)
