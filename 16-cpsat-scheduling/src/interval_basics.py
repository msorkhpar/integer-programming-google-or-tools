"""Lesson 4.5.1: an interval variable ties a start, a size and an end into one object.

Patterned on the OR-Tools samples interval_sample_sat.py and optional_interval_sample_sat.py,
https://github.com/google/or-tools/tree/stable/ortools/sat/samples. GridCap is fictional.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve
from season import HORIZON

model = cp_model.CpModel()
start = model.new_int_var(0, HORIZON, "start_P014")
end = model.new_int_var(0, HORIZON, "end_P014")
trim = model.new_interval_var(start, 2, end, "trim_P014")
print(repr(trim))

same = model.new_fixed_size_interval_var(start, 2, "trim_P014_fixed")
print(repr(same))
holiday = model.new_fixed_size_interval_var(25, 1, "holiday")
print(repr(holiday))

model.add(start >= 3)
model.minimize(end)
solver, status = solve(model)
print(f"with the interval:    {status}  start {solver.value(start)}  end {solver.value(end)}")

loose = cp_model.CpModel()
start = loose.new_int_var(0, HORIZON, "start_P014")
end = loose.new_int_var(0, HORIZON, "end_P014")
loose.add(start >= 3)
loose.minimize(end)
solver, status = solve(loose)
print(f"without the interval: {status}  start {solver.value(start)}  end {solver.value(end)}")
