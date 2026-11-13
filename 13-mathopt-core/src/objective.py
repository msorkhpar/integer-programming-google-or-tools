"""The objective: one per model, set by maximize or minimize; a second call replaces the first."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="objective")
x = model.add_binary_variable(name="x")
y = model.add_variable(lb=0, ub=2.5, name="y")
model.add_linear_constraint(x + y <= 1.5, name="c")

model.maximize(2 * x + y)
print("first :", model.objective.is_maximize, dict(sorted((t.variable.name, t.coefficient) for t in model.objective.linear_terms())))
model.minimize(x - y + 10)
print("second:", model.objective.is_maximize, dict(sorted((t.variable.name, t.coefficient) for t in model.objective.linear_terms())),
      "offset", model.objective.offset)

result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print(result.termination.reason.name, "objective", result.objective_value(),
      "x =", result.variable_values(x), "y =", result.variable_values(y))
