"""Lagrangian relaxation of the yearly budget rows: the bound for one set of prices, by enumeration."""

from __future__ import annotations

import itertools

from gridcap import Portfolio, Project

from capital import alt_groups


def components(portfolio: Portfolio) -> list[list[Project]]:
    """Groups of projects tied by a rule other than the budget: alternatives, parent and child."""
    root = {p.project_id: p.project_id for p in portfolio.projects}

    def find(a: str) -> str:
        while root[a] != a:
            a = root[a]
        return a

    for members in alt_groups(portfolio).values():
        for other in members[1:]:
            root[find(other)] = find(members[0])
    for p in portfolio.projects:
        if p.parent:
            root[find(p.project_id)] = find(p.parent)
    groups: dict[str, list[Project]] = {}
    for p in portfolio.projects:
        groups.setdefault(find(p.project_id), []).append(p)
    return list(groups.values())


def allowed(group: list[Project], choice: dict[str, int | None]) -> bool:
    """The rules left in the relaxed model: must-dos, alternatives and precedence, inside one group."""
    alts: dict[str, int] = {}
    for p in group:
        t = choice[p.project_id]
        if p.must_do and t is None:
            return False
        if t is not None and p.alt_group:
            alts[p.alt_group] = alts.get(p.alt_group, 0) + 1
        if t is not None and p.parent:
            s = choice.get(p.parent)
            if s is None or s > t - p.parent_lag:
                return False
    return all(n <= 1 for n in alts.values())


def priced(p: Project, t: int, lam: dict[int, float]) -> float:
    """npv[i,t] less the price of the money project i spends if it starts in t."""
    return p.npv[t] - sum(lam.get(y, 0.0) * c for y, c in p.spend(t).items())


def lagrangian(portfolio: Portfolio, lam: dict[int, float]) -> tuple[float, dict[str, int]]:
    """L(lam) and the plan that reaches it: each group picks its best choice on its own."""
    bound = sum(lam[y] * portfolio.budget[y] for y in portfolio.years)
    plan: dict[str, int] = {}
    for group in components(portfolio):
        options = [[None, *p.starts()] for p in group]
        best, best_choice = None, None
        for combo in itertools.product(*options):
            choice = {p.project_id: t for p, t in zip(group, combo)}
            if not allowed(group, choice):
                continue
            worth = sum(priced(p, t, lam) for p, t in zip(group, combo) if t is not None)
            if best is None or worth > best:
                best, best_choice = worth, choice
        bound += best
        plan.update({pid: t for pid, t in best_choice.items() if t is not None})
    return bound, plan


def spend_of(portfolio: Portfolio, plan: dict[str, int]) -> dict[int, int]:
    spend = {y: 0 for y in portfolio.years}
    for pid, t in plan.items():
        for y, c in portfolio.project(pid).spend(t).items():
            spend[y] += c
    return spend
