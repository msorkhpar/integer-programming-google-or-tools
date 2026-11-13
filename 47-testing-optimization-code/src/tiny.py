"""Hand-made GridCap-shaped instances, small enough to check every number by eye.

A unit test of one rule needs an instance where that rule alone decides: two or three projects,
budgets set so that only the rule under test can refuse a plan. These helpers fill in every field
the test does not care about, so the instance shows only what matters.
"""

from __future__ import annotations

from gridcap import Portfolio, Project

YEARS = (2027, 2028, 2029)
ROOMY = 10_000          # a budget no tiny instance can reach, so the budget row never binds


def project(pid: str, cost: tuple[int, ...] = (100,), window: tuple[int, int] = (2027, 2027), *,
            must: bool = False, parent: str | None = None, lag: int = 0, alt: str | None = None,
            npv: int = 10) -> Project:
    """A project with only the fields a rule reads; its NPV is the same in every start year."""
    first, last = window
    return Project(project_id=pid, name=pid, program="distribution", region="Ridge", asset_id=f"A-{pid}",
                   intervention="replace", cost_profile=cost, earliest_start=first, latest_start=last,
                   must_do=must, parent=parent, parent_lag=lag, alt_group=alt, crew_months=1,
                   npv={t: npv for t in range(first, last + 1)})


def portfolio(*projects: Project, budget: dict[int, int] | None = None, years: tuple[int, ...] = YEARS,
              name: str = "tiny-test") -> Portfolio:
    """An instance with these projects; every year's budget is roomy unless `budget` says otherwise."""
    limits = {y: ROOMY for y in years} | (budget or {})
    return Portfolio(name=name, seed=0, years=years, discount_rate=0.07, projects=tuple(projects), assets=(),
                     capital_budget=sum(limits.values()), budget=limits, region_budget={}, region_floor={},
                     crews={})
