"""The regional timing model of this module: when to start each project of one region, in three APIs.

It is the multi-period model of lesson 6.4.1, restricted to one region of a GridCap
medium portfolio so that one solve takes seconds, not minutes. The same rows are built three ways,
because the solvers this module measures are reached through three APIs: MathOpt (HiGHS, SCIP),
CP-SAT's own `cp_model`, and gurobipy. GridCap is fictional.

A plan is a dict {project id: start year}; a project not in it is not started.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import Portfolio, generate

PORTFOLIO_SEEDS = (2027, 1)
REGIONS = ("Ridge", "Valley", "Coast", "Plains")


def region_portfolio(pf: Portfolio, region: str) -> Portfolio:
    """One region's projects (a child only with its parent), with each year's budget scaled to the region.

    The scale is the region's share of the whole portfolio's spend in that year, if every project
    started as early as it can; each year is then raised, if needed, to the region's must-do spend
    in that year, so that every must-do project fits at its earliest start.
    """
    ids = {p.project_id for p in pf.projects if p.region == region}
    projects = tuple(p for p in pf.projects if p.project_id in ids and (p.parent is None or p.parent in ids))
    full = {y: sum(p.spend(p.earliest_start).get(y, 0) for p in pf.projects) for y in pf.years}
    share = {y: sum(p.spend(p.earliest_start).get(y, 0) for p in projects) for y in pf.years}
    must = {y: sum(p.spend(p.earliest_start).get(y, 0) for p in projects if p.must_do) for y in pf.years}
    budget = {y: max(pf.budget[y] * share[y] // max(full[y], 1), must[y]) for y in pf.years}
    return replace(pf, name=f"{region}-{pf.seed}", projects=projects, budget=budget,
                   region_budget={}, region_floor={}, crews={})


def instance_set() -> list[Portfolio]:
    """Every region of the medium portfolios drawn with each seed: eight regional plans."""
    return [region_portfolio(generate("medium", seed), region)
            for seed in PORTFOLIO_SEEDS for region in REGIONS]


def groups(pf: Portfolio) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for p in pf.projects:
        if p.alt_group:
            found.setdefault(p.alt_group, []).append(p.project_id)
    return {g: m for g, m in found.items() if len(m) > 1}


def keys(pf: Portfolio) -> list[tuple[str, int]]:
    """Every (project, start year) pair the model has a variable for."""
    return [(p.project_id, t) for p in pf.projects for t in p.starts()]


@dataclass
class PlanModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[i, t] = 1: project i starts in year t


def build(pf: Portfolio) -> PlanModel:
    model = mathopt.Model(name=pf.name)
    x = {(i, t): model.add_binary_variable(name=f"x_{i}_{t}") for i, t in keys(pf)}
    by_id = {p.project_id: p for p in pf.projects}

    def started(i: str, by: int | None = None):
        return sum(x[i, t] for t in by_id[i].starts() if by is None or t <= by)

    for p in pf.projects:
        row = started(p.project_id) == 1 if p.must_do else started(p.project_id) <= 1
        model.add_linear_constraint(row, name=f"{'must' if p.must_do else 'once'}_{p.project_id}")
    for g, members in groups(pf).items():
        model.add_linear_constraint(sum(started(i) for i in members) <= 1, name=f"alt_{g}")
    for c in pf.projects:
        if c.parent:
            for t in c.starts():
                model.add_linear_constraint(started(c.project_id, t) <= started(c.parent, t - c.parent_lag),
                                            name=f"after_{c.project_id}_{t}")
    for y in pf.years:
        spend = sum((a * x[p.project_id, t] for p in pf.projects for t in p.starts()
                     for year, a in p.spend(t).items() if year == y), start=mathopt.LinearExpression())
        model.add_linear_constraint(spend <= pf.budget[y], name=f"budget_{y}")
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in pf.projects for t in p.starts()))
    return PlanModel(model, x)


def build_cpsat(pf: Portfolio) -> tuple[cp_model.CpModel, dict[tuple[str, int], cp_model.IntVar]]:
    model = cp_model.CpModel()
    x = {(i, t): model.new_bool_var(f"x_{i}_{t}") for i, t in keys(pf)}
    by_id = {p.project_id: p for p in pf.projects}

    def started(i: str, by: int | None = None):
        return sum(x[i, t] for t in by_id[i].starts() if by is None or t <= by)

    for p in pf.projects:
        model.add(started(p.project_id) == 1 if p.must_do else started(p.project_id) <= 1)
    for members in groups(pf).values():
        model.add(sum(started(i) for i in members) <= 1)
    for c in pf.projects:
        if c.parent:
            for t in c.starts():
                model.add(started(c.project_id, t) <= started(c.parent, t - c.parent_lag))
    for y in pf.years:
        terms = [a * x[p.project_id, t] for p in pf.projects for t in p.starts()
                 for year, a in p.spend(t).items() if year == y]
        if terms:
            model.add(sum(terms) <= pf.budget[y])
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in pf.projects for t in p.starts()))
    return model, x


def value(pf: Portfolio, plan: dict[str, int]) -> int:
    """The plan's NPV, $k."""
    return sum(pf.project(i).npv[t] for i, t in plan.items())


def broken(pf: Portfolio, plan: dict[str, int]) -> list[str]:
    """The names of the rows the plan breaks, in the model's own names."""
    by_id = {p.project_id: p for p in pf.projects}
    out = [f"unknown_{i}_{t}" for i, t in plan.items() if i not in by_id or t not in by_id[i].starts()]
    plan = {i: t for i, t in plan.items() if i in by_id and t in by_id[i].starts()}
    out += [f"must_{p.project_id}" for p in pf.projects if p.must_do and p.project_id not in plan]
    for g, members in groups(pf).items():
        if sum(i in plan for i in members) > 1:
            out.append(f"alt_{g}")
    for c in pf.projects:
        if c.parent and c.project_id in plan:
            if c.parent not in plan or plan[c.parent] > plan[c.project_id] - c.parent_lag:
                out.append(f"after_{c.project_id}_{plan[c.project_id]}")
    for y in pf.years:
        if sum(by_id[i].spend(t).get(y, 0) for i, t in plan.items()) > pf.budget[y]:
            out.append(f"budget_{y}")
    return out


def plan_of(pm: PlanModel, values) -> dict[str, int]:
    """Project id -> start year, from a {variable: value} mapping."""
    return {i: t for (i, t), v in pm.x.items() if values[v] > 0.5}
