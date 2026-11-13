"""NPV within 1%, then risk removed, then the least spend, with gurobipy's setObjectiveN."""

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from gurobi_model import build, chosen, mask, quiet_env

small = generate("small")
try:
    env = quiet_env()
except gp.GurobiError as error:              # no license mounted: say so, without user or host names
    raise SystemExit(mask(str(error)))

gm = build(env, small)
m = gm.model
m.ModelSense = GRB.MAXIMIZE                                     # one sense for every objective
m.setObjectiveN(gm.objective["npv"], index=0, priority=2, weight=1, reltol=0.01, name="npv")
m.setObjectiveN(gm.objective["risk"], index=1, priority=1, weight=1, name="risk")
m.setObjectiveN(gm.objective["spend"], index=2, priority=0, weight=-1, name="spend")  # -1: minimize
m.Params.MIPGap = 0.0
m.optimize()

print(f"status {m.Status} (2 is OPTIMAL), objectives {m.NumObj}")
for k in range(m.NumObj):
    m.Params.ObjNumber = k                       # which objective the ObjN* attributes read
    print(f"  {m.ObjNName:6} priority {m.ObjNPriority}  weight {m.ObjNWeight:+.0f}  reltol {m.ObjNRelTol:g}"
          f"  abstol {m.ObjNAbsTol:g}  value {m.ObjNVal:,.1f}")
print(f"projects {len(chosen(gm))}")

for reltol in (0.0, 0.01, 0.20):                  # the same objectives on the LP relaxation
    lp = build(env, small)
    lp.model.update()                               # the variables exist before their type changes
    for var in lp.model.getVars():
        var.VType = GRB.CONTINUOUS                  # 0 <= x <= 1, no longer binary
    lp.model.ModelSense = GRB.MAXIMIZE
    lp.model.setObjectiveN(lp.objective["npv"], index=0, priority=2, weight=1, reltol=reltol, name="npv")
    lp.model.setObjectiveN(lp.objective["risk"], index=1, priority=1, weight=1, name="risk")
    lp.model.optimize()
    values = []
    for k in range(2):
        lp.model.Params.ObjNumber = k
        values.append(lp.model.ObjNVal)
    print(f"LP relaxation, npv reltol {reltol:4}: npv {values[0]:,.1f}  risk {values[1]:,.1f}")

copied = build(env, small)                     # MathOpt's numbers copied unchanged: 0, 1, 2
copied.model.ModelSense = GRB.MAXIMIZE
copied.model.setObjectiveN(copied.objective["npv"], index=0, priority=0, weight=1, reltol=0.01, name="npv")
copied.model.setObjectiveN(copied.objective["risk"], index=1, priority=1, weight=1, name="risk")
copied.model.setObjectiveN(copied.objective["spend"], index=2, priority=2, weight=-1, name="spend")
copied.model.Params.MIPGap = 0.0
copied.model.optimize()
values = []
for k in range(3):
    copied.model.Params.ObjNumber = k
    values.append(copied.model.ObjNVal)
print(f"priorities copied from MathOpt: npv {values[0]:,.0f}  risk {values[1]:,.1f}  spend {values[2]:,.0f}"
      f"  projects {len(chosen(copied))}")
