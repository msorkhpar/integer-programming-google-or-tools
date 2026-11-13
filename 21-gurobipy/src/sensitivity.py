"""Lesson 5.3.2: budget prices and their ranges on GridCap small's LP relaxation, checked by re-solving."""

from gridcap import generate
from grb import STATUS, build_selection, quiet_env

env = quiet_env()
small = generate("small")
sel = build_selection(env, small, integer=False)          # 0 <= x_i <= 1: the LP relaxation
m = sel.model
m.optimize()
base = m.ObjVal
print("LP relaxation:", STATUS[m.Status], round(base, 2))
print("row           Pi      RHS   SARHSLow  SARHSUp")
for y, row in sel.budget.items():
    print(f"{row.ConstrName:13} {row.Pi:6.4f} {row.RHS:7,.0f} {row.SARHSLow:9,.1f} {row.SARHSUp:9,.1f}")

# Check the 2030 price: move the budget inside its range, then past it, and compare.
row = sel.budget[2030]
pi, rhs, up = row.Pi, row.RHS, row.SARHSUp
for new in (rhs + 100, up, up + 300):
    row.RHS = new
    m.optimize()
    print(f"budget 2030 = {new:8,.1f}: objective {m.ObjVal:9,.2f}  gain {m.ObjVal - base:7,.2f}"
          f"  Pi x change {pi * (new - rhs):7,.2f}")
row.RHS = rhs
m.optimize()

# Objective ranging: how far a project's NPV may move before the LP's plan changes.
print("var        X  VBasis       RC     Obj  SAObjLow   SAObjUp")
for pid in ("P005", "P002", "P024", "P001"):
    v = sel.x[pid]
    print(f"{v.VarName:8} {v.X:5.3f} {v.VBasis:4} {v.RC + 0.0:10.2f} {v.Obj:7,.0f} {v.SAObjLow + 0.0:9,.1f} {v.SAObjUp:9,.1f}")

# A reduced cost is the objective coefficient less what the column's rows charge at their prices.
v = sel.x["P002"]
column = m.getCol(v)
terms = [(column.getConstr(k).ConstrName, column.getCoeff(k), column.getConstr(k).Pi) for k in range(column.size())]
print(f"{v.VarName}'s column:")
for name, a, price in terms:
    print(f"  {name:12} a {a:6,.0f}  Pi {price:8.4f}  charge {a * price:9.2f}")
print(f"  RC = {v.Obj:,.0f} - {sum(a * p for _, a, p in terms):,.2f} = {v.Obj - sum(a * p for _, a, p in terms):,.2f}"
      f"  (Gurobi's RC {v.RC:,.2f})")
