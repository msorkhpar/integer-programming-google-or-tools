"""What a plan spends, counted from its starts, apart from the model."""

from __future__ import annotations

from .portfolio import Project
from .request import Request


def spend_by_year(projects: list[Project], starts: dict[str, int]) -> dict[int, int]:
    """Each year's spend, $k: the cost of every project starting that year."""
    cost = {p.pid: p.cost for p in projects}
    spend: dict[int, int] = {}
    for pid, year in starts.items():
        spend[year] = spend.get(year, 0) + cost[pid]
    return dict(sorted(spend.items()))


def share_by_year(projects: list[Project], starts: dict[str, int], region: str) -> dict[int, float]:
    """The region's percent of each year's spend, for the years the plan spends anything."""
    region_of = {p.pid: p.region for p in projects}
    total = spend_by_year(projects, starts)
    mine = spend_by_year(projects, {pid: y for pid, y in starts.items() if region_of[pid] == region})
    return {year: 100 * mine.get(year, 0) / spend for year, spend in total.items()}


def overrides(request: Request) -> list[str]:
    """Each must-do override with its recorded reason, by project id."""
    return [f"{pid}: {reason.strip()}" for pid, reason in sorted(request.must_do.items())]
