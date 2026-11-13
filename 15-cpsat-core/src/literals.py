"""Lesson 4.4.2: a literal, and three ways to write one implication that allow the same assignments.

Adapted from the OR-Tools examples literal_sample_sat.py and reified_sample_sat.py,
https://github.com/google/or-tools/tree/stable/ortools/sat/samples (Apache-2.0).
"""

from ortools.sat.python import cp_model

from cpsat_models import allowed_assignments

model = cp_model.CpModel()
x = model.new_bool_var("x")
not_x = ~x
print(x, not_x, ~not_x)


def with_bool_and(model, v):
    model.add_bool_and(v["x"], ~v["y"]).only_enforce_if(v["b"])


def with_implications(model, v):
    model.add_implication(v["b"], v["x"])
    model.add_implication(v["b"], ~v["y"])


def with_bool_or(model, v):
    model.add_bool_or(~v["b"], v["x"])
    model.add_bool_or(~v["b"], ~v["y"])


for form in (with_bool_and, with_implications, with_bool_or):
    print(f"{form.__name__:18} b x y allowed: {' '.join(allowed_assignments(form, 'bxy'))}")
