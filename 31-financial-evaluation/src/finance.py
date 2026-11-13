"""The money arithmetic of module 31: discounting, escalation, annuities and start-year NPV.

Conventions, used by every program of the module:

* Cash flows are keyed by calendar year. An amount in year y is treated as paid at the start of
  that year, so it is discounted by (1 + rate) ** (y - valuation_year). This is the convention of
  `numpy_financial.npv`, whose first value is not discounted.
* Costs are positive numbers in a cost profile; in a net cash flow they enter with a minus sign.
* Money is in $k, as in GridCap.
"""

from __future__ import annotations


def discount_factor(rate: float, years: float) -> float:
    """What $1 paid `years` from the valuation date is worth on that date."""
    return (1 + rate) ** -years


def present_value(flows: dict[int, float], rate: float, valuation_year: int) -> float:
    """The value on `valuation_year` of a cash flow {calendar year: amount}."""
    return sum(amount * discount_factor(rate, year - valuation_year) for year, amount in flows.items())


def escalate(amount: float, rate: float, years: float) -> float:
    """A price quoted today, paid `years` later, when prices grow by `rate` a year."""
    return amount * (1 + rate) ** years


def real_rate(nominal: float, inflation: float) -> float:
    """The real discount rate that matches a nominal one (the exact Fisher relation)."""
    return (1 + nominal) / (1 + inflation) - 1


def annuity_factor(rate: float, years: int) -> float:
    """Present value of $1 paid at the end of each of the next `years` years."""
    if rate == 0:
        return float(years)
    return (1 - (1 + rate) ** -years) / rate


def equivalent_annual_cost(present_cost: float, rate: float, years: int) -> float:
    """The level end-of-year payment over `years` years with the same present value."""
    return present_cost / annuity_factor(rate, years)


def start_year_flows(costs: tuple[float, ...], benefits: dict[int, float], start: int) -> dict[int, float]:
    """A project's net cash flow by calendar year if it starts in `start`.

    `costs[k]` is spent in year start + k; `benefits[k]` is received in year start + k.
    """
    flows: dict[int, float] = {}
    for k, cost in enumerate(costs):
        flows[start + k] = flows.get(start + k, 0.0) - cost
    for k, benefit in benefits.items():
        flows[start + k] = flows.get(start + k, 0.0) + benefit
    return flows


def npv_by_start_year(costs: tuple[float, ...], benefits_for, starts, rate: float,
                      valuation_year: int) -> dict[int, float]:
    """{start year: NPV on `valuation_year`}, one entry per allowed start.

    `benefits_for(start)` returns that start's benefits by year offset, so a benefit that shrinks
    with delay (as GridCap's does) is one function, not a special case.
    """
    return {t: present_value(start_year_flows(costs, benefits_for(t), t), rate, valuation_year)
            for t in starts}
