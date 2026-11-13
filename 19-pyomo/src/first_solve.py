"""Lesson 5.1.1: a first solve with HiGHS, and a scalar mutable Param changed between solves.

GridCap is a fictional utility's portfolio. A one-period selection on GridCap tiny: fund each
project (at its earliest start) or not, within one budget. The budget is a mutable Param with no
index, so one model is built once and solved at three budgets.
"""

import pyomo.environ as pyo

from gridcap import generate

tiny = generate("tiny")

m = pyo.ConcreteModel()
m.P = pyo.Set(initialize=[p.project_id for p in tiny.projects])
m.capex = pyo.Param(m.P, initialize={p.project_id: p.capex for p in tiny.projects})
m.value = pyo.Param(m.P, initialize={p.project_id: p.value for p in tiny.projects})
m.budget = pyo.Param(initialize=3000, mutable=True)      # no index set: a scalar Param, one number
m.x = pyo.Var(m.P, domain=pyo.Binary)
m.spend = pyo.Constraint(expr=sum(m.capex[i] * m.x[i] for i in m.P) <= m.budget)
m.total = pyo.Objective(expr=sum(m.value[i] * m.x[i] for i in m.P), sense=pyo.maximize)
print("spend row:", m.spend.expr)

solver = pyo.SolverFactory("appsi_highs")       # HiGHS through Pyomo's appsi interface
solver.config.mip_gap = 0.0                     # stop only at a proven optimum
for b in (3000, 5000, 8000):
    m.budget = b                                # assigning to a scalar mutable Param sets its value
    solver.solve(m)
    funded = [i for i in m.P if pyo.value(m.x[i]) > 0.5]
    print(f"budget {pyo.value(m.budget):>5}: value {pyo.value(m.total):>5}, funded {funded}")
