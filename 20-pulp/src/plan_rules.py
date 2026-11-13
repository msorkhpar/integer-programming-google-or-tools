"""Check a multi-period schedule against lesson 6.4.1's rules from the data alone, with no solver."""

from __future__ import annotations

from gridcap import Portfolio


def broken_rules(portfolio: Portfolio, plan: dict[str, int]) -> list[str]:
    """The rules a schedule (project id -> start year) breaks; an empty list means it is allowed."""
    broken = []
    for p in portfolio.projects:
        if p.project_id in plan and plan[p.project_id] not in p.starts():
            broken.append(f"window_{p.project_id}")
        if p.must_do and p.project_id not in plan:
            broken.append(f"must_{p.project_id}")
        if p.parent and p.project_id in plan:
            if p.parent not in plan or plan[p.project_id] < plan[p.parent] + p.parent_lag:
                broken.append(f"after_{p.project_id}")
    groups: dict[str, int] = {}
    for pid in plan:
        g = portfolio.project(pid).alt_group
        if g:
            groups[g] = groups.get(g, 0) + 1
    broken += [f"alt_{g}" for g, n in groups.items() if n > 1]
    for year in portfolio.years:
        spend = sum(portfolio.project(pid).spend(t).get(year, 0) for pid, t in plan.items())
        if spend > portfolio.budget[year]:
            broken.append(f"budget_{year}")
    return broken
