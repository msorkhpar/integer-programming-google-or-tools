"""Lesson 6.1.2: four planning rules in words, each one row on GridCap small's selection model.

GridCap is a fictional utility's portfolio, and these rules are invented for the lesson.
"""

from gridcap import generate
from selection_model import EXACT, build, funded, solve_highs

small = generate("small")


def conflict(sel):        # P030 and P032 share one Valley line outage: not both
    x = sel.x
    sel.model.add_linear_constraint(x["P030"] + x["P032"] <= 1, name="outage_P030_P032")


def needs(sel):           # the P028 tower replacement needs P024 to carry Ridge load meanwhile
    x = sel.x
    sel.model.add_linear_constraint(x["P028"] <= x["P024"], name="needs_P028_P024")


def both_need(sel):       # P022 and P025 together overload the Valley yard unless P033 rebuilds it
    x = sel.x
    sel.model.add_linear_constraint(x["P022"] + x["P025"] - 1 <= x["P033"], name="yard_P022_P025")


def needs_one(sel):       # undergrounding P034 needs one of the Plains replacements P013 or P040
    x = sel.x
    sel.model.add_linear_constraint(x["P034"] <= x["P013"] + x["P040"], name="feed_P034")


def solve(*rules):
    sel = build(small)
    for rule in rules:
        rule(sel)
    result = solve_highs(sel.model, EXACT)
    return result.objective_value(), funded(sel, result)


npv0, plan0 = solve()
print(f"no extra rule: NPV ${npv0:,.0f}k, {len(plan0)} projects")
for rule in (conflict, needs, both_need, needs_one):
    npv, plan = solve(rule)
    print(f"{rule.__name__:10} NPV ${npv:,.0f}k ({npv - npv0:+,.0f})  adds {sorted(set(plan) - set(plan0))}  "
          f"drops {sorted(set(plan0) - set(plan))}")
npv, plan = solve(conflict, needs, both_need, needs_one)
print(f"all four   NPV ${npv:,.0f}k ({npv - npv0:+,.0f})  adds {sorted(set(plan) - set(plan0))}  "
      f"drops {sorted(set(plan0) - set(plan))}")
