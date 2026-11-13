from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Main:
    name: str
    age: float            # years, at the start of the plan
    beta: float           # Weibull shape
    eta: float            # Weibull scale, years
    households: int       # households cut off by one break
    hours: float          # hours until their water is back


def breaks(age: float, beta: float, eta: float, years: float) -> float:
    """Expected breaks of a main between ages `age` and `age + years` (repaired, not renewed)."""
    return ((age + years) / eta) ** beta - (age / eta) ** beta


def benefit(main: Main, depth: float, start: int, duration: int, first_year: int, window: int) -> dict[str, float]:
    """Breaks and household-hours without water that renewing `main` avoids within the window."""
    in_service = start + duration
    remaining = first_year + window - in_service
    if remaining <= 0:
        return {"breaks": 0.0, "household_hours": 0.0}
    old = main.age + (in_service - first_year)
    young = (1 - depth) * old
    avoided = breaks(old, main.beta, main.eta, remaining) - breaks(young, main.beta, main.eta, remaining)
    return {"breaks": avoided, "household_hours": avoided * main.households * main.hours}


if __name__ == "__main__":
    elm = Main("Elm St", 20, 2.0, 10.0, 50, 6.0)
    print(benefit(elm, 1.0, 2030, 0, 2030, 10))
