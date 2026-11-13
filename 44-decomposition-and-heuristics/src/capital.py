"""The multi-year GridCap model every lesson of this module decomposes, and a quiet HiGHS solve.

It is the timing model of lesson 6.4.1 with the spread costs of lesson 6.4.2 and the cumulative
precedence rows of lesson 6.4.3, written again here so that this module's programs run on their
own. `crews=True` adds lesson 4.6.1's crew rows (crew-months per program and year).
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class Capital:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]            # x[i, t] = 1: project i starts in year t
    spend: dict[int, mathopt.LinearExpression]
    budget: dict[int, mathopt.LinearConstraint] = field(default_factory=dict)
    crews: dict[tuple[str, int], mathopt.LinearConstraint] = field(default_factory=dict)


def crew_use(portfolio: Portfolio, x: dict) -> dict[tuple[str, int], mathopt.LinearExpression]:
    """Crew-months each program uses in each year: m_i in every year project i is worked on."""
    use: dict[tuple[str, int], mathopt.LinearExpression] = {}
    for p in portfolio.projects:
        for t in p.starts():
            for y in p.spend(t):
                if y in portfolio.years:
                    use.setdefault((p.program, y), mathopt.LinearExpression())
                    use[p.program, y] += p.crew_months * x[p.project_id, t]
    return use


def build(portfolio: Portfolio, *, integer: bool = True, budget_rows: bool = True,
          crews: bool = False) -> Capital:
    model = mathopt.Model(name=f"{portfolio.name} capital plan")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str):
        return sum(x[pid, t] for t in by_id[pid].starts())

    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    for g, members in alt_groups(portfolio).items():
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
    cap = Capital(model, x, spend)
    if budget_rows:
        cap.budget = {y: model.add_linear_constraint(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
                      for y in portfolio.years}
    if crews:
        for (g, y), use in crew_use(portfolio, x).items():
            cap.crews[g, y] = model.add_linear_constraint(use <= portfolio.crews[g, y], name=f"crews_{g}_{y}")
    model.maximize(npv_of(portfolio, x))
    return cap


def npv_of(portfolio: Portfolio, x: dict) -> mathopt.LinearExpression:
    return sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())


def alt_groups(portfolio: Portfolio) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    return groups


def schedule(cap: Capital, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    values = result.variable_values()
    return {pid: t for (pid, t), v in cap.x.items() if values[v] > 0.5}


def value(portfolio: Portfolio, plan: dict[str, int]) -> int:
    """A plan's NPV, summed in plain Python from the data."""
    return sum(portfolio.project(pid).npv[t] for pid, t in plan.items())


def violations(portfolio: Portfolio, plan: dict[str, int], *, crews: bool = False) -> list[str]:
    """Every rule of `build` that the plan breaks, checked in plain Python."""
    broken = []
    by_id = {p.project_id: p for p in portfolio.projects}
    for p in portfolio.projects:
        if p.must_do and p.project_id not in plan:
            broken.append(f"must_{p.project_id}")
        if p.project_id in plan and plan[p.project_id] not in p.starts():
            broken.append(f"window_{p.project_id}")
    for g, members in alt_groups(portfolio).items():
        if sum(m in plan for m in members) > 1:
            broken.append(f"alt_{g}")
    for pid, t in plan.items():
        c = by_id[pid]
        if c.parent and (c.parent not in plan or plan[c.parent] > t - c.parent_lag):
            broken.append(f"after_{pid}")
    spend = {y: 0 for y in portfolio.years}
    use: dict[tuple[str, int], int] = {}
    for pid, t in plan.items():
        for y, amount in by_id[pid].spend(t).items():
            spend[y] += amount
            use[by_id[pid].program, y] = use.get((by_id[pid].program, y), 0) + by_id[pid].crew_months
    broken += [f"budget_{y}" for y in portfolio.years if spend[y] > portfolio.budget[y]]
    if crews:
        broken += [f"crews_{g}_{y}" for (g, y), u in use.items() if u > portfolio.crews[g, y]]
    return broken


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None,
                **kwargs) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping its stray debug line out of the output."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params, **kwargs)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
