"""MathOpt stores every row as lb <= a.x <= ub, with the variables moved to the left."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="row shapes")
t = model.add_variable(lb=0, name="t")
d = model.add_variable(lb=0, ub=4000, name="d")
free = model.add_variable(name="free")                 # no lb, no ub given
model.add_linear_constraint(t + d <= 8890, name="written_le")
model.add_linear_constraint(d >= 300, name="written_ge")
model.add_linear_constraint(t == 2 * d, name="written_eq")
model.add_linear_constraint(lb=1000, ub=5000, expr=t + d, name="written_range")
model.add_linear_constraint(t <= 0.5 * (t + d) + 100, name="written_both_sides")

for row in model.linear_constraints():
    terms = " ".join(f"{x.coefficient:+g}*{x.variable.name}" for x in sorted(row.terms(), key=lambda x: x.variable.id))
    print(f"{row.name:19} {row.lower_bound:>7} <= {terms:12} <= {row.upper_bound}")
for v in model.variables():
    print(f"variable {v.name}: {v.lower_bound} <= {v.name} <= {v.upper_bound}")
