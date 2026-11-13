"""Lesson 6.5.6: a planner's manual overrides, applied as bounds on the start variables.

GridCap is a fictional utility's portfolio; the overrides below are invented for the lesson.
"""

from gridcap import generate
from override_tools import Override, apply, undo
from planning_model import build, money, schedule, solve_highs

small = generate("small")

OVERRIDES = [Override("P036", "year", 2028),       # engineering: the Coast repair goes in 2028
             Override("P032", "out"),              # the Valley repair waits for a study
             Override("P021", "not_before", 2030),  # no Coast crew before 2030
             Override("P024", "in")]               # the board wants the Ridge undergrounding, any year

plan = build(small)
rows = plan.model.get_num_linear_constraints()
base = solve_highs(plan.model)
before = schedule(plan, base)
changes = [apply(plan, o) for o in OVERRIDES]
print(f"rows before {rows}, after {plan.model.get_num_linear_constraints()}")
forced = solve_highs(plan.model)
after = schedule(plan, forced)
print(f"no overrides  NPV {money(base.objective_value())}")
print(f"overrides     NPV {money(forced.objective_value())}  costs {money(base.objective_value() - forced.objective_value())}")
for o in OVERRIDES:
    print(f"  {o.pid} {o.kind:10} {o.year or '':4}  start {before.get(o.pid, '-')} -> {after.get(o.pid, '-')}")
moved = sorted(i for i in set(before) | set(after) if before.get(i) != after.get(i)
               and i not in {o.pid for o in OVERRIDES})
print("other projects that changed:", {i: (before.get(i, "-"), after.get(i, "-")) for i in moved})
for c in reversed(changes):
    undo(plan, c)
print(f"undone        NPV {money(solve_highs(plan.model).objective_value())}  rows {plan.model.get_num_linear_constraints()}")
