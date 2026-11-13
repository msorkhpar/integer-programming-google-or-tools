"""One plan of Ridge's crew split, and the same plan with the crews renumbered."""

import itertools

from gridcap import generate
from crew_split import assignment, build, region_jobs, solve

jobs = region_jobs(generate("medium"), "Ridge")
print(f"Ridge's 14 largest transmission jobs, crew-months: {list(jobs.values())}, total {sum(jobs.values())}")
cs = build(jobs, crews=4)
result = solve(cs)
plan = assignment(cs, result)
print(f"best makespan {result.objective_value():.0f} months (a perfect split would be {sum(jobs.values()) / 4})")
for k, crew in enumerate(plan):
    print(f"  crew {k}: {' '.join(crew)}  load {sum(jobs[j] for j in crew)}")

# Renumber the crews: crew k's jobs go to crew perm[k]. Each renumbering is a different x; check that
# it satisfies every row of the model and gives the same makespan.
rows = [(c.lower_bound, {t.variable: t.coefficient for t in c.terms()}, c.upper_bound)
        for c in cs.model.linear_constraints()]
points, allowed = set(), 0
for perm in itertools.permutations(range(4)):
    on = {(j, perm[k]) for k, crew in enumerate(plan) for j in crew}
    point = {v: 1.0 if key in on else 0.0 for key, v in cs.x.items()}
    point[cs.makespan] = result.objective_value()
    allowed += all(lo - 1e-9 <= sum(a * point[v] for v, a in terms.items()) <= hi + 1e-9 for lo, terms, hi in rows)
    points.add(frozenset(on))
print(f"renumberings of the 4 crews: 24, distinct x: {len(points)}, allowed with makespan "
      f"{result.objective_value():.0f}: {allowed}")
