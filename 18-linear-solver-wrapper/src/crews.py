"""Lesson 4.7.4: GridCap's eight crews and what each would cost to lead each tiny project.

Two crews are based in each region: a line crew, qualified for every program, and a field crew,
not qualified for transmission. A crew working away from its region adds travel. The crews,
rates and travel costs are invented for this lesson; GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

from gridcap import REGIONS, Portfolio

CREWS = [f"{region} {kind}" for region in REGIONS for kind in ("line", "field")]
RATE = {"line": 24, "field": 18}                          # $k per crew-month
#: $k of travel and set-up for a crew from region a working in region b
TRAVEL = {("Ridge", "Valley"): 6, ("Ridge", "Coast"): 14, ("Ridge", "Plains"): 10,
          ("Valley", "Coast"): 8, ("Valley", "Plains"): 9, ("Coast", "Plains"): 12}


def travel(a: str, b: str) -> int:
    return 0 if a == b else TRAVEL.get((a, b), TRAVEL.get((b, a)))


def cost(crew: str, project) -> int | None:
    """$k for `crew` to lead `project`, or None if the crew may not."""
    region, kind = crew.split()
    if kind == "field" and project.program == "transmission":
        return None
    return RATE[kind] * project.crew_months + travel(region, project.region)


def cost_table(portfolio: Portfolio) -> dict[tuple[str, str], int]:
    """{(crew, project id): $k} over the allowed pairs only."""
    return {(c, p.project_id): cost(c, p) for c in CREWS for p in portfolio.projects if cost(c, p) is not None}
