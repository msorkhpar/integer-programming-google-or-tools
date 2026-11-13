"""A multi-period GridCap selection model in MathOpt: when, not only whether, to start each project."""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class TimingModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[i, t] = 1: project i starts in year t
    spend: dict[int, mathopt.LinearExpression] = field(default_factory=dict)
    budget: dict[int, mathopt.LinearConstraint] = field(default_factory=dict)


def start_variables(model: mathopt.Model, portfolio: Portfolio, integer: bool = True) -> dict:
    """One variable per project and allowed start year. Years outside the window get none."""
    return {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
            for p in portfolio.projects for t in p.starts()}


def spend_by_year(portfolio: Portfolio, x: dict) -> dict[int, mathopt.LinearExpression]:
    """What the plan spends in each calendar year, with each project's cost spread over its life."""
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    return spend


def lump_by_year(portfolio: Portfolio, x: dict) -> dict[int, mathopt.LinearExpression]:
    """The shortcut this module warns about: the whole capex charged to the start year."""
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            spend[t] += p.capex * x[p.project_id, t]
    return spend


def build(portfolio: Portfolio, *, integer: bool = True, precedence: str = "cumulative",
          cash_flow: str = "spread") -> TimingModel:
    model = mathopt.Model(name=f"{portfolio.name} timing")
    x = start_variables(model, portfolio, integer)
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
            add_precedence(model, x, by_id[c.parent], c, precedence)

    spend = spend_by_year(portfolio, x) if cash_flow == "spread" else lump_by_year(portfolio, x)
    budget = {year: model.add_linear_constraint(spend[year] <= portfolio.budget[year], name=f"budget_{year}")
              for year in portfolio.years}
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return TimingModel(model, x, spend, budget)


def add_precedence(model, x, parent, child, form: str) -> None:
    """The child starts only if the parent does, at least `child.parent_lag` years after it."""
    lag = child.parent_lag
    if form == "aggregated":
        # One constraint for "funded only with the parent", one on the start-year averages.
        model.add_linear_constraint(sum(x[child.project_id, t] for t in child.starts())
                                    <= sum(x[parent.project_id, s] for s in parent.starts()),
                                    name=f"needs_{child.project_id}")
        # Smallest valid big-M: with the child unfunded the row must allow the parent's latest start.
        big = max(parent.starts()) + lag
        model.add_linear_constraint(
            sum(t * x[child.project_id, t] for t in child.starts())
            >= sum((s + lag) * x[parent.project_id, s] for s in parent.starts())
            - big * (1 - sum(x[child.project_id, t] for t in child.starts())),
            name=f"after_{child.project_id}")
    elif form == "cumulative":
        # For every year: the child has started by t only if the parent started by t - lag.
        for t in child.starts():
            model.add_linear_constraint(
                sum(x[child.project_id, u] for u in child.starts() if u <= t)
                <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - lag),
                name=f"after_{child.project_id}_{t}")
    else:
        raise ValueError(form)


def schedule(tm: TimingModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in tm.x.items() if result.variable_values(v) > 0.5}


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints `HighsMipSolverData::transformNewIntegerFeasible
    Solution tmpSolver.run();` on some MIP solves, with no log requested. It
    is buffered C output, so it would appear when the program exits. Here the process's standard
    output points at /dev/null for the solve and that buffer is flushed before it is restored.
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
