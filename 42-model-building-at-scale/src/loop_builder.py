"""The timing model of lessons 6.4.1-6.4.2, built with plain loops over GridCap objects.

A copy of lesson 6.4.2's `timing_model.build` with its defaults (spread cash flow, cumulative
precedence), so this module's programs run on their own. It is the reference every faster builder
in this module must reproduce exactly. GridCap is fictional.
"""

from __future__ import annotations

import ctypes
import os
import sys

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


def build_loops(portfolio: Portfolio) -> mathopt.Model:
    model = mathopt.Model(name=f"{portfolio.name} timing")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=True, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str):
        return sum(x[pid, t] for t in by_id[pid].starts())

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
            parent, lag = by_id[c.parent], c.parent_lag
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - lag),
                    name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for year in portfolio.years:
        model.add_linear_constraint(spend[year] <= portfolio.budget[year], name=f"budget_{year}")
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return model


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, with OR-Tools 9.15's stray HiGHS debug line kept out of the output."""
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
