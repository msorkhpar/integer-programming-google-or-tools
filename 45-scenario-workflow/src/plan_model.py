"""The GridCap planning model that every scenario of this module builds and solves.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.

`build` writes the multi-period model of lessons 6.4.1 to 6.4.3 and 6.5.1 to 6.5.3: one binary
x[i, t] per project and allowed start year, a once or must-do row per project, one row per
alternative group, cumulative precedence rows for children, and a budget row per year with each
project's cost spread over its years of work. Planner overrides change only variable bounds
(lesson 6.5.6, and lesson 12.1.2 here), so they never add a row.

`solve_highs` keeps the bundled HiGHS's stray debug line out of the program's output
even with no log requested, as `timing_model.solve_highs` of lessons 6.4.1 to 6.4.4 does.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class Built:
    """A built model with its start variables, keyed by (project, start year)."""

    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]


def build(portfolio: Portfolio, budget: dict[int, int],
          bounds: dict[tuple[str, int], tuple[int, int]]) -> Built:
    """The planning model for one scenario's budgets, with the overrides' bounds applied last."""
    model = mathopt.Model(name=portfolio.name)
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}

    def started(pid: str, upto: int | None = None) -> mathopt.LinearExpression:
        terms = mathopt.LinearExpression()
        for t in portfolio.project(pid).starts():
            if upto is None or t <= upto:
                terms += x[pid, t]
        return terms

    for p in portfolio.projects:
        i = p.project_id
        if p.must_do:
            model.add_linear_constraint(started(i) == 1, name=f"must_{i}")
        else:
            model.add_linear_constraint(started(i) <= 1, name=f"once_{i}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in sorted(groups.items()):
        model.add_linear_constraint(sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            for t in c.starts():
                model.add_linear_constraint(started(c.project_id, t) <= started(c.parent, t - c.parent_lag),
                                            name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        model.add_linear_constraint(spend[y] <= budget[y], name=f"budget_{y}")
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    for key, (lower, upper) in bounds.items():
        x[key].lower_bound, x[key].upper_bound = lower, upper
    return Built(model, x)


def solve_highs(model: mathopt.Model, gap: float = 0.0) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the output."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=gap))
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
