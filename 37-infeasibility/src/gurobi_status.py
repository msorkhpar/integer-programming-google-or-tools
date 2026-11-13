"""Lesson 9.1.1: Gurobi's INF_OR_UNBD, and DualReductions=0 to separate it.

The same three two-variable models as status_zoo.py, in gurobipy, run on the size-limited license
mounted in the runner. The environment prints nothing (no banner, no log), so no license or machine
detail reaches the output.
"""

import gurobipy as gp
from gurobipy import GRB

from convert import quiet_env

STATUS = {getattr(GRB.Status, n): n for n in dir(GRB.Status) if n.isupper()}   # 4 -> "INF_OR_UNBD"
env = quiet_env()


def tiny(kind: str, integer: bool) -> tuple[gp.Model, gp.Var]:
    m = gp.Model(kind, env=env)
    vtype = GRB.INTEGER if integer else GRB.CONTINUOUS
    x = m.addVar(vtype=vtype, name="x")                      # lb=0 by default in gurobipy
    y = m.addVar(vtype=vtype, name="y")
    if kind == "infeasible":
        m.addConstr(x + y <= 4, name="cap")
        m.addConstr(x + y >= 6, name="need")
    elif kind == "unbounded":
        m.addConstr(x - y <= 2, name="gap")
    else:
        m.addConstr(x - y >= 1, name="above")
        m.addConstr(x - y <= -1, name="below")
    m.setObjective(x + y, GRB.MAXIMIZE)
    return m, x


print(f"{'model':<11}{'type':<5}{'default':<13}DualReductions=0")
for kind in ("infeasible", "unbounded", "both"):
    for integer in (False, True):
        default, _ = tiny(kind, integer)
        default.optimize()
        strict, x = tiny(kind, integer)
        strict.Params.DualReductions = 0                     # presolve may not use dual arguments
        strict.optimize()
        extra = f"   objective {strict.ObjVal:g}, x = {x.X:g}" if strict.Status == GRB.OPTIMAL else ""
        print(f"{kind:<11}{'MIP' if integer else 'LP':<5}{STATUS[default.Status]:<13}{STATUS[strict.Status]}{extra}")
