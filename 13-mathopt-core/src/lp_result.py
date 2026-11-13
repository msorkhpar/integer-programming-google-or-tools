# Adapted from the OR-Tools example advanced_linear_programming.py,
# https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py
"""An LP's result carries more than a MILP's: dual values, reduced costs and a basis."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

model = mathopt.Model(name="advanced_linear_programming")
x = [model.add_variable(lb=0.0, name=f"x{j}") for j in range(3)]
constraints = [
    model.add_linear_constraint(10 * x[0] + 4 * x[1] + 5 * x[2] <= 600, name="c1"),
    model.add_linear_constraint(2 * x[0] + 2 * x[1] + 6 * x[2] <= 300, name="c2"),
    model.add_linear_constraint(mathopt.fast_sum(x) <= 100, name="c3"),
]
model.maximize(10 * x[0] + 6 * x[1] + 4 * x[2])

result = mathopt.solve(model, mathopt.SolverType.GLOP)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"model failed to solve to optimality: {result.termination}")
print("objective  :", round(result.objective_value(), 4))
print("values     :", [round(v, 4) for v in result.variable_values(x)])
if not result.has_dual_feasible_solution():
    raise RuntimeError("no dual solution was returned on optimal")
print("duals      :", [round(d, 4) + 0.0 for d in result.dual_values(constraints)])   # + 0.0 turns -0.0 into 0.0
print("reduced    :", [round(r, 4) for r in result.reduced_costs(x)])
if not result.has_basis():
    raise RuntimeError("no basis was returned on optimal")
print("row status :", [s.name for s in result.constraint_status(constraints)])
print("var status :", [s.name for s in result.variable_status(x)])

# The same reading on GridCap small's LP relaxation: what one more $k of each year's budget is worth.
sel = build(generate("small"), integer=False)
relaxed = solve(sel.model, mathopt.SolverType.GLOP)
print("LP relaxation:", relaxed.termination.reason.name, round(relaxed.objective_value(), 1))
for year, row in sel.budget.items():
    dual = round(relaxed.dual_values(row), 4) + 0.0
    print(f"  {row.name}: dual {dual:.4f}  status {relaxed.constraint_status(row).name}")
