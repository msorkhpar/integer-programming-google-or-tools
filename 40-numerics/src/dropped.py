"""A coefficient of 1e-9 never reaches HiGHS: the nonzero count gives it away."""

from ortools.math_opt.python import mathopt

from loan_model import row_violations, solve

for a in (1e-8, 1e-9):
    model = mathopt.Model(name="tiny")
    x = model.add_variable(lb=0, ub=1000, name="x")
    y = model.add_binary_variable(name="y")
    model.add_linear_constraint(a * x + y <= 1, name="row")
    model.maximize(x + y)
    result, log = solve(model)
    built = sum(len(list(model.row_nonzeros(r))) for r in model.linear_constraints())
    values = result.variable_values()
    print(f"a = {a:.0e}: built {built} nonzeros; HiGHS: {log[0]}")
    print(f"  {result.termination.reason.name}  x = {values[x]:g}  y = {values[y]:g}"
          f"  row broken by {row_violations(model, values).get('row', 0.0):.1e}")
