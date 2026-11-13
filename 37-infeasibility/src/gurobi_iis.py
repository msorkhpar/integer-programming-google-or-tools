"""Lesson 9.1.3: gurobipy's computeIIS on the Budget Lock scenario, steered with IISConstrForce, with the
variables typed binary, and on the LP relaxation.

GridCap is a fictional utility's portfolio. The model is lock_model's, copied row for row into
gurobipy (convert.to_gurobi), 80 variables and 70 rows, well inside the size-limited license. The
environment prints nothing, so no license or machine detail reaches the output.
"""

from gurobipy import GRB

from convert import quiet_env, to_gurobi
from gridcap import generate
from lock_model import LOCK, build

small = generate("small")
env = quiet_env()


def iis(g) -> tuple[list[str], list[str], list[str]]:
    """Rows, lower bounds and upper bounds in the IIS that computeIIS just found."""
    rows = sorted(c.ConstrName for c in g.getConstrs() if c.IISConstr)
    lower = [v.VarName for v in g.getVars() if v.IISLB]
    upper = [v.VarName for v in g.getVars() if v.IISUB]
    return rows, lower, upper


g = to_gurobi(build(small, LOCK).model, env)
g.optimize()
g.computeIIS()
rows, lower, upper = iis(g)
print(f"MILP, computeIIS: minimal {bool(g.IISMinimal)}, {len(rows)} rows, {len(lower)} lower bounds, {len(upper)} upper bounds")
print("   rows:", rows)
print("   upper bounds:", upper, "| lower bounds, e.g.:", lower[:3])


def bounds_in(g) -> None:
    """Force every variable bound into the IIS, so that it chooses among rows only."""
    for v in g.getVars():
        v.IISLBForce = 1
        v.IISUBForce = 1


g = to_gurobi(build(small, LOCK).model, env)
bounds_in(g)
g.computeIIS()
print("bounds forced in:", iis(g)[0])

for name, force in (("budget_2028", 0), ("crews_transmission_2028", 1)):       # 0: keep the row out; 1: put it in
    g = to_gurobi(build(small, LOCK).model, env)
    bounds_in(g)
    g.getConstrByName(name).IISConstrForce = force
    g.computeIIS()
    print(f"bounds in, {name} {'out' if force == 0 else 'in'}: minimal {bool(g.IISMinimal)},", iis(g)[0])

binary = to_gurobi(build(small, LOCK).model, env)            # every variable here is a 0-1 integer
for v in binary.getVars():
    v.VType = GRB.BINARY                                     # the same variables, typed binary
binary.computeIIS()
rows, lower, upper = iis(binary)
print(f"typed BINARY: {len(rows)} rows, {len(lower)} lower bounds, {len(upper)} upper bounds,", rows)

relaxed = to_gurobi(build(small, LOCK).model, env).relax()  # every integer variable made continuous
relaxed.optimize()
relaxed.computeIIS()
rows, lower, upper = iis(relaxed)
print("LP relaxation, computeIIS:", rows, f"+ {len(lower)} lower bounds")
