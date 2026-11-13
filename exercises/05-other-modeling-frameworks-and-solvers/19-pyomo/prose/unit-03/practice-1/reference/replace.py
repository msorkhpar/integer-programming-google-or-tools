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


def plan(assets: dict[str, Asset], demand: float) -> tuple[float, dict[str, str]]:
    """The cheapest repair-or-replace plan that carries `demand`, and the choice for each asset."""
    m = build(assets, demand)
    pyo.TransformationFactory("gdp.bigm").apply_to(m)
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    solver.solve(m)
    chosen = {i: "replace" if m.choice[i].disjuncts[1].indicator_var.value else "repair" for i in m.A}
    return pyo.value(m.total), chosen


if __name__ == "__main__":
    fleet = {"T1": Asset(120, 400, 30, 60), "T2": Asset(90, 350, 25, 50)}
    print(plan(fleet, 80))
