"""The multi-period start-year model of lessons 6.4.1-6.4.2, with any per-start objective coefficients."""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from asset_curves import AGE_AFTER, risk_reduction
from gridcap import Portfolio

WINDOW = 10        # years over which a project's risk reduction is counted, from the plan's first year


def risk_coefficients(portfolio: Portfolio, eta_of=None, rate: float | None = None) -> dict[tuple[str, int], float]:
    """rr[i, s]: discounted risk removed over the window if project i starts in year s, $k."""
    window = tuple(range(portfolio.years[0], portfolio.years[0] + WINDOW))
    rate = portfolio.discount_rate if rate is None else rate
    rr = {}
    for p in portfolio.projects:
        a = portfolio.asset(p.asset_id)
        if eta_of is not None:
            a = eta_of(a)
        for s in p.starts():
            rr[p.project_id, s] = risk_reduction(a, window, s, p.duration, AGE_AFTER[p.intervention], rate)
    return rr


@dataclass
class StartModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]


def build(portfolio: Portfolio, coefficient: dict[tuple[str, int], float]) -> StartModel:
    model = mathopt.Model(name=f"{portfolio.name} starts")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
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
            parent = by_id[c.parent]
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        model.add_linear_constraint(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
    model.maximize(sum(coefficient[key] * var for key, var in x.items()))
    return StartModel(model, x)


def solve_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with HiGHS to a zero gap, keeping the engine's stray debug line out of the output."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def plan_of(sm: StartModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in sm.x.items() if result.variable_values(v) > 0.5}
