"""A one-period GridCap selection that buys missing transmission crew-months from contractors at tiered prices.

GridCap is a fictional utility's portfolio. The selection is lesson 1.1.3's one-period model (fund
each project or not, within the capital budget, must-dos funded). New here: transmission projects
need crew-months; GridCap's own crews cover OWN of them, and every month beyond that is bought from
contractors. Contractor prices rise by tier, so the contract cost is a convex piecewise-linear
function of the months bought, handed to Pyomo's `Piecewise` component.
"""

from __future__ import annotations

import pyomo.environ as pyo

from gridcap import Portfolio

MONTHS = [0, 10, 20, 40]          # breakpoints: contractor crew-months bought
COST = [0, 300, 750, 2150]        # contract cost at each breakpoint, $k: tiers of $30k, $45k, $70k a month
DISCOUNT = [0, 450, 750, 1150]    # a volume-discount offer instead: $45k, $30k, $20k a month


def build(portfolio: Portfolio, own: int, *, cost: list[float] = COST, constr_type: str = "LB",
          repn: str = "INC", force_pw: bool = False) -> pyo.ConcreteModel:
    projects = portfolio.projects
    m = pyo.ConcreteModel(name=f"{portfolio.name} contractors")
    m.P = pyo.Set(initialize=[p.project_id for p in projects])
    m.T = pyo.Set(within=m.P, initialize=[p.project_id for p in projects if p.program == "transmission"])
    m.value = pyo.Param(m.P, initialize={p.project_id: p.value for p in projects})
    m.capex = pyo.Param(m.P, initialize={p.project_id: p.capex for p in projects})
    m.months = pyo.Param(m.P, initialize={p.project_id: p.crew_months for p in projects})
    m.must = pyo.Param(m.P, within=pyo.Boolean, initialize={p.project_id: p.must_do for p in projects})

    m.x = pyo.Var(m.P, domain=pyo.Binary)
    m.bought = pyo.Var(bounds=(MONTHS[0], MONTHS[-1]))        # contractor crew-months
    m.contract = pyo.Var(bounds=(0, None))                     # what they cost, $k

    m.budget = pyo.Constraint(expr=sum(m.capex[i] * m.x[i] for i in m.P) <= portfolio.capital_budget)
    m.must_do = pyo.Constraint(m.P, rule=lambda m, i: m.x[i] == 1 if m.must[i] else pyo.Constraint.Skip)
    m.crews = pyo.Constraint(expr=sum(m.months[i] * m.x[i] for i in m.T) <= own + m.bought)
    m.tiers = pyo.Piecewise(m.contract, m.bought, pw_pts=MONTHS, f_rule=cost,
                            pw_constr_type=constr_type, pw_repn=repn, force_pw=force_pw)

    m.net = pyo.Objective(expr=sum(m.value[i] * m.x[i] for i in m.P) - m.contract, sense=pyo.maximize)
    return m


def tier_cost(months: float, cost: list[float] = COST) -> float:
    """The contract cost of `months` contractor crew-months, read off the tiers by hand."""
    for (a, fa), (b, fb) in zip(zip(MONTHS, cost), zip(MONTHS[1:], cost[1:])):
        if months <= b:
            return fa + (fb - fa) * (months - a) / (b - a)
    raise ValueError(f"{months} is beyond the last breakpoint")
