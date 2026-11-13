"""A share rule written as a ratio is not linear; multiplied out by the total, it is."""

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS

model = mathopt.Model(name="share rule")
s = {k: model.add_variable(lb=0, name=f"s_{k}") for k in PROGRAMS}
total = sum(s.values())

try:
    model.add_linear_constraint(s["transmission"] / total <= 0.5, name="share_transmission")
except TypeError as error:
    print("ratio refused:", type(error).__name__)

row = model.add_linear_constraint(s["transmission"] <= 0.5 * total, name="share_transmission")
terms = sorted(row.terms(), key=lambda t: t.variable.id)
print("stored as:", row.lower_bound, "<=", " ".join(f"{t.coefficient:+g}*{t.variable.name}" for t in terms),
      "<=", row.upper_bound)
