"""The CIPT value function: benefit measures, normalized by fixed references and swing-weighted.

    v(i, t) = sum over measures k of  w[k] * m[i, t, k] / R[k]

`m` is a project's benefit in measure k's own unit, `R[k]` the reference (the swing) in the same
unit, so `m / R` has no unit, and `w` are swing weights that sum to 1. The references and the board's
swing ratings are invented for GridCap, a fictional utility.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from benefits import Measures, measures
from gridcap import Portfolio

#: The four measures, the Measures field each one reads, and its unit.
MEASURES = {
    "reliability": ("customer_minutes", "customer-minutes"),
    "safety": ("incidents", "incidents"),
    "environmental": ("tco2e", "tCO2e"),
    "financial": ("npv", "$k"),
}
#: The swing of each measure: from no benefit (0) to this much, set by the board for the planning
#: cycle and frozen with the portfolio snapshot.
REFERENCE = {"reliability": 3_000_000, "safety": 1.0, "environmental": 200.0, "financial": 5_000}
#: The board's swing ratings: the biggest swing gets 100, the others a share of it.
SWING_RATINGS = {"reliability": 100, "safety": 80, "financial": 60, "environmental": 20}


def swing_weights(ratings: dict[str, float]) -> dict[str, float]:
    """Weights from swing ratings: each rating over their total, so the weights sum to 1."""
    total = sum(ratings.values())
    return {k: r / total for k, r in ratings.items()}


WEIGHTS = swing_weights(SWING_RATINGS)


def raw(m: Measures) -> dict[str, float]:
    """A project's benefits, each in its own unit."""
    return {k: float(getattr(m, field)) for k, (field, _) in MEASURES.items()}


def normalized(benefit: dict[str, float], reference: dict[str, float]) -> dict[str, float]:
    """Each benefit as a share of its reference swing: 0 is no benefit, 1 is the full swing."""
    return {k: benefit[k] / reference[k] for k in benefit}


def value(benefit: dict[str, float], reference: dict[str, float], weights: dict[str, float]) -> float:
    """The weighted sum of the normalized benefits, in value points."""
    score = normalized(benefit, reference)
    return sum(weights[k] * score[k] for k in weights)


def value_table(portfolio: Portfolio, reference=REFERENCE, weights=WEIGHTS) -> dict[tuple[str, int], float]:
    """v[(project, start year)] for every start each project may use."""
    return {(p.project_id, t): value(raw(measures(portfolio, p, t)), reference, weights)
            for p in portfolio.projects for t in p.starts()}


def npv_equivalent(points: float, reference=REFERENCE, weights=WEIGHTS) -> float:
    """Value points restated as the $k of NPV that would earn the same points."""
    return points * reference["financial"] / weights["financial"]


def exchange_rates(reference=REFERENCE, weights=WEIGHTS, base: str = "financial") -> dict[str, float]:
    """How many units of `base` one unit of each measure is worth: (w_k / R_k) / (w_base / R_base)."""
    per_unit = {k: weights[k] / reference[k] for k in weights}
    return {k: per_unit[k] / per_unit[base] for k in weights}


def ranking(values: dict) -> list:
    """Keys from the highest value to the lowest; ties broken by the key, so the order is stable."""
    return sorted(values, key=lambda key: (-values[key], key))


def value_expression(x: dict, v: dict) -> mathopt.LinearExpression:
    """The plan's value, sum of v[i, t] x[i, t], as one MathOpt expression."""
    return mathopt.fast_sum(v[key] * x[key] for key in x)
