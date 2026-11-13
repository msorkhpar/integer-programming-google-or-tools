"""Lesson 5.3.1: the timing model of lesson 6.4.1 in gurobipy, with tupledict sums and wildcards."""

from gridcap import generate
from grb import STATUS, build_plan, chosen, quiet_env

env = quiet_env()
small = generate("small")
pl = build_plan(env, small)
m, x = pl.model, pl.x
m.Params.MIPGap = 0.0

m.update()                                   # names and counts are readable after an update
print("x has", len(x), "variables, one per project and allowed start year")
print("x.select('P017', '*') =", [v.VarName for v in x.select("P017", "*")])
print("x.sum('P017', '*')    =", x.sum("P017", "*"))
print("rows:", m.NumConstrs, "| e.g.", [c.ConstrName for c in m.getConstrs()][:3], "...")

m.optimize()
plan = chosen(pl)
print("status", STATUS[m.Status], "| NPV", m.ObjVal, "| projects started", len(plan))
print("spend by year:", {y: round(e.getValue()) for y, e in pl.spend.items()})
