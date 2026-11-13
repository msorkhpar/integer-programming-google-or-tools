"""The inherited PuLP script and its MathOpt port on three GridCap sizes, checked the way lesson 4.7.2 checks a port.

The port runs SCIP here, because this process has imported pulp (see highs_after_pulp.py).
"""

from dataclasses import replace

from ortools.math_opt.python import mathopt

from gridcap import generate
from legacy_selection import solve_legacy
from mathopt_selection import solve_ported


def allowed(portfolio, funded) -> bool:
    """Does a plan keep every rule of the selection model? Checked from the data, with no solver."""
    chosen = set(funded)
    if sum(portfolio.project(pid).capex for pid in chosen) > portfolio.capital_budget:
        return False
    groups = {}
    for p in portfolio.projects:
        if p.must_do and p.project_id not in chosen:
            return False
        if p.parent and p.project_id in chosen and p.parent not in chosen:
            return False
        if p.alt_group and p.project_id in chosen:
            groups[p.alt_group] = groups.get(p.alt_group, 0) + 1
    return all(n <= 1 for n in groups.values())


for size in ("tiny", "small", "medium"):
    portfolio = generate(size)
    status, old_value, old_plan, prob = solve_legacy(portfolio, gap=0)
    reason, new_value, new_plan, model = solve_ported(portfolio, mathopt.SolverType.GSCIP, gap=0.0)
    same_rows = sorted(r.name for r in prob.constraints()) == sorted(c.name for c in model.linear_constraints())
    print(f"{size:<6} PuLP+CBC {status} ${old_value:,.0f}k | MathOpt+SCIP {reason} ${new_value:,.0f}k | "
          f"same value: {abs(old_value - new_value) < 1e-6}, same plan: {sorted(old_plan) == sorted(new_plan)}, "
          f"each plan allowed: {allowed(portfolio, old_plan) and allowed(portfolio, new_plan)}, same rows: {same_rows}")

small = generate("small")
tight = replace(small, capital_budget=sum(p.capex for p in small.projects if p.must_do) - 1000)
print("infeasible budget:", solve_legacy(tight)[:3], "|", solve_ported(tight, mathopt.SolverType.GSCIP)[:3])

# The three lines of silent_rows.py, handed to MathOpt's add_linear_constraint.
model = mathopt.Model(name="silent")
x = {i: model.add_binary_variable(name="x_" + i) for i in ("P005", "P007")}
last_plan = {"P005": 1.0}
for label, row in (("lock on data", lambda: last_plan["P005"] == 1),
                   ("chained band", lambda: 1 <= x["P005"] + x["P007"] <= 2),
                   ("no comparison", lambda: x["P005"] + x["P007"])):
    try:
        model.add_linear_constraint(row(), name=label.replace(" ", "_"))
        print(f"MathOpt, {label}: added")
    except TypeError as error:
        print(f"MathOpt, {label}: TypeError: {str(error).splitlines()[0].split('. ')[0]}")
