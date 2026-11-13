"""Lesson 6.5.2: a child project that needs one parent, all of several parents, or any one of them.

GridCap is a fictional utility's portfolio; the dependencies below are invented for the lesson.
P028 replaces a Ridge tower set in 2030, and while it is out the load has to be carried by a
Ridge circuit that has been put underground: P024 or P037.
"""

from gridcap import generate
from planning_model import build, money, schedule, solve_highs

small = generate("small")
CHILD, PARENTS = "P028", ["P024", "P037"]


def needs_one(plan):              # P028 needs P024, started no later than P028 starts
    for t in small.project(CHILD).starts():
        plan.model.add_linear_constraint(plan.started_by(CHILD, t) <= plan.started_by("P024", t),
                                         name=f"needs_{CHILD}_P024_{t}")


def needs_all(plan):              # P028 needs both P024 and P037
    for parent in PARENTS:
        for t in small.project(CHILD).starts():
            plan.model.add_linear_constraint(plan.started_by(CHILD, t) <= plan.started_by(parent, t),
                                             name=f"needs_{CHILD}_{parent}_{t}")


def needs_any(plan):              # P028 needs at least one of P024 and P037
    for t in small.project(CHILD).starts():
        plan.model.add_linear_constraint(
            plan.started_by(CHILD, t) <= sum(plan.started_by(parent, t) for parent in PARENTS),
            name=f"needs_any_{CHILD}_{t}")


def no_rule(plan):
    pass


print(f"{CHILD} may start {list(small.project(CHILD).starts())}; "
      + "; ".join(f"{p} may start {list(small.project(p).starts())}" for p in PARENTS))
base = None
for label, rule in [("no rule", no_rule), ("needs P024", needs_one), ("needs all", needs_all),
                    ("needs any", needs_any)]:
    plan = build(small)
    rule(plan)
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    base = result.objective_value() if base is None else base
    shown = {i: starts.get(i, "-") for i in [CHILD, *PARENTS]}
    print(f"{label:10}  NPV {money(result.objective_value())}  costs {money(base - result.objective_value()):>6}  {shown}")
