"""Lesson 4.5.3: the same method choice with one Boolean per job and method, and no Element.

weeks_j = sum_m W_j[m] * use[j, m] is a linear expression once exactly one use[j, m] is 1. An
interval's size must be affine (one variable times a constant, plus a constant), so the sum goes
into an integer variable first. GridCap is fictional.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve
from methods_element import DATA, METHODS

probe = cp_model.CpModel()
use = [probe.new_bool_var(f"use_{m}") for m in METHODS]
start = probe.new_int_var(0, 14, "start")
end = probe.new_int_var(0, 14, "end")
try:
    probe.new_interval_var(start, sum(w * u for w, u in zip(DATA["P011"][0], use)), end, "work_P011")
except TypeError as error:
    print("a sum as the size:", error)

for deadline in (14, 8, 5):
    model = cp_model.CpModel()
    use, tasks, costs = {}, [], []
    for j, (w, c) in DATA.items():
        for m in range(len(METHODS)):
            use[j, m] = model.new_bool_var(f"use_{j}_{METHODS[m]}")
        model.add_exactly_one(use[j, m] for m in range(len(METHODS)))
        weeks = model.new_int_var(min(w), max(w), f"weeks_{j}")
        model.add(weeks == sum(w[m] * use[j, m] for m in range(len(METHODS))))
        costs.append(sum(c[m] * use[j, m] for m in range(len(METHODS))))
        start = model.new_int_var(0, deadline, f"start_{j}")
        end = model.new_int_var(0, deadline, f"end_{j}")
        tasks.append(model.new_interval_var(start, weeks, end, f"work_{j}"))
    model.add_no_overlap(tasks)
    model.minimize(sum(costs))
    solver, status = solve(model)
    print(f"deadline week {deadline}: {status}, cost ${solver.objective_value:.0f}k")
