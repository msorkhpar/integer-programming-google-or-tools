"""Lesson 6.4.1's multi-period GridCap selection model, written in PuLP and solved with CBC."""

from __future__ import annotations

from dataclasses import dataclass

import pulp

from gridcap import Portfolio


@dataclass
class PulpTiming:
    prob: pulp.LpProblem
    x: dict[tuple[str, int], pulp.LpVariable]          # x[i, t] = 1: project i starts in year t


def build(portfolio: Portfolio) -> PulpTiming:
    prob = pulp.LpProblem("gridcap_timing", pulp.LpMaximize)
    x = {(p.project_id, t): prob.add_variable(f"x_{p.project_id}_{t}", 0, 1, cat=pulp.LpBinary)
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str, by: int | None = None) -> pulp.LpAffineExpression:
        return pulp.lpSum(x[pid, t] for t in by_id[pid].starts() if by is None or t <= by)

    prob += pulp.lpSum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()), "npv"

    for p in portfolio.projects:
        if p.must_do:
            prob += started(p.project_id) == 1, f"must_{p.project_id}"
        else:
            prob += started(p.project_id) <= 1, f"once_{p.project_id}"
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        prob += pulp.lpSum(started(m) for m in members) <= 1, f"alt_{g}"
    for c in portfolio.projects:
        if c.parent:
            for t in c.starts():
                prob += started(c.project_id, by=t) <= started(c.parent, by=t - c.parent_lag), \
                    f"after_{c.project_id}_{t}"

    for year in portfolio.years:
        spend = pulp.lpSum(amount * x[p.project_id, t]
                           for p in portfolio.projects for t in p.starts()
                           for y, amount in p.spend(t).items() if y == year)
        prob += spend <= portfolio.budget[year], f"budget_{year}"
    return PulpTiming(prob, x)


def cbc(**options) -> pulp.LpSolver:
    """PuLP 3.3's bundled CBC, quiet unless asked: `msg`, `timeLimit`, `gapRel`, `threads`, ..."""
    return pulp.PULP_CBC_CMD(**{"msg": False, **options})


def schedule(pt: PulpTiming) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in pt.x.items() if v.varValue > 0.5}
