"""What a list of replacements costs and what it removes."""

from __future__ import annotations

from dataclasses import dataclass

from .fleet import Transformer, risk


@dataclass(frozen=True)
class Summary:
    units: int
    spend: int              # $k
    risk_removed: float     # $k of expected failure cost this year


def summarize(fleet: list[Transformer], chosen: list[str]) -> Summary:
    by_id = {t.tid: t for t in fleet}
    units = [by_id[tid] for tid in chosen]
    return Summary(len(units), sum(t.cost for t in units), sum(risk(t) for t in units))


def outages(fleet: list[Transformer], replace: dict[str, int]) -> set[tuple[str, int]]:
    """The (substation, year) outages the replacements need: one per substation and year."""
    substation = {t.tid: t.substation for t in fleet}
    return {(substation[tid], y) for tid, y in replace.items()}


def spend_by_year(fleet: list[Transformer], replace: dict[str, int], outage_cost: int = 0) -> dict[int, int]:
    """What the replacements cost in each year, with their outages, $k."""
    cost = {t.tid: t.cost for t in fleet}
    spend: dict[int, int] = {}
    for tid, y in replace.items():
        spend[y] = spend.get(y, 0) + cost[tid]
    for _, y in outages(fleet, replace):
        spend[y] += outage_cost
    return dict(sorted(spend.items()))
