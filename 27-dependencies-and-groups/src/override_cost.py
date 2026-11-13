"""Lesson 6.5.6: the price of each override, one model, bounds applied and restored.

GridCap is a fictional utility's portfolio; the overrides are those of `overrides.py`.
"""

from gridcap import generate
from override_tools import Override, apply, undo
from planning_model import build, money, solve_highs

small = generate("small")
OVERRIDES = [Override("P036", "year", 2028), Override("P032", "out"),
             Override("P021", "not_before", 2030), Override("P024", "in")]

plan = build(small)                       # built once; every solve below reuses it
free = solve_highs(plan.model).objective_value()
print(f"no override   NPV {money(free)}")
for o in OVERRIDES:
    changes = apply(plan, o)
    value = solve_highs(plan.model).objective_value()
    undo(plan, changes)
    print(f"{o.pid} {o.kind:10} alone  NPV {money(value)}  costs {money(free - value)}")
changes = [apply(plan, o) for o in OVERRIDES]
together = solve_highs(plan.model).objective_value()
print(f"all four together  NPV {money(together)}  costs {money(free - together)}")
