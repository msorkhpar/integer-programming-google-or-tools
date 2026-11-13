"""Lesson 5.3.1: a first gurobipy model, its lazy updates, and GridCap small's selection model.

GridCap is a fictional utility's portfolio. Every solve runs in a quiet environment (`grb.quiet_env`),
so no license banner or log is printed.
"""

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb import STATUS, build_selection, quiet_env

env = quiet_env()

# Three candidate projects, one budget of $1,000k: which to fund for the most NPV?
m = gp.Model("three-projects", env=env)
feeder = m.addVar(vtype=GRB.BINARY, name="feeder")        # cost 600, NPV 420
breaker = m.addVar(vtype=GRB.BINARY, name="breaker")      # cost 300, NPV 250
trim = m.addVar(vtype=GRB.BINARY, name="trim")            # cost 250, NPV 190
m.addConstr(600 * feeder + 300 * breaker + 250 * trim <= 1000, name="budget")
m.setObjective(420 * feeder + 250 * breaker + 190 * trim, GRB.MAXIMIZE)

print("before update:", m.NumVars, "variables,", m.NumConstrs, "rows")
m.update()
print("after update: ", m.NumVars, "variables,", m.NumConstrs, "rows")

m.optimize()
print("status", m.Status, STATUS[m.Status], "| objective", m.ObjVal)
for v in m.getVars():
    print(f"  {v.VarName:8} {v.X:g}")

# GridCap small's selection model, built in grb.build_selection.
small = generate("small")
sel = build_selection(env, small)
sel.model.Params.MIPGap = 0.0                  # prove optimality exactly, as MathOpt's EXACT does
sel.model.optimize()
print("GridCap small:", STATUS[sel.model.Status], sel.model.ObjVal)
print("funded:", [i for i, v in sel.x.items() if v.X > 0.5][:8], "...")
