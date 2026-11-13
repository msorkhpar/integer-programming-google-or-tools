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
