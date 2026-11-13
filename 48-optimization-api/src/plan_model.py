"""The GridCap planning model the module's API solves: the multi-period selection model of lessons 6.4.1 and 6.4.2.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.

One binary x[i, t] per project and allowed start year; must-do, once, alternative-group and
parent-after rows; each project's cost spread over its years of work; one budget row per year.
The API lets a request replace any year's budget, so `build` takes the budgets to use.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class PlanModel:
    portfolio: Portfolio
    budget: dict[int, int]
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]


def build(portfolio: Portfolio, budget: dict[int, int]) -> PlanModel:
    """The model of lesson 12.4.1, with B_y = budget[y]. Row names match the lesson's labels."""
    model = mathopt.Model(name=f"{portfolio.name} plan")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}

    def started(pid: str, by: int | None = None) -> mathopt.LinearExpression:
        p = portfolio.project(pid)
        return mathopt.LinearExpression(sum(x[pid, t] for t in p.starts() if by is None or t <= by))

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
    return PlanModel(portfolio, dict(budget), model, x)


def starts_of(pm: PlanModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the best plan starts."""
    values = result.variable_values()
    return dict(sorted((pid, t) for (pid, t), v in pm.x.items() if values[v] > 0.5))


def spend_of(portfolio: Portfolio, starts: dict[str, int]) -> dict[int, int]:
    """What a plan spends in each year of the horizon, from the data (not from the model)."""
    spend = {y: 0 for y in portfolio.years}
    for pid, t in starts.items():
        for year, amount in portfolio.project(pid).spend(t).items():
            spend[year] += amount
    return spend
