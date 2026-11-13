"""What the planner asks for, and what the model answers."""

from __future__ import annotations

from dataclasses import dataclass

from .fleet import FIRST_YEAR


@dataclass(frozen=True)
class Request:
    budget: int                 # $k per year
    years: int = 1              # the plan's length, from FIRST_YEAR
    window: int | None = None   # years over which removed risk is counted; None: the plan's years
    rate: float = 0.07          # discount rate for risk removed in later years
    min_age: int = 0            # units younger than this, in FIRST_YEAR, are not candidates
    gap: float = 0.0            # stop when the plan is within this share of the bound
    # Stubs: the next lesson gives these fields their meaning; this model ignores them.
    outage_cost: int = 0
    outages: int | None = None

    def plan_years(self) -> range:
        return range(FIRST_YEAR, FIRST_YEAR + self.years)

    def risk_years(self) -> range:
        return range(FIRST_YEAR, FIRST_YEAR + (self.window or self.years))


@dataclass(frozen=True)
class Plan:
    replace: dict[str, int]     # transformer id -> year of replacement
    value: float                # risk removed, $k: the objective
    bound: float                # no plan is worth more than this
    status: str                 # the solver's termination reason
