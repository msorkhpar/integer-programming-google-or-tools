# Adapted from the OR-Tools example "MathOpt basic example",
# https://developers.google.com/optimization/math_opt/basic_example
# (and its sample ortools/math_opt/samples/python/basic_example.py, Apache-2.0)
"""The smallest complete MathOpt program: build a model, solve it, check the status, read the answer."""

from ortools.math_opt.python import mathopt

# 1. A model: an empty, named container. Nothing about any solver yet.
model = mathopt.Model(name="getting_started_lp")

# 2. Variables, each with its bounds (its domain).
x = model.add_variable(lb=-1.0, ub=1.5, name="x")
y = model.add_variable(lb=0.0, ub=1.0, name="y")

# 3. Constraints, each one linear comparison.
model.add_linear_constraint(x + y <= 1.5, name="c")

# 4. The objective, with its sense.
model.maximize(x + 2 * y)

# 5. Solve with a named solver, and check how the solve ended before reading anything.
result = mathopt.solve(model, mathopt.SolverType.GLOP)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"model failed to solve: {result.termination}")
print("termination:", result.termination.reason.name)
print("objective:", result.objective_value())
print("x =", result.variable_values(x), " y =", result.variable_values(y))

# The same model, untouched, on a second solver: only the SolverType changes.
again = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("HiGHS:", again.termination.reason.name, again.objective_value())
