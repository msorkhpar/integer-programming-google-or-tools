"""What the planners ask for: a yearly budget, the plan's years, and the rules they turn on."""

from __future__ import annotations

from dataclasses import dataclass, field

from .portfolio import FIRST_YEAR


@dataclass(frozen=True)
class Request:
    budget: int                   # $k for each plan year
    years: int = 5                # plan years, counted from FIRST_YEAR
    max_starts: int | None = 3    # most projects that may start in one year; None: no cap
    # Stub: the next lesson gives this field its meaning; this model ignores it.
    shares: dict[str, int] = field(default_factory=dict)

    def plan_years(self) -> list[int]:
        return list(range(FIRST_YEAR, FIRST_YEAR + self.years))


def check(projects: list[Project], request: Request) -> None:
    """A new function. Raises ValueError, with a message, before any model is built, when request.shares names a region with no project in the portfolio, sets a share outside 0 to 100, or sets shares that add up to more than 100. Returns None otherwise."""
    raise NotImplementedError
