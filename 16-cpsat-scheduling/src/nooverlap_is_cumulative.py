"""Lesson 4.5.2: NoOverlap is the cumulative constraint with capacity 1 and every demand 1.

The one-crew jobs and blocked weeks of lesson 4.5.1, solved both ways. GridCap is fictional.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve
from one_crew import BLOCKED, WORK, job
from season import HORIZON


def makespan(resource: str) -> int:
    model = cp_model.CpModel()
    ends, intervals = [], []
    for j in WORK:
        start = model.new_int_var(0, HORIZON, f"start_{j}")
        intervals.append(model.new_fixed_size_interval_var(start, job[j].weeks, f"work_{j}"))
        ends.append(intervals[-1].end_expr())
    intervals += [model.new_fixed_size_interval_var(first, weeks, name) for name, (first, weeks) in BLOCKED.items()]
    if resource == "no_overlap":
        model.add_no_overlap(intervals)
    else:
        model.add_cumulative(intervals, [1] * len(intervals), 1)
    span = model.new_int_var(0, HORIZON, "makespan")
    model.add_max_equality(span, ends)
    model.minimize(span)
    solver, status = solve(model)
    return solver.value(span)


print("add_no_overlap:                 makespan", makespan("no_overlap"))
print("add_cumulative, capacity 1:     makespan", makespan("cumulative"))
