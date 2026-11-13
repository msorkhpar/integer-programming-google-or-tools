"""What the planner asks for, and what the model answers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .fleet import FIRST_YEAR


@dataclass(frozen=True)
class Request:
    budget: int                 # $k per year
    years: int = 1              # the plan's length, from FIRST_YEAR
    window: int | None = None   # years over which removed risk is counted; None: the plan's years
    rate: float = 0.07          # discount rate for risk removed in later years
    min_age: int = 0            # units younger than this, in FIRST_YEAR, are not candidates
    gap: float = 0.0            # stop when the plan is within this share of the bound
    outage_cost: int = 0        # $k for each substation taken out of service in a year
    outages: int | None = None  # most substation outages per region per year; None: no limit
    crew_weeks: int | None = None   # crew-weeks per region per year; None: no limit
    lead_times: bool = False        # a unit needed before its kind's lead time must come from spares
    spares: dict[str, int] = field(default_factory=dict)    # spare units in stock, by kind

    def scaled(self, factor: int) -> Request:
        """Stub: the next lesson grows every limit with the fleet. Until then, the request unchanged."""
        return self

    def has_outages(self) -> bool:
        return self.outage_cost > 0 or self.outages is not None

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
