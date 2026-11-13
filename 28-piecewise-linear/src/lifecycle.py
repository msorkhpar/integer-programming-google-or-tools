"""Lesson 6.6.4: lifecycle value curves for asset renewal, from GridCap's Weibull failure model.

GridCap is a fictional utility's portfolio. Each asset has a Weibull shape `weibull_beta` and scale
`weibull_eta` (years); with repairs that only restore an asset to working order, the expected number
of failures between ages a and a + h is (( a + h) / eta)^beta - (a / eta)^beta. The invented
setting: a renewal of depth d (0 = nothing, 1 = full replacement) makes the asset as old as
(1 - d) times its age, and costs d times its replacement project's capex. Its value is the expected
failure cost (`cof` per failure) it avoids over the plan's five years.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from piecewise import Curve, add_incremental, add_segments

HORIZON = 5                                     # years in the plan, 2027 to 2031
DEPTHS = (0.0, 0.25, 0.5, 0.75, 1.0)            # the curve's five breakpoints


def expected_failures(age: float, beta: float, eta: float, years: float = HORIZON) -> float:
    return ((age + years) / eta) ** beta - (age / eta) ** beta


def risk_avoided(asset, depth: float) -> float:
    """$k of expected failure cost avoided over the plan by a renewal of this depth."""
    before = expected_failures(asset.age, asset.weibull_beta, asset.weibull_eta)
    after = expected_failures((1 - depth) * asset.age, asset.weibull_beta, asset.weibull_eta)
    return asset.cof * (before - after)


def value_curve(asset, depths=DEPTHS) -> Curve:
    return Curve(tuple(depths), tuple(risk_avoided(asset, d) for d in depths))


@dataclass
class Renewal:
    model: mathopt.Model
    depth: dict[str, mathopt.LinearExpression]      # project id -> depth expression
    value: dict[str, mathopt.LinearExpression]      # project id -> value on the curve ($k)
    binaries: int


def candidates(portfolio):
    """The replacement projects and their assets."""
    return [(p, portfolio.asset(p.asset_id)) for p in portfolio.projects if p.intervention == "replace"]


def renewal_model(portfolio, fund: float, choose, depths=DEPTHS) -> Renewal:
    """Choose a renewal depth per candidate to maximize the value avoided, within the fund ($k)."""
    model = mathopt.Model(name="renewal")
    depth, value, binaries = {}, {}, 0
    for p, asset in candidates(portfolio):
        curve = value_curve(asset, depths)
        piece = choose(curve)(model, curve, p.project_id)
        depth[p.project_id], value[p.project_id] = piece.x, piece.y
        binaries += len(piece.binaries)
    model.add_linear_constraint(sum(p.capex * depth[p.project_id] for p, _ in candidates(portfolio)) <= fund,
                                name="fund")
    model.maximize(sum(value.values()))
    return Renewal(model, depth, value, binaries)


def by_shape(curve: Curve):
    """Segments where the value curve is concave (the solver pushes value up), the incremental form elsewhere."""
    return add_segments if curve.concave() else add_incremental
