"""Lesson 4.5.1: the same one-crew schedule with NoOverlap written out as pairwise order choices.

For every pair of jobs (and blocked periods), one Boolean says which comes first, and an enforced
linear row keeps them apart. This is the disjunction NoOverlap replaces; a MIP writes it with big-M
rows (lesson 6.2.1, later in the course). GridCap is fictional.
"""

from itertools import combinations

from ortools.sat.python import cp_model

from cpsat_run import solve
from one_crew import BLOCKED, WORK, job
from season import HORIZON

model = cp_model.CpModel()
start, end = {}, {}
for j in WORK:
    start[j] = model.new_int_var(0, HORIZON, f"start_{j}")
    end[j] = model.new_int_var(0, HORIZON, f"end_{j}")
    model.add(end[j] == start[j] + job[j].weeks)
for name, (first, weeks) in BLOCKED.items():
    start[name], end[name] = first, first + weeks

pairs = 0
for a, b in combinations(list(start), 2):
    if isinstance(start[a], int) and isinstance(start[b], int):
        continue                                    # two fixed periods: nothing to decide
    a_first = model.new_bool_var(f"{a}_before_{b}")
    model.add(end[a] <= start[b]).only_enforce_if(a_first)
    model.add(end[b] <= start[a]).only_enforce_if(~a_first)
    pairs += 1

makespan = model.new_int_var(0, HORIZON, "makespan")
model.add_max_equality(makespan, [end[j] for j in WORK])
model.minimize(makespan)
solver, status = solve(model)
print(f"{status}: makespan {solver.value(makespan)} weeks with {pairs} order Booleans")
