"""The asset-risk arithmetic of module 32: Weibull failure curves, remaining life, risk and its reduction.

Every function is plain `math`, so each formula on the page is one line of code. The programs of the
module check these functions against `scipy.stats.weibull_min`, which uses the same curve with
shape `c = beta` and `scale = eta`.
"""

from __future__ import annotations

import math

#: The share of its age an asset keeps after each kind of work (the convention of lesson 1.1.2).
AGE_AFTER = {"replace": 0.0, "rebuild": 0.0, "underground": 0.0, "repair": 0.5, "trim": 0.5,
             "clear": 0.5, "widen": 0.5}


def cumulative(t: float, beta: float, eta: float) -> float:
    """F(t): the probability that the asset has failed by age t."""
    return 1 - math.exp(-((t / eta) ** beta))


def survival(t: float, beta: float, eta: float) -> float:
    """R(t) = 1 - F(t): the probability that it is still working at age t."""
    return math.exp(-((t / eta) ** beta))


def density(t: float, beta: float, eta: float) -> float:
    """f(t): how densely failures are packed around age t, per year."""
    return (beta / eta) * (t / eta) ** (beta - 1) * survival(t, beta, eta)


def hazard(t: float, beta: float, eta: float) -> float:
    """h(t) = f(t) / R(t): the failure rate, per year, of the assets still working at age t."""
    return (beta / eta) * (t / eta) ** (beta - 1)


def cumulative_hazard(t: float, beta: float, eta: float) -> float:
    """Lambda(t) = (t / eta) ** beta, so that R(t) = exp(-Lambda(t))."""
    return (t / eta) ** beta


def pof_next(age: float, beta: float, eta: float) -> float:
    """The probability it fails within a year, given that it is working at `age`."""
    return 1 - survival(age + 1, beta, eta) / survival(age, beta, eta)


def failures_next(age: float, beta: float, eta: float) -> float:
    """Expected failures in the coming year if every failure is repaired without making it younger."""
    return cumulative_hazard(age + 1, beta, eta) - cumulative_hazard(age, beta, eta)


def residual_median(age: float, beta: float, eta: float) -> float:
    """Years until the chance it has failed, given that it works at `age`, reaches one half."""
    return eta * ((age / eta) ** beta + math.log(2)) ** (1 / beta) - age


def eta_from_rul(age: float, rul: float, beta: float) -> float:
    """The scale that makes `rul` the median remaining life of an asset of this age and shape."""
    return (((age + rul) ** beta - age ** beta) / math.log(2)) ** (1 / beta)


def yearly_risk(age: float, beta: float, eta: float, cof: float) -> float:
    """Expected failure cost in the coming year, $k: expected failures times the cost of one."""
    return cof * failures_next(age, beta, eta)


def ages_by_year(age_now: float, years, start: int, duration: int, keep: float) -> dict[int, float]:
    """The asset's age in each plan year if work starts in `start` and lasts `duration` years.

    Until the work is done the asset keeps aging. In the year after the work ends it is
    `keep` times the age it had reached, and it ages one year per year from there.
    """
    first, done = years[0], start + duration
    ages = {}
    for y in years:
        if y < done:
            ages[y] = age_now + (y - first)
        else:
            ages[y] = keep * (age_now + (done - first)) + (y - done)
    return ages


def yearly_reduction(asset, years, start: int, duration: int, keep: float) -> dict[int, float]:
    """Risk removed in each plan year ($k) by work that starts in `start`."""
    after = ages_by_year(asset.age, years, start, duration, keep)
    out = {}
    for y in years:
        before = yearly_risk(asset.age + (y - years[0]), asset.weibull_beta, asset.weibull_eta, asset.cof)
        out[y] = before - yearly_risk(after[y], asset.weibull_beta, asset.weibull_eta, asset.cof)
    return out


def risk_reduction(asset, years, start: int, duration: int, keep: float, rate: float = 0.0) -> float:
    """The coefficient of x[i, start]: the plan's yearly reductions, discounted to its first year."""
    cut = yearly_reduction(asset, years, start, duration, keep)
    return sum(cut[y] / (1 + rate) ** (y - years[0]) for y in years)
