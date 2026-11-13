"""Lesson 6.4.1's multi-period model in MathOpt, the version the PuLP port is checked against.

The same model as `timing_model.build`, the builder of lessons 6.4.1 to 6.4.4 (cumulative precedence, spread cash flow), cut
down to what lesson 6.4.1 builds, so this module's programs can run it on their own.
"""

from __future__ import annotations

import ctypes
import os
import sys

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


def build(portfolio: Portfolio) -> tuple[mathopt.Model, dict[tuple[str, int], mathopt.Variable]]:
    model = mathopt.Model(name="gridcap_timing")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str, by: int | None = None) -> mathopt.LinearExpression:
        return mathopt.LinearExpression() + sum(x[pid, t] for t in by_id[pid].starts() if by is None or t <= by)

    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            for t in c.starts():
                model.add_linear_constraint(started(c.project_id, by=t) <= started(c.parent, by=t - c.parent_lag),
                                            name=f"after_{c.project_id}_{t}")
    for year in portfolio.years:
        spend = mathopt.LinearExpression() + sum(amount * x[p.project_id, t]
                                                 for p in portfolio.projects for t in p.starts()
                                                 for y, amount in p.spend(t).items() if y == year)
        model.add_linear_constraint(spend <= portfolio.budget[year], name=f"budget_{year}")
    return model, x


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """`mathopt.solve` with HiGHS, with standard output sent to /dev/null for the call.

    The HiGHS bundled in OR-Tools 9.15 can print a stray debug line on a MIP solve, even
    with no log requested; the `solve_highs` of lessons 6.4.1 to 6.4.4 does the same.
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
