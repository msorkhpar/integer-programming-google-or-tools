"""Lesson 6.5.4: a maximum lag, alone and together with the minimum lag.

GridCap is a fictional utility's portfolio; the maximum lag below is invented for the lesson.
P023 (a Valley distribution replacement) must start at least 1 year after P022 (the Valley
transmission repair it depends on), and the crews ask that it start no more than MAX years after.
"""

from gridcap import generate
from planning_model import build, money, schedule, solve_highs

small = generate("small")
PARENT, CHILD, MIN = "P022", "P023", 1


def max_lag_rows(plan, k: int):
    """If the child is funded, it has started by year t whenever the parent had started by t - k."""
    for t in small.years:
        plan.model.add_linear_constraint(
            plan.started_by(CHILD, t) >= plan.started_by(PARENT, t - k) + plan.started(CHILD) - 1,
            name=f"within_{CHILD}_{t}")


print(f"{PARENT} may start {list(small.project(PARENT).starts())}, NPV {dict(small.project(PARENT).npv)}")
print(f"{CHILD} may start {list(small.project(CHILD).starts())}, NPV {dict(small.project(CHILD).npv)}")
for label, k in [("min lag 1 only", None), ("max lag 2", 2), ("max lag 1", 1), ("max lag 0", 0)]:
    plan = build(small)                    # GridCap's own row: P023 at least 1 year after P022
    if k is not None:
        max_lag_rows(plan, k)
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    print(f"{label:15} NPV {money(result.objective_value())}  {PARENT} {starts.get(PARENT, '-')}  "
          f"{CHILD} {starts.get(CHILD, '-')}")
