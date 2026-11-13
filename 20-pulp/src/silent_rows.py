"""Three lines that look like rows of the inherited model and are not, each next to the line it meant.

Each case adds one planner rule to the selection model on GridCap small and solves it with CBC.
"""

import warnings

from pulp import PULP_CBC_CMD, LpConstraint, LpMaximize, LpProblem, LpStatus, LpVariable, lpSum, value

from gridcap import generate

small = generate("small")
ids = [p.project_id for p in small.projects]
last_plan = {"P005": 1.0, "P006": 0.0}        # last year's plan, read from a file: data, not variables

recorder = warnings.catch_warnings(record=True)
caught = recorder.__enter__()                  # keep every warning PuLP raises, to print it in place
warnings.simplefilter("always")
warnings.simplefilter("ignore", DeprecationWarning)


def base():
    x = LpVariable.dicts("x", ids, cat="Binary")
    prob = LpProblem("selection", LpMaximize)
    prob += lpSum(p.value * x[p.project_id] for p in small.projects), "value"
    prob += lpSum(p.capex * x[p.project_id] for p in small.projects) <= small.capital_budget, "budget"
    for p in small.projects:
        if p.must_do:
            prob += x[p.project_id] == 1, "must_" + p.project_id
        if p.parent:
            prob += x[p.project_id] <= x[p.parent], "parent_" + p.project_id
    groups = {}
    for p in small.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g in groups:
        prob += lpSum(groups[g]) <= 1, "alt_" + g
    return prob, x


def ridge(x):
    return lpSum(p.capex * x[p.project_id] for p in small.projects if p.region == "Ridge")


def crew(x):
    return lpSum(p.crew_months * x[p.project_id] for p in small.projects)


def report(label, prob, x):
    prob.solve(PULP_CBC_CMD(msg=0))
    funded = [i for i in ids if value(x[i]) > 0.5]
    print(f"{label:<22} rows {prob.numConstraints():>2}  {LpStatus[prob.status]}  objective {value(prob.objective):>7,.0f}  "
          f"value ${sum(small.project(i).value for i in funded):,}k  P005 {'in' if 'P005' in funded else 'out'}  "
          f"Ridge ${value(ridge(x)):,.0f}k  crew {value(crew(x)):.0f}")
    for w in caught:
        print(f"{'':<22} PuLP warned: {w.category.__name__}: {w.message}")
    caught.clear()


prob, x = base()
report("no extra rule", prob, x)

# Rule 1: keep last year's P005 in the plan.
prob, x = base()
row = last_plan["P005"] == 1
print("the lock row as written is a", type(row).__name__, "=", row)
prob += row, "lock_P005"
report("lock written on data", prob, x)
prob, x = base()
prob += x["P005"] == 1, "lock_P005"
report("lock written on x", prob, x)

# Rule 2: Ridge receives between $9,000k and $12,000k.
prob, x = base()
row = 9000 <= ridge(x) <= 12000
print("the chained row as written is:", row)
prob += row, "ridge_band"
report("band chained", prob, x)
prob, x = base()
prob += ridge(x) >= 9000, "ridge_min"
prob += ridge(x) <= 12000, "ridge_max"
report("band as two rows", prob, x)

# Rule 3: at most 90 crew-months in total.
prob, x = base()
prob += crew(x), "crew"
report("crew row, no <=", prob, x)
prob, x = base()
prob += crew(x) <= 90, "crew"
report("crew row with <= 90", prob, x)

print("a guard that refuses anything but a constraint:", isinstance(last_plan["P005"] == 1, LpConstraint),
      isinstance(crew(x), LpConstraint), isinstance(crew(x) <= 90, LpConstraint))
