"""Lesson 5.3.3: feasRelaxS and feasRelax on lesson 4.3.5's infeasible scenario, each on a fresh copy.

feasRelax changes the model it is called on, so every case below rebuilds the scenario and relaxes
a copy of it: no relaxation is stacked on another.
"""

from gridcap import generate
from grb import STATUS, build_plan, quiet_env

env = quiet_env()
small = generate("small")


def scenario():
    pl = build_plan(env, small)
    pl.x["P032", 2027].LB = 1
    pl.budget[2030].RHS = 5000
    pl.budget[2031].RHS = 5000
    pl.model.update()
    return pl


def changes(model) -> list[str]:
    """The artificial variables feasRelax added that took a value: what had to give, and by how much."""
    return [f"{v.VarName} = {v.X:,.0f}" for v in model.getVars() if v.VarName.startswith("Art") and v.X > 1e-6]


# 1. Every row may be violated, each unit of violation costs 1.
pl = scenario()
relaxed = pl.model.copy()                       # feasRelax changes the model it is called on
relaxed.feasRelaxS(0, False, False, True)       # relaxobjtype 0: sum of violations; rows only
relaxed.optimize()
print("all rows, unit penalty :", STATUS[relaxed.Status], "| violation", relaxed.ObjVal, "|", changes(relaxed))

# 2. Only the budget rows may give, at 1 per $k: the board's promise and the must-do rule hold.
pl = scenario()
relaxed = pl.model.copy()
budgets = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
relaxed.feasRelax(0, False, None, None, None, budgets, [1.0] * len(budgets))
relaxed.optimize()
print("budget rows only       :", STATUS[relaxed.Status], "| violation", relaxed.ObjVal, "|", changes(relaxed))
row = relaxed.getRow(relaxed.getConstrByName("budget_2030"))
print("budget_2030 now has    :", [(row.getVar(k).VarName, row.getCoeff(k)) for k in range(row.size())
                                   if row.getVar(k).VarName.startswith("Art")])

# 3. Same, but count the rows that give (relaxobjtype 2), not the dollars.
pl = scenario()
relaxed = pl.model.copy()
budgets = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
relaxed.feasRelax(2, False, None, None, None, budgets, [1.0] * len(budgets))
relaxed.optimize()
print("budget rows, count     :", STATUS[relaxed.Status], "| rows relaxed", relaxed.ObjVal, "|", changes(relaxed))

# 4. minrelax=True: among the cheapest repairs, the plan with the best NPV.
pl = scenario()
relaxed = pl.model.copy()
budgets = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
relaxed.Params.MIPGap = 0.0
phase1 = relaxed.feasRelax(0, True, None, None, None, budgets, [1.0] * len(budgets))
relaxed.optimize()
print("minrelax=True          : least violation", phase1, "| NPV", relaxed.ObjVal, "|", changes(relaxed))
print("rows feasRelax added   :", [c.ConstrName for c in relaxed.getConstrs() if c.ConstrName.startswith(("feas", "CArt"))])
