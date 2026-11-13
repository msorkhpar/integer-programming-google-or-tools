from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo
from pyomo.gdp import Disjunction


@dataclass(frozen=True)
class Asset:
    repair: float       # cost of a repair, $k
    replace: float      # cost of a replacement, $k
    repaired: float     # MVA it can carry after a repair
    new: float          # MVA it can carry once replaced


def build(assets: dict[str, Asset], demand: float) -> pyo.ConcreteModel:
    m = pyo.ConcreteModel()
    m.A = pyo.Set(initialize=list(assets))
    m.cost = pyo.Var(m.A, bounds=lambda m, i: (0, max(assets[i].repair, assets[i].replace)))
    m.rating = pyo.Var(m.A, bounds=lambda m, i: (0, max(assets[i].repaired, assets[i].new)))

    def choice(m, i):
        a = assets[i]
        return [[m.cost[i] >= a.repair, m.rating[i] <= a.repaired],      # disjunct 0: repair
                [m.cost[i] >= a.replace, m.rating[i] <= a.new]]          # disjunct 1: replace
    m.choice = Disjunction(m.A, rule=choice)
    m.carry = pyo.Constraint(expr=sum(m.rating[i] for i in m.A) >= demand)
    m.total = pyo.Objective(expr=sum(m.cost[i] for i in m.A))
    return m


def lp_bound(assets: dict[str, Asset], demand: float, form: str) -> float:
    """The LP relaxation's optimum after `form` ("gdp.bigm" or "gdp.hull") writes the disjunctions."""
    m = build(assets, demand)
    pyo.TransformationFactory(form).apply_to(m)
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(m)
    pyo.SolverFactory("appsi_highs").solve(m)
    return pyo.value(m.total)


def lp_bounds(assets: dict[str, Asset], demand: float) -> tuple[float, float]:
    """The big-M and the hull LP bounds of the same repair-or-replace model."""
    return lp_bound(assets, demand, "gdp.bigm"), lp_bound(assets, demand, "gdp.hull")


if __name__ == "__main__":
    fleet = {"T1": Asset(120, 400, 30, 60), "T2": Asset(90, 350, 25, 50)}
    print(lp_bounds(fleet, 80))
