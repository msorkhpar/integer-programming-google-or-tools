# Adapted from the OR-Tools example advanced_linear_programming.py,
# https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py
"""Lesson 5.3.2: the LP of lesson 4.2.2 in gurobipy, read through its dual and basis attributes."""

import gurobipy as gp
from gurobipy import GRB

from grb import STATUS, quiet_env

env = quiet_env()
m = gp.Model("advanced_linear_programming", env=env)
x = m.addVars(3, lb=0.0, name="x")
c1 = m.addConstr(10 * x[0] + 4 * x[1] + 5 * x[2] <= 600, name="c1")
c2 = m.addConstr(2 * x[0] + 2 * x[1] + 6 * x[2] <= 300, name="c2")
c3 = m.addConstr(x.sum() <= 100, name="c3")
m.setObjective(10 * x[0] + 6 * x[1] + 4 * x[2], GRB.MAXIMIZE)
m.optimize()

rows, cols = [c1, c2, c3], [x[0], x[1], x[2]]
print("status     :", STATUS[m.Status], "| objective", round(m.ObjVal, 4))
print("X          :", [round(v, 4) for v in m.getAttr("X", cols)])
print("Pi         :", [round(p, 4) + 0.0 for p in m.getAttr("Pi", rows)])
print("Slack      :", [round(s, 4) + 0.0 for s in m.getAttr("Slack", rows)])
print("RC         :", [round(r, 4) + 0.0 for r in m.getAttr("RC", cols)])
print("CBasis     :", m.getAttr("CBasis", rows), "(0 basic, -1 nonbasic)")
print("VBasis     :", m.getAttr("VBasis", cols), "(0 basic, -1 at lower bound, -2 at upper bound)")

# The same LP as a minimization of the negated objective: same plan, every Pi and RC changes sign.
m.setObjective(-(10 * x[0] + 6 * x[1] + 4 * x[2]), GRB.MINIMIZE)
m.optimize()
print("minimize -f:", round(m.ObjVal, 4), "| Pi", [round(p, 4) + 0.0 for p in m.getAttr("Pi", rows)],
      "| RC", [round(r, 4) + 0.0 for r in m.getAttr("RC", cols)])
