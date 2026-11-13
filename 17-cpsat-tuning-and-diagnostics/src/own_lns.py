"""Lesson 4.6.1: a hand-written large neighborhood search (LNS) on GridCap medium.

GridCap is a fictional utility's portfolio. Start from the plan one worker finds in 3 units of
deterministic time, then repeat: free the projects of two regions, fix every other start variable
to its current value, hint the current plan, and let CP-SAT re-plan the freed part for 0.5 units.
Keep the result if it is better. One worker and a seeded `random.Random` make every number repeat.
"""

import random

from ortools.sat.python import cp_model

from cpsat_plan import build, schedule
from gridcap import REGIONS, generate

medium = generate("medium")


def solve(plan, work: float) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.max_deterministic_time = work
    solver.solve(plan.model)
    return solver


plan = build(medium)
solver = solve(plan, 3.0)
current, best, spent = schedule(plan, solver), solver.objective_value, solver.deterministic_time
print(f"start          plan ${best:,.0f}k  work {spent:.2f}")

rng = random.Random(17)
for step in range(1, 11):
    regions = sorted(rng.sample(REGIONS, 2))
    free = {p.project_id for p in medium.projects if p.region in regions}
    plan = build(medium)
    for (pid, t), var in plan.x.items():
        value = 1 if current.get(pid) == t else 0
        plan.model.add_hint(var, value)
        if pid not in free:
            plan.model.add(var == value)              # outside the neighborhood: keep the current plan
    solver = solve(plan, 0.5)
    spent += solver.deterministic_time
    if solver.objective_value > best:
        current, best = schedule(plan, solver), solver.objective_value
    print(f"step {step:>2} {'+'.join(regions):<13} plan ${best:,.0f}k  work {spent:.2f}")

plain = solve(build(medium), spent)
print(f"one plain solve with the same work: plan ${plain.objective_value:,.0f}k")
