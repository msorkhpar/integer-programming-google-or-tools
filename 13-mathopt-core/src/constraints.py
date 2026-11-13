"""Linear constraints: every form MathOpt accepts, what it stores, and the two it refuses."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="constraints")
x = model.add_binary_variable(name="x")
y = model.add_variable(lb=0, ub=2.5, name="y")
z = model.add_integer_variable(lb=0, ub=4, name="z")


def show(row: mathopt.LinearConstraint) -> None:
    terms = ", ".join(f"{t.coefficient:g}*{t.variable.name}" for t in row.terms())
    print(f"{row.name:8} lb={row.lower_bound:<5g} ub={row.upper_bound:<5g} terms: {terms}")


show(model.add_linear_constraint(x + y <= 1.5, name="upper"))
show(model.add_linear_constraint(x + z >= 1, name="lower"))
show(model.add_linear_constraint(y == 2 * x, name="equal"))
show(model.add_linear_constraint((1 <= y + z) <= 3, name="ranged"))
show(model.add_linear_constraint(2 * x + 5 <= y + 7, name="moved"))
show(model.add_linear_constraint(lb=1, ub=3, expr=x + z, name="keyword"))

try:
    model.add_linear_constraint(1 <= y + z <= 3)
except TypeError as error:
    for line in str(error).splitlines():
        print("TypeError:", line)
try:
    model.add_linear_constraint(x + y != 1)
except TypeError as error:
    print("TypeError:", error)
