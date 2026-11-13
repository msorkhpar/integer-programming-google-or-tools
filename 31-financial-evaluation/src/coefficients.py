"""GridCap's NPV-by-start-year table, rebuilt from its cash flows with `finance.npv_by_start_year`."""

from __future__ import annotations

import math

from gridcap import Portfolio, Project

from finance import npv_by_start_year


def gridcap_benefits(project: Project, ratio: float, decay: float):
    """GridCap's benefit model: one amount in the start year, smaller by `decay` per year of delay."""
    def benefits_for(start: int) -> dict[int, float]:
        return {0: project.capex * ratio * (1 - decay) ** (start - project.earliest_start)}
    return benefits_for


def coefficient_table(portfolio: Portfolio, assumptions: dict, rate: float) -> dict[tuple[str, int], int]:
    """{(project id, start year): NPV in $k on the first plan year, rounded to a whole $k}."""
    table = {}
    for p in portfolio.projects:
        ratio, decay = assumptions[p.project_id]
        npv = npv_by_start_year(p.cost_profile, gridcap_benefits(p, ratio, decay), p.starts(), rate,
                                valuation_year=portfolio.years[0])
        for t, value in npv.items():
            table[p.project_id, t] = math.floor(value + 0.5)
    return table
