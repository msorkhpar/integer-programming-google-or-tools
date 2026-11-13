"""Lesson 9.1.4: elastic repairs of the Budget Lock scenario, with two penalty policies, and gurobipy's feasRelax.

GridCap is a fictional utility's portfolio. The soft rows are the ones planners and finance set
(budgets, crews, floors, overrides) and the must-do rows; "once", alternatives and precedence stay
hard, because bending them gives a plan that means nothing (half a project, two alternatives).
"""

from convert import quiet_env, to_gurobi
from elastic import best_repair, elastic, fewest_rules, min_violation
from gridcap import generate
from lock_model import LOCK, build

small = generate("small")
lm = build(small, LOCK)
soft = [n for n in lm.rules if n.startswith(("budget_", "crews_", "floor_", "force_", "must_"))]
print(f"{len(soft)} soft rows of {len(lm.rules)}")

flat = {n: 1.0 for n in soft}                                  # every unit of every row costs 1
el = elastic(lm.model, flat)
result = min_violation(el)
print(f"every unit costs 1   : violation {result.objective_value():g}, bends {el.bends(result)}")

POLICY = {"budget_": 1.0, "floor_": 1.0, "crews_": 50.0, "force_": 10_000.0, "must_": 10_000.0}


def policy(name: str) -> float:
    """$k per unit of violation: a $k is $k, a crew-month is priced at $50k, overrides and must-dos almost never bend."""
    return next(w for prefix, w in POLICY.items() if name.startswith(prefix))


priced = {n: policy(n) for n in soft}
el = elastic(lm.model, priced)
result = min_violation(el)
least = result.objective_value()
print(f"priced in $k         : violation {least:g}, bends {el.bends(result)}")
repaired = best_repair(el, least)
print(f"best NPV among those repairs: ${repaired.objective_value():,.0f}k, bends {el.bends(repaired)}")
values = repaired.variable_values()
crew_2030 = {pid: small.project(pid).crew_months for (pid, t), v in lm.x.items()
             if values[el.model.get_variable(v.id)] > 0.5 and small.project(pid).program == "distribution"
             and t <= 2030 < t + small.project(pid).duration}
print(f"distribution crew-months used in 2030: {crew_2030}, available {small.crews['distribution', 2030]}")

BIG = {"budget_": 50_000, "floor_": 50_000, "crews_": 100, "force_": 1, "must_": 1}
el = elastic(lm.model, flat)
result = fewest_rules(el, {n: next(b for p, b in BIG.items() if n.startswith(p)) for n in soft})
print(f"fewest rows bent     : {result.objective_value():g} rows, bends {el.bends(result)}")

# gurobipy's feasRelax on the same rows with the same prices: relaxobjtype 0 (weighted sum).
env = quiet_env()
for minrelax in (False, True):
    g = to_gurobi(lm.model, env)
    rows = [g.getConstrByName(n) for n in soft]
    g.Params.MIPGap = 0.0
    phase1 = g.feasRelax(0, minrelax, None, None, None, rows, [priced[n] for n in soft])
    g.optimize()
    added = {v.VarName: round(v.X, 6) for v in g.getVars() if v.VarName.startswith("Art") and v.X > 1e-6}
    if minrelax:
        print(f"feasRelax, minrelax=True : least violation {phase1:g}, NPV ${g.ObjVal:,.0f}k, {added}")
    else:
        print(f"feasRelax, minrelax=False: violation {g.ObjVal:g}, {added}")
for name in ("budget_2028", "floor_Coast", "must_P017"):        # how feasRelax wrote each kind of row
    row = g.getRow(g.getConstrByName(name))
    print(f"row {name:<12} ({g.getConstrByName(name).Sense}):",
          [(row.getVar(k).VarName, row.getCoeff(k)) for k in range(row.size()) if row.getVar(k).VarName.startswith("Art")])
