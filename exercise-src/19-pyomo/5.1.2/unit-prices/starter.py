from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo


@dataclass(frozen=True)
class Unit:
    low: float        # MW when on
    high: float       # MW at most
    fixed: float      # $ per hour while on
    marginal: float   # $ per MWh


def commit(units: dict[str, Unit], demand: float, integer: bool = True) -> pyo.ConcreteModel:
    m = pyo.ConcreteModel()
    m.U = pyo.Set(initialize=list(units))
    m.on = pyo.Var(m.U, domain=pyo.Binary if integer else pyo.UnitInterval)
    m.mw = pyo.Var(m.U, bounds=lambda m, u: (0, units[u].high))
    m.low = pyo.Constraint(m.U, rule=lambda m, u: m.mw[u] >= units[u].low * m.on[u])
    m.high = pyo.Constraint(m.U, rule=lambda m, u: m.mw[u] <= units[u].high * m.on[u])
    m.demand = pyo.Constraint(expr=sum(m.mw[u] for u in m.U) == demand)
    m.cost = pyo.Objective(expr=sum(units[u].fixed * m.on[u] + units[u].marginal * m.mw[u] for u in m.U))
    return m


def price(units: dict[str, Unit], demand: float) -> tuple[float, float]:
    """The cheapest hourly cost, and the price of one more MW once the commitment is fixed."""
    # TODO: solve the MILP from commit(); fix each unit's on/off at its value; relax integrality;
    #       declare a dual Suffix; re-solve; read the demand row's dual.
    return 0.0, 0.0


if __name__ == "__main__":
    fleet = {"hydro": Unit(10, 60, 100, 5), "gas": Unit(40, 120, 900, 30), "peaker": Unit(5, 50, 300, 80)}
    print(price(fleet, 150))
