"""Lesson 6.5.2: all-or-nothing bundles, and bundles that must start in the same year.

GridCap is a fictional utility's portfolio; the two bundles below are invented for the lesson.
"""

from gridcap import generate
from planning_model import build, money, schedule, solve_highs

small = generate("small")
BUNDLES = {
    "Plains feeders": ["P013", "P026", "P040"],      # one feeder program: all of it or none
    "Ridge vegetation": ["P008", "P020", "P035"],    # one crew mobilization for all three
}


def all_or_nothing(plan, members):
    first = members[0]
    for other in members[1:]:
        plan.model.add_linear_constraint(plan.started(other) == plan.started(first),
                                         name=f"bundle_{first}_{other}")


def same_year(plan, members):
    first = members[0]
    common = set.intersection(*(set(small.project(i).starts()) for i in members))
    for i in members:
        for t in small.project(i).starts():
            if t not in common:
                plan.model.add_linear_constraint(plan.x[i, t] == 0, name=f"apart_{i}_{t}")
    for other in members[1:]:
        for t in sorted(common):
            plan.model.add_linear_constraint(plan.x[other, t] == plan.x[first, t],
                                             name=f"together_{first}_{other}_{t}")
    return sorted(common)


for name, members in BUNDLES.items():
    print(f"{name}: " + ", ".join(f"{i} {small.project(i).capex:,} may start {list(small.project(i).starts())}"
                                    for i in members))
    base = None
    for label, rule in [("no bundle", None), ("all or nothing", all_or_nothing), ("same year", same_year)]:
        plan = build(small)
        note = ""
        if rule is not None:
            common = rule(plan, members)
            note = f"  common years {common}" if common is not None else ""
        result = solve_highs(plan.model)
        starts = schedule(plan, result)
        base = result.objective_value() if base is None else base
        print(f"  {label:14}  NPV {money(result.objective_value())}  costs {money(base - result.objective_value()):>5}  "
              f"{ {i: starts.get(i, '-') for i in members} }{note}")
