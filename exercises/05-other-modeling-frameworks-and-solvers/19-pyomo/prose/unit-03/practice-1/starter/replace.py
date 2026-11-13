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
    # TODO: the asset set; cost and rating variables with their bounds; one Disjunction per asset
    #       (repair or replace); the carry row; the objective, named m.total.
    return m


def plan(assets: dict[str, Asset], demand: float) -> tuple[float, dict[str, str]]:
    """The cheapest repair-or-replace plan that carries `demand`, and the choice for each asset."""
    # TODO: transform with gdp.bigm, solve with appsi_highs, read each asset's choice from indicator_var.
    return 0.0, {}


if __name__ == "__main__":
    fleet = {"T1": Asset(120, 400, 30, 60), "T2": Asset(90, 350, 25, 50)}
    print(plan(fleet, 80))
