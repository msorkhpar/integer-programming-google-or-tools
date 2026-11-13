"""CIPT Lite, milestone 3: the coefficient tables. NPV by start year, risk reduction, weighted value.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

* `npv_table` rebuilds each start year's NPV from the project's cash flow (lesson 7.2.4): costs from
  the cost profile, the benefit forecast shrinking with delay, every amount discounted to the plan's
  first year.
* `risk_table` turns each asset's predicted RUL into a point on its Weibull curve (lesson 7.3.2),
  and counts the risk an intervention removes over a fixed ten-year window, discounted (lesson
  7.3.4).
* `value_table` normalizes both by fixed references and weights them from swing ratings (lessons
  7.4.2-7.4.4). Every table is keyed (project id, start year), one entry per start variable.
"""

from __future__ import annotations

import math

import gridcap.generator as generator
from gridcap import DEFAULT_SEED, Portfolio

WINDOW = 10                 # years of risk counted, from the plan's first year (lesson 7.3.4)
#: The share of its age an asset keeps after each kind of work (lesson 1.1.2's convention).
AGE_AFTER = {"replace": 0.0, "rebuild": 0.0, "underground": 0.0, "repair": 0.5, "trim": 0.5,
             "clear": 0.5, "widen": 0.5}
#: Fixed references (the swing from no benefit to this much), set before any project is scored.
REFERENCE = {"npv": 5_000.0, "risk": 2_000.0}
#: The board's swing ratings: risk removed is the bigger swing.
RATINGS = {"risk": 100, "npv": 60}


# --- NPV by start year --------------------------------------------------------------------------

def benefit_forecast(size: str, seed: int = DEFAULT_SEED) -> tuple[Portfolio, dict[str, tuple[float, float]]]:
    """(portfolio, {project id: (benefit ratio, decay per year of delay)}).

    GridCap's generator draws these two numbers per project and keeps only the NPVs they give. A
    finance team hands them over as a benefit forecast; here the generator is replayed and each
    draw recorded, as lesson 7.2.4 does. The portfolio is unchanged.
    """
    found: dict[str, tuple[float, float]] = {}
    original = generator._with_npv

    def recording(draw, project, years):
        units: list[float] = []

        class Recorder:
            def unit(self) -> float:
                units.append(draw.unit())
                return units[-1]

        out = original(Recorder(), project, years)
        found[project.project_id] = (1.15 + 0.9 * units[0], 0.03 + 0.05 * units[1])
        return out

    generator._with_npv = recording
    try:
        portfolio = generator.generate(size, seed)
    finally:
        generator._with_npv = original
    return portfolio, found


def npv(costs: tuple[int, ...], benefit: float, start: int, rate: float, first_year: int) -> float:
    """NPV on `first_year` of a project started in `start`: one benefit in the start year, costs
    spread over its years of work, each amount discounted from its own calendar year."""
    value = benefit * (1 + rate) ** -(start - first_year)
    for k, cost in enumerate(costs):
        value -= cost * (1 + rate) ** -(start + k - first_year)
    return value


def npv_table(pf: Portfolio, forecast: dict[str, tuple[float, float]]) -> dict[tuple[str, int], int]:
    table = {}
    for p in pf.projects:
        ratio, decay = forecast[p.project_id]
        for t in p.starts():
            benefit = p.capex * ratio * (1 - decay) ** (t - p.earliest_start)
            table[p.project_id, t] = math.floor(npv(p.cost_profile, benefit, t, pf.discount_rate, pf.years[0]) + 0.5)
    return table


# --- Risk reduction from PoF and RUL -------------------------------------------------------------

def eta_from_rul(age: float, rul: float, beta: float) -> float:
    """The scale that makes `rul` the median remaining life at this age and shape (lesson 7.3.2)."""
    return (((age + rul) ** beta - age ** beta) / math.log(2)) ** (1 / beta)


def yearly_risk(age: float, beta: float, eta: float, cof: float) -> float:
    """Expected failure cost in the coming year, $k: CoF times the expected failures (lesson 7.3.3)."""
    return cof * (((age + 1) / eta) ** beta - (age / eta) ** beta)


def risk_reduction(age: float, beta: float, eta: float, cof: float, start: int, duration: int, keep: float,
                   first_year: int, rate: float) -> float:
    """Discounted risk removed over the window by work that starts in `start` (lesson 7.3.4).

    The asset ages until the work ends; from the year after, it is `keep` times the age it had
    reached, and ages again.
    """
    done, total = start + duration, 0.0
    for y in range(first_year, first_year + WINDOW):
        before = age + (y - first_year)
        after = before if y < done else keep * (age + (done - first_year)) + (y - done)
        total += (yearly_risk(before, beta, eta, cof) - yearly_risk(after, beta, eta, cof)) \
            / (1 + rate) ** (y - first_year)
    return total


def risk_table(pf: Portfolio, anchor_rul: bool = True) -> dict[tuple[str, int], float]:
    """rr[i, s] in $k. With `anchor_rul`, each asset's scale is set so that its RUL is the median."""
    table = {}
    for p in pf.projects:
        a = pf.asset(p.asset_id)
        eta = eta_from_rul(a.age, a.rul, a.weibull_beta) if anchor_rul else a.weibull_eta
        for s in p.starts():
            table[p.project_id, s] = risk_reduction(a.age, a.weibull_beta, eta, a.cof, s, p.duration,
                                                    AGE_AFTER[p.intervention], pf.years[0], pf.discount_rate)
    return table


# --- Weighted value -------------------------------------------------------------------------------

def weights(ratings: dict[str, float] = RATINGS) -> dict[str, float]:
    total = sum(ratings.values())
    return {k: r / total for k, r in ratings.items()}


def value_table(npv_of: dict, rr_of: dict, reference: dict = REFERENCE,
                ratings: dict = RATINGS) -> dict[tuple[str, int], float]:
    """v[i, t] = w_npv * npv / R_npv + w_risk * rr / R_risk, in value points."""
    w = weights(ratings)
    return {key: w["npv"] * npv_of[key] / reference["npv"] + w["risk"] * rr_of[key] / reference["risk"]
            for key in npv_of}
