"""Lesson 6.3.2: assigning the plan's projects to crews is a generalized assignment problem.

The plan is GridCap small's best selection (20 projects). A regional crew loses one crew-month to
travel on a project outside its region; the contractor works anywhere at a higher rate. GridCap,
its crews and their rates are fictional.
"""

from gridcap import generate
from knapsack_models import (CAPACITY, CONTRACTOR, CREWS, EXACT, assignment_model, base_plan, chosen, size,
                             solve_highs)

small = generate("small")
plan = base_plan(small)
print(f"the plan: {len(plan)} projects, {sum(p.crew_months for p in plan)} crew-months")
print("each region's own work against its crew:")
for k in CREWS:
    home = sum(p.crew_months for p in plan if p.region == k)
    print(f"  {k:<7} {home:3} of {CAPACITY[k]}{'  over' if home > CAPACITY[k] else ''}")

model, x = assignment_model(plan)
result = solve_highs(model, EXACT)
crew_of = dict(chosen(x, result))
print(f"cheapest assignment: labour ${result.objective_value():,.0f}k")
for k in CREWS + (CONTRACTOR,):
    mine = [p for p in plan if crew_of[p.project_id] == k]
    load = sum(size(p, k) for p in mine)
    away = [f"{p.project_id}({p.region})" for p in mine if k != CONTRACTOR and p.region != k]
    print(f"  {k:<10} {load:3} of {CAPACITY[k]}; away from home: {' '.join(away) if away else '-'}"
          + (f"; projects {' '.join(p.project_id for p in mine)}" if k == CONTRACTOR else ""))
