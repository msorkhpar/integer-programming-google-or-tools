"""Lesson 5.3.2: a MIP has no duals; Model.fixed() gives the LP with the integers fixed, and what it prices."""

import gurobipy as gp

from gridcap import generate
from grb import STATUS, build_selection, quiet_env

env = quiet_env()
small = generate("small")
sel = build_selection(env, small)
m = sel.model
m.Params.MIPGap = 0.0
m.optimize()
print("MIP:", STATUS[m.Status], m.ObjVal, "| IsMIP", m.IsMIP)
try:
    print(sel.budget[2027].Pi)
except (AttributeError, gp.GurobiError) as error:
    print("Pi on a MIP:", type(error).__name__, error)

f = m.fixed()                                   # a new LP: every binary fixed at its solution value
f.optimize()
print("fixed():", STATUS[f.Status], f.ObjVal, "| IsMIP", f.IsMIP, "| fixed vars",
      sum(1 for v in f.getVars() if v.LB == v.UB))
print("budget Pi in the fixed LP:", [round(f.getConstrByName(f"budget[{y}]").Pi, 4) + 0.0 for y in small.years])
for pid in ("P001", "P002"):
    v = f.getVarByName(f"x[{pid}]")
    print(f"  {v.VarName}: X {v.X + 0.0:g}  LB {v.LB + 0.0:g}  UB {v.UB + 0.0:g}  RC {v.RC:,.1f}")
