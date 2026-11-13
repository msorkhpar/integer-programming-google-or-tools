"""What a plan spends, counted from its starts, apart from the model."""

from __future__ import annotations

from .portfolio import Project


def spend_by_year(projects: list[Project], starts: dict[str, int]) -> dict[int, int]:
    """Each year's spend, $k: the cost of every project starting that year."""
    cost = {p.pid: p.cost for p in projects}
    spend: dict[int, int] = {}
    for pid, year in starts.items():
        spend[year] = spend.get(year, 0) + cost[pid]
    return dict(sorted(spend.items()))
