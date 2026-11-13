"""Lesson 6.6.4: the renewal model again in Pyomo, with Pyomo's Piecewise component, as an independent check.

GridCap is a fictional utility's portfolio. The same five-breakpoint value curves (lifecycle.py)
are handed to `pyomo.environ.Piecewise`, which writes the formulation itself; `pw_repn` names the
formulation and `pw_constr_type="EQ"` asks for value = f(depth). HiGHS solves each one through
Pyomo's `appsi_highs` interface, and the MathOpt model of renewal_plan.py gives the reference.
"""

import pyomo.environ as pyo

from gridcap import generate
from lifecycle import DEPTHS, candidates, renewal_model, value_curve
from piecewise import add_incremental
from renewal_plan import FUND
from selection import EXACT, solve_highs


def pyomo_renewal(portfolio, fund, repn):
    cands = candidates(portfolio)
    m = pyo.ConcreteModel()
    m.P = pyo.Set(initialize=[p.project_id for p, _ in cands])
    m.depth = pyo.Var(m.P, bounds=(0, 1))
    m.value = pyo.Var(m.P)
    m.curve = pyo.Piecewise(
        m.P, m.value, m.depth,
        pw_pts={p.project_id: list(DEPTHS) for p, _ in cands},
        f_rule={p.project_id: list(value_curve(a).ys) for p, a in cands},
        pw_constr_type="EQ", pw_repn=repn)
    m.fund = pyo.Constraint(expr=sum(p.capex * m.depth[p.project_id] for p, _ in cands) <= fund)
    m.obj = pyo.Objective(expr=sum(m.value[i] for i in m.P), sense=pyo.maximize)
    return m


if __name__ == "__main__":
    small = generate("small")
    plan = renewal_model(small, FUND, lambda curve: add_incremental)
    print(f"MathOpt, incremental form : ${solve_highs(plan.model, EXACT).objective_value():,.1f}k")
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    for repn in ("INC", "CC", "LOG", "SOS2"):
        m = pyomo_renewal(small, FUND, repn)
        try:
            solver.solve(m)
            print(f"Pyomo Piecewise, {repn:4}    : ${pyo.value(m.obj):,.1f}k, "
                  f"depths {{P019: {pyo.value(m.depth['P019']):.3f}, P023: {pyo.value(m.depth['P023']):.3f}}}")
        except Exception as error:
            print(f"Pyomo Piecewise, {repn:4}    : {type(error).__name__}: {str(error).splitlines()[0]}")
