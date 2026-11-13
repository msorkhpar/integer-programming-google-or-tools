"""Lesson 6.3.2: a crew that may not do a project gets no variable for it.

Only the Ridge and Valley crews and the contractor are qualified for transmission work. GridCap,
its crews and their qualifications are fictional.
"""

from gridcap import generate
from knapsack_models import (CAPACITY, CONTRACTOR, CREWS, EXACT, LINE_CREWS, assignment_model, base_plan,
                             chosen, eligible, size, solve_highs)

small = generate("small")
plan = base_plan(small)
crews = CREWS + (CONTRACTOR,)

for p in plan:
    if not any(eligible(p, k) and size(p, k) <= CAPACITY[k] for k in crews):
        print(f"{p.project_id}: no crew can take it")
line_work = sum(min(size(p, k) for k in LINE_CREWS) for p in plan if p.program == "transmission")
print(f"transmission work needs at least {line_work} crew-months; "
      f"line crews have {sum(CAPACITY[k] for k in LINE_CREWS)}")

for only in (False, True):
    model, x = assignment_model(plan, only_eligible=only)
    result = solve_highs(model, EXACT)
    crew_of = dict(chosen(x, result))
    label = "line crews only for transmission" if only else "any crew for any project"
    print(f"{label}: {len(x)} variables, labour ${result.objective_value():,.0f}k")
    for k in crews:
        mine = [p for p in plan if crew_of[p.project_id] == k]
        print(f"  {k:<10} {sum(size(p, k) for p in mine):3} of {CAPACITY[k]}: "
              f"{' '.join(p.project_id + p.program[0] for p in mine)}")
