"""Lesson 5.3.3: NPV first, then the least spend, with setObjectiveN (lesson 4.3.2's question in gurobipy)."""

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb import STATUS, build_plan, chosen, quiet_env

env = quiet_env()
small = generate("small")


def scenario(npv_priority: int, spend_priority: int, npv_reltol: float):
    pl = build_plan(env, small)
    m = pl.model
    m.ModelSense = GRB.MAXIMIZE                          # one sense for every objective
    total_spend = gp.quicksum(pl.spend.values())
    m.setObjectiveN(pl.npv, index=0, priority=npv_priority, weight=1.0, reltol=npv_reltol, name="npv")
    m.setObjectiveN(total_spend, index=1, priority=spend_priority, weight=-1.0, name="spend")  # -1: minimize
    m.Params.MIPGap = 0.0
    m.optimize()
    values = []
    for k in range(m.NumObj):
        m.Params.ObjNumber = k                           # which objective ObjNVal reads
        values.append(m.ObjNVal)
    return STATUS[m.Status], values, len(chosen(pl))


for label, args in [("NPV, then spend, exact      ", (2, 1, 0.0)),
                    ("NPV within 1%, then spend   ", (2, 1, 0.01)),
                    ("spend first, then NPV       ", (1, 2, 0.0))]:
    status, (npv, spent), started = scenario(*args)
    print(f"{label} {status}  NPV {npv:9,.0f}  spend {spent:9,.0f}  projects {started}")
