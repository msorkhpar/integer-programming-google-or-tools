"""Lesson 5.3.4: the size-limited license at its edge: 2,000 variables solve, 2,001 do not.

The output shown in the lesson comes from the course runner's size-limited license. With an
academic or commercial license every model here solves; the program prints whichever happens.
"""

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb import STATUS, build_plan, mask, quiet_env

env = quiet_env()


def try_solve(m: gp.Model) -> str:
    m.Params.TimeLimit = 60
    try:
        m.optimize()
        return STATUS[m.Status]
    except gp.GurobiError as error:
        return f"GurobiError {error.errno}: {mask(str(error))}"


for n in (2000, 2001):
    m = gp.Model(f"{n} variables", env=env)
    x = m.addVars(n, ub=1.0, name="x")
    m.setObjective(x.sum(), GRB.MAXIMIZE)
    m.update()
    print(f"{n:,} variables, {m.NumConstrs} rows -> {try_solve(m)}")

m = gp.Model("2,001 rows", env=env)
y = m.addVar(name="y")
m.addConstrs((y <= k + 1 for k in range(2001)), name="cap")
m.update()
print(f"{m.NumVars} variable, {m.NumConstrs:,} rows -> {try_solve(m)}")

for size in ("small", "medium", "large"):
    pl = build_plan(env, generate(size))
    pl.model.update()
    print(f"GridCap {size} timing model: {pl.model.NumVars:,} variables, {pl.model.NumConstrs:,} rows -> "
          f"{try_solve(pl.model)}")
