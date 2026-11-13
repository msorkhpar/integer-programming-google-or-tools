"""GridCap's capital projects: one record per project, and a seeded generator.

GridCap is the course's fictional utility. Every portfolio here is drawn by `generate` from a seed,
and no number in it is a real utility's.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

REGIONS = ("north", "plains", "coast")
FIRST_YEAR = 2027


@dataclass(frozen=True)
class Project:
    pid: str
    region: str
    cost: int        # $k, paid in the year the project starts
    value: int       # $k, what the project is worth to GridCap
    earliest: int    # the first year it may start
    latest: int      # the last year it may start


def generate(n: int, seed: int = 58, years: int = 5) -> list[Project]:
    """n invented projects. Plains projects are worth less per $k, as the planners say they are."""
    rng = random.Random(seed)
    projects = []
    for k in range(n):
        region = REGIONS[rng.randrange(len(REGIONS))]
        cost = rng.randrange(100, 900, 10)
        ratio = rng.uniform(0.6, 1.5) if region == "plains" else rng.uniform(0.9, 2.4)
        earliest = FIRST_YEAR + rng.randrange(years)
        latest = min(FIRST_YEAR + years - 1, earliest + rng.randrange(3))
        projects.append(Project(f"P{k + 1:03d}", region, cost, round(cost * ratio), earliest, latest))
    return projects
