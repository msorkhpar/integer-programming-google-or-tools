"""The two GridCap selection models of module 10, and quiet ways to solve them.

* The **budget knapsack**: fund each project or not, one budget row (`capital_budget`), nothing else.
  Lesson 3.3.1 cuts its LP relaxation by hand.
* The **five-year selection model**: fund each project or not, at its earliest start; one budget row
  for each of the plan's first five years, plus the must-do, parent and alternative rules. Lessons
  3.3.2 to 3.3.4 presolve it, run heuristics on it and read its log.

GridCap is a fictional utility; its numbers are teaching data.
"""

from __future__ import annotations

import ctypes
import os
import re
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

PLAN_YEARS = 5


@dataclass
class Selection:
    model: mathopt.Model
    x: dict[str, mathopt.Variable]                       # x[i] = 1: project i is funded
    rows: dict[str, mathopt.LinearConstraint] = field(default_factory=dict)


def knapsack(portfolio: Portfolio, *, integer: bool = True) -> Selection:
    """max sum v_i x_i  s.t.  sum c_i x_i <= B (the one budget row), 0 <= x_i <= 1."""
    model = mathopt.Model(name=f"{portfolio.name} knapsack")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    budget = model.add_linear_constraint(
        sum(p.capex * x[p.project_id] for p in portfolio.projects) <= portfolio.capital_budget, name="budget")
    return Selection(model, x, {"budget": budget})


def spend(portfolio: Portfolio, year: int) -> dict[str, int]:
    """What each project spends in `year` if it starts at its earliest start (projects spending 0 left out)."""
    return {p.project_id: p.spend(p.earliest_start)[year] for p in portfolio.projects
            if year in p.spend(p.earliest_start)}


def plan_years(portfolio: Portfolio) -> tuple[int, ...]:
    return portfolio.years[:PLAN_YEARS]


def five_year(portfolio: Portfolio, *, integer: bool = True) -> Selection:
    """The five-year selection model (the running MILP of lessons 3.3.1 to 3.3.4)."""
    model = mathopt.Model(name="selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    rows = {}
    for y in plan_years(portfolio):
        rows[f"budget_{y}"] = model.add_linear_constraint(
            sum(c * x[i] for i, c in spend(portfolio, y).items()) <= portfolio.budget[y], name=f"budget_{y}")
    for p in portfolio.projects:
        if p.must_do:
            rows[f"must_{p.project_id}"] = model.add_linear_constraint(
                x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            rows[f"after_{p.project_id}"] = model.add_linear_constraint(
                x[p.project_id] <= x[p.parent], name=f"after_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, ids in sorted(groups.items()):
        rows[f"alt_{g}"] = model.add_linear_constraint(sum(x[i] for i in ids) <= 1, name=f"alt_{g}")
    return Selection(model, x, rows)


def solve_quiet(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS,
                params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve, keeping the bundled HiGHS's stray debug line out of the program's output.

    OR-Tools 9.15.6755's HiGHS prints `HighsMipSolverData::transformNewIntegerFeasibleSolution
    tmpSolver.run();` on some MIP solves, as C output buffered until the program exits. Standard
    output points at /dev/null for the solve, and the C buffer is flushed there before it is restored.
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


TIMES = [
    (re.compile(r"(\s)\d+(\.\d+)?s$"), r"\1<t>s"),                     # presolve rounds, progress rows
    (re.compile(r"^(\s*Timing\s+)[\d.]+"), r"\1<t>"),                   # report: wall-clock seconds
    (re.compile(r"^(\s*P-D integral\s+)[\d.e+-]+"), r"\1<t>"),          # report: changes from run to run
]


def mask_times(line: str) -> str:
    """Wall-clock times change on every run; the rest of a HiGHS MIP log does not."""
    for pattern, replacement in TIMES:
        line = pattern.sub(replacement, line)
    return line


def solve_with_log(model: mathopt.Model, params: mathopt.SolveParameters | None = None,
                   solver: mathopt.SolverType = mathopt.SolverType.HIGHS) -> tuple[mathopt.SolveResult, list[str]]:
    """Solve and keep every log line the solver wrote, in order, with its times masked."""
    lines: list[str] = []
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        result = mathopt.solve(model, solver, params=params, msg_cb=lines.extend)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
    return result, [mask_times(line) for line in lines]


def funded(sel: Selection, result: mathopt.SolveResult) -> list[str]:
    return [i for i, v in sel.x.items() if result.variable_values(v) > 0.5]
