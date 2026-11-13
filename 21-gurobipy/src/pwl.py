"""Lesson 5.3.3: lesson 6.6.2's falling-tier credit line as one addGenConstrPWL row.

GridCap is a fictional utility's portfolio; the credit line is invented. Breakpoints: $k drawn and
the line's total cost, (0, 0), (1,500, 675), (3,000, 1,050), (5,000, 1,250).
"""

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb import STATUS, quiet_env

XS = [0, 1500, 3000, 5000]
YS = [0, 675, 1050, 1250]

env = quiet_env()
small = generate("small")
m = gp.Model("small-credit", env=env)
x = m.addVars(small.project_ids, vtype=GRB.BINARY, name="x")
draw = m.addVar(lb=0, ub=XS[-1], name="draw")               # $k drawn from the credit line
cost = m.addVar(lb=0, name="cost")                          # what the draw costs, $k
m.addGenConstrPWL(draw, cost, XS, YS, name="credit")        # cost = f(draw), f through the breakpoints
m.addConstr(gp.quicksum(p.capex * x[p.project_id] for p in small.projects) <= small.capital_budget + draw,
            name="budget")
groups: dict[str, list[str]] = {}
for p in small.projects:
    if p.must_do:
        m.addConstr(x[p.project_id] == 1, name=f"must_{p.project_id}")
    if p.parent:
        m.addConstr(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
    if p.alt_group:
        groups.setdefault(p.alt_group, []).append(p.project_id)
for g, members in groups.items():
    m.addConstr(gp.quicksum(x[i] for i in members) <= 1, name=f"alt_{g}")
m.setObjective(gp.quicksum(p.value * x[p.project_id] for p in small.projects) - cost, GRB.MAXIMIZE)
m.Params.MIPGap = 0.0
m.optimize()
print(f"{STATUS[m.Status]}: objective ${m.ObjVal:,.0f}k, drawn ${draw.X:,.0f}k, cost ${cost.X:,.0f}k")
print("general constraints:", m.NumGenConstrs, "| variables:", m.NumVars, "| binaries:", m.NumBinVars)

# Outside the breakpoints Gurobi extends the first and last pieces; the variable's bounds keep draw inside.
probe = gp.Model("probe", env=env)
u = probe.addVar(lb=-1000, ub=7000, name="u")
v = probe.addVar(lb=-GRB.INFINITY, name="v")
probe.addGenConstrPWL(u, v, XS, YS)
for at in (-1000, 6000):
    u.LB = u.UB = at
    probe.optimize()
    print(f"f({at:,}) = {v.X:,.0f}")
