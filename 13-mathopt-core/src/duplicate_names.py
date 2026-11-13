"""Names are for people, but MathOpt checks them: two variables with one name are refused at solve time."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="duplicate-names")
first = model.add_binary_variable(name="x_P001")
second = model.add_binary_variable(name="x_P001")      # accepted here: nothing is checked yet
model.maximize(first + second)
print("built:", model.get_num_variables(), "variables, both named", first.name)
try:
    mathopt.solve(model, mathopt.SolverType.HIGHS)
except Exception as error:                              # OR-Tools 9.15 raises an AttributeError here
    print("raised:", type(error).__name__)
    print("reason:", error.__context__)                # the real message (lesson 4.2.4)
