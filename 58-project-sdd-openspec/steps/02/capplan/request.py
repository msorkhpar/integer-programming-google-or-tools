"""What the planners ask for: a yearly budget, the plan's years, and the rules they turn on."""

from __future__ import annotations

from dataclasses import dataclass, field

from .portfolio import FIRST_YEAR, Project


@dataclass(frozen=True)
class Request:
    budget: int                   # $k for each plan year
    years: int = 5                # plan years, counted from FIRST_YEAR
    max_starts: int | None = 3    # most projects that may start in one year; None: no cap
    shares: dict[str, int] = field(default_factory=dict)    # region -> least % of each year's spend
    # Stub: the next lesson gives this field its meaning; this model ignores it.
    must_do: dict[str, str] = field(default_factory=dict)

    def plan_years(self) -> list[int]:
        return list(range(FIRST_YEAR, FIRST_YEAR + self.years))


def check(projects: list[Project], request: Request) -> None:
    """Refuse, before any model is built, a request that no plan could keep."""
    regions = {p.region for p in projects}
    for region, pct in request.shares.items():
        if region not in regions:
            raise ValueError(f"a share for {region!r}, which has no project in the portfolio")
        if not 0 <= pct <= 100:
            raise ValueError(f"the share of {region} is {pct}%, outside 0 to 100")
    if sum(request.shares.values()) > 100:
        raise ValueError(f"the shares add up to {sum(request.shares.values())}%, more than 100")
