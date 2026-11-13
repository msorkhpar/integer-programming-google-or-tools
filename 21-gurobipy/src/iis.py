"""Lesson 5.3.3: lesson 4.3.5's infeasible scenario in gurobipy, explained by computeIIS."""

import os
import tempfile

from gridcap import generate
from grb import STATUS, build_plan, quiet_env

env = quiet_env()
small = generate("small")
pl = build_plan(env, small)
m = pl.model

# The scenario: the board promises P032 for 2027, and finance caps 2030 and 2031 at 5,000 each.
pl.x["P032", 2027].LB = 1
pl.budget[2030].RHS = 5000
pl.budget[2031].RHS = 5000
m.optimize()
print("solve:", m.Status, STATUS[m.Status])

m.computeIIS()
print("IISMinimal:", m.IISMinimal)
rows = [c for c in m.getConstrs() if c.IISConstr]
bounds = [(v.VarName, side) for v in m.getVars() for side, on in (("lower", v.IISLB), ("upper", v.IISUB)) if on]
print(f"IIS: {len(rows)} rows, {len(bounds)} variable bounds")
for c in rows:
    print(f"   {c.ConstrName}: {c.Sense} {c.RHS:,.0f}")
print("P032's promise (LB of x[P032,2027]) in the IIS:", bool(pl.x["P032", 2027].IISLB))

# write() with the .ilp extension writes only the IIS, in LP format.
with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "conflict.ilp")
    m.write(path)
    with open(path) as handle:
        text = handle.read()
for line in text.splitlines():                     # the row lines, cut short; the long sums are elided
    if line and not line.startswith(("   +", " x[")):
        print(line if len(line) <= 72 else line[:72] + " ...")
