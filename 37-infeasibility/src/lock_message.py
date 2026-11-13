"""Lesson 9.1.6: the Budget Lock scenario explained in one planner-readable message (the section 9 milestone).

GridCap is a fictional utility's portfolio. The program runs the whole diagnosis: the pre-solve
checks (lesson 9.1.2), every conflict in turn (lessons 9.1.3 and 9.1.5), each conflict in plain
words (this lesson), and the cheapest repair under the $k prices of lesson 9.1.4, checked by a solve.
"""

from dataclasses import replace

from checks import run_checks
from elastic import elastic, min_violation
from filters import Oracle, deletion_filter
from gridcap import generate
from lock_model import LOCK, build, solve
from message import explain

small = generate("small")
scenario = LOCK
lm = build(small, scenario)
print(f"Scenario '{scenario.name}' has no plan that keeps every rule.")
for problem in run_checks(small, scenario):
    print(f"Found before solving: {problem.subject}: {problem.detail}.")

conflicts = []
oracle = Oracle(lm.model)
active = list(lm.rules)
while oracle.infeasible(active):
    conflict = deletion_filter(oracle, active)
    conflicts.append(conflict)
    active.remove(next(n for n in conflict if n.startswith(("force_", "budget_", "crews_"))))

for number, conflict in enumerate(conflicts, start=1):
    print()
    print(f"Conflict {number} of {len(conflicts)}.", end=" ")
    for line in explain(conflict, small, scenario):
        print(line)

# One repair for the whole scenario: the least violation, with $k prices (lesson 9.1.4), then checked.
PRICE = {"budget_": 1.0, "floor_": 1.0, "crews_": 50.0, "force_": 10_000.0, "must_": 10_000.0}
soft = {n: w for n in lm.rules for p, w in PRICE.items() if n.startswith(p)}
el = elastic(lm.model, soft)
bends = el.bends(min_violation(el))
budget = {**scenario.budget}
crews = {**scenario.crews}
for name, amount in bends.items():
    kind, _, rest = name.partition("_")
    if kind == "budget":
        budget[int(rest)] = budget.get(int(rest), small.budget[int(rest)]) + round(amount)
    elif kind == "crews":
        program, year = rest.rsplit("_", 1)
        crews[program, int(year)] = crews.get((program, int(year)), small.crews[program, int(year)]) + round(amount)
repaired = replace(scenario, name="repaired", budget=budget, crews=crews)
result = solve(build(small, repaired).model)
print()
print("The cheapest repair, with a crew-month priced at $50k and a broken must-do or override at $10,000k:")
for year, value in sorted(budget.items()):
    old = scenario.budget.get(year, small.budget[year])
    if value != old:
        print(f"  - the {year} budget: ${value:,}k instead of ${old:,}k")
for (program, year), value in sorted(crews.items()):
    old = scenario.crews.get((program, year), small.crews[program, year])
    if value != old:
        print(f"  - {program} crews in {year}: {value} crew-months instead of {old}")
print(f"With these, the model finds a plan: {result.termination.reason.name}, NPV ${result.objective_value():,.0f}k.")
