"""Lesson 5.3.1: attributes of the model, its variables and its rows, read and written."""

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb import STATUS, build_selection, quiet_env

env = quiet_env()
small = generate("small")
sel = build_selection(env, small)
m, x, budget = sel.model, sel.x, sel.budget
m.Params.MIPGap = 0.0

try:
    print(x["P001"].X)                         # no solve yet: no solution to read
except AttributeError as error:
    print("before optimize:", type(error).__name__, error)

m.optimize()
print("model     :", "NumVars", m.NumVars, "| NumConstrs", m.NumConstrs, "| NumBinVars", m.NumBinVars,
      "| NumNZs", m.NumNZs)
print("solution  :", STATUS[m.Status], "| ObjVal", m.ObjVal, "| ObjBound", m.ObjBound, "| MIPGap", m.MIPGap,
      "| SolCount", m.SolCount)
print("variable  :", x["P001"].VarName, "X", x["P001"].X, "LB", x["P001"].LB, "UB", x["P001"].UB,
      "VType", x["P001"].VType, "Obj", x["P001"].Obj)
row = budget[2030]
print("row       :", row.ConstrName, "Sense", row.Sense, "RHS", row.RHS, "Slack", row.Slack)

# getAttr reads one attribute of many objects at once, in the container it is given.
print("X of a list:", [v + 0.0 for v in m.getAttr("X", [x["P001"], x["P002"], x["P003"]])])   # + 0.0: -0.0 -> 0.0
slack = m.getAttr("Slack", budget)                  # a tupledict in, a dict-like out
print("Slack by year:", {y: round(s) for y, s in slack.items()})

# Writing attributes changes the model: force P001 out, give 2030 another $1,000k, re-optimize.
x["P001"].UB = 0
budget[2030].RHS += 1000
m.optimize()
print("after edits:", STATUS[m.Status], m.ObjVal, "| P001", x["P001"].X, "| RHS 2030", budget[2030].RHS)

try:
    print(budget[2030].Pi)
except (AttributeError, gp.GurobiError) as error:
    print("a MIP row has no Pi:", type(error).__name__, error)
