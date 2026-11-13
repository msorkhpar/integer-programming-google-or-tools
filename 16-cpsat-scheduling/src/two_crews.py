"""Lesson 4.5.1: two crews, and each job done by exactly one of them, with optional intervals.

Each job gets one optional interval per crew, all sharing the job's start and end; exactly one of
them is present, and each crew's NoOverlap sees only the present ones. The pattern is the CP-SAT
Primer's "multiple rooms" example (https://d-krupke.github.io/cpsat-primer/advanced_modelling.html)
with the optional intervals of the OR-Tools sample optional_interval_sample_sat.py. GridCap is
fictional.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve
from one_crew import WORK, job
from season import HORIZON

CREW_NAMES = ["A", "B"]
BLOCKED = {"A": [(8, 1, "training")], "B": [(0, 4, "finishing last season")]}

model = cp_model.CpModel()
start, end, does = {}, {}, {}
on_crew = {c: [] for c in CREW_NAMES}
for j in WORK:
    start[j] = model.new_int_var(0, HORIZON, f"start_{j}")
    end[j] = model.new_int_var(0, HORIZON, f"end_{j}")
    for c in CREW_NAMES:
        does[j, c] = model.new_bool_var(f"{c}_does_{j}")
        on_crew[c].append(model.new_optional_interval_var(start[j], job[j].weeks, end[j], does[j, c], f"{j}_by_{c}"))
    model.add_exactly_one(does[j, c] for c in CREW_NAMES)
for c in CREW_NAMES:
    for first, weeks, name in BLOCKED[c]:
        on_crew[c].append(model.new_fixed_size_interval_var(first, weeks, f"{c}_{name}"))
    model.add_no_overlap(on_crew[c])

makespan = model.new_int_var(0, HORIZON, "makespan")
model.add_max_equality(makespan, [end[j] for j in WORK])
model.minimize(makespan)
solver, status = solve(model)

print(f"{status}: makespan {solver.value(makespan)} weeks")
for c in CREW_NAMES:
    rows = [(solver.value(start[j]), solver.value(end[j]), j) for j in WORK if solver.boolean_value(does[j, c])]
    rows += [(first, first + weeks, name) for first, weeks, name in BLOCKED[c]]
    print(f"  crew {c}: " + ", ".join(f"{name} {s}-{e - 1}" for s, e, name in sorted(rows)))

# The shortcut the Primer warns about: one ordinary interval per job, put in both crews' lists.
shared = cp_model.CpModel()
ends, lists = [], {c: [] for c in CREW_NAMES}
for j in WORK:
    s = shared.new_int_var(0, HORIZON, f"start_{j}")
    interval = shared.new_fixed_size_interval_var(s, job[j].weeks, f"work_{j}")
    ends.append(interval.end_expr())
    for c in CREW_NAMES:
        lists[c].append(interval)
for c in CREW_NAMES:
    for first, weeks, name in BLOCKED[c]:
        lists[c].append(shared.new_fixed_size_interval_var(first, weeks, f"{c}_{name}"))
    shared.add_no_overlap(lists[c])
span = shared.new_int_var(0, HORIZON, "makespan")
shared.add_max_equality(span, ends)
shared.minimize(span)
solver, status = solve(shared)
print(f"one interval in both crews' lists: {status}, makespan {solver.value(span)} weeks")
