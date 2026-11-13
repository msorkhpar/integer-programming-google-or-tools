from __future__ import annotations

import math


def yearly_pof(age: float, beta: float, eta: float) -> float:
    """The probability that an asset working at this age fails within the next year (Weibull shape beta, scale eta)."""
    # TODO: next year's probability of failure, for an asset still working at this age.
    return 0.0


def start_year_npv(flows: list[float], start: int, base_year: int, escalation: float, rate: float,
                   valuation_year: int) -> float:
    """NPV of a project started in `start`, valued at `valuation_year`.

    flows[k] is the amount of the project's k-th year (negative for costs), quoted in `base_year`
    prices; it is paid in calendar year start + k, escalated from the base year and discounted to
    the valuation year. Every flow counts, however far past the plan's end it lands.
    """
    # TODO: escalate and discount every flow, then add them up.
    return 0.0


if __name__ == "__main__":
    print(round(yearly_pof(40, 3.5, 45), 3), round(start_year_npv([-100, 50, 50, 50], 2027, 2027, 0.0, 0.1, 2027), 3))
