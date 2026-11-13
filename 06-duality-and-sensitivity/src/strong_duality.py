"""Lesson 2.3.2: at the optimum the primal and the dual have the same value, and the prices match."""

from ortools.math_opt.python import mathopt

from budget_lp import build, clean
from certificates import price_bound
from dualize import dualize
from gridcap import generate

tiny = generate("tiny")
lp = build(tiny)
dual_model, price = dualize(lp.model)
print(f"primal: {lp.model.get_num_variables()} variables, {lp.model.get_num_linear_constraints()} rows; "
      f"dual: {dual_model.get_num_variables()} variables, {dual_model.get_num_linear_constraints()} rows")

primal = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
dual = mathopt.solve(dual_model, mathopt.SolverType.GLOP)
print(f"primal {primal.termination.reason.name} max {primal.objective_value():,.4f}")
print(f"dual   {dual.termination.reason.name} min {dual.objective_value():,.4f}")
same = all(abs(dual.variable_values(price[row.name]) - primal.dual_values(row)) < 1e-9
           for row in lp.model.linear_constraints())
print(f"dual LP's prices equal MathOpt's dual_values on all {len(price)} rows: {same}")

# A floor above what the vegetation crews can do in three years: no plan exists.
too_high = build(tiny, floor=2000)
dual_model, _ = dualize(too_high.model)
print("floor 2000: primal", mathopt.solve(too_high.model, mathopt.SolverType.GLOP).termination.reason.name,
      "| dual with GLOP", mathopt.solve(dual_model, mathopt.SolverType.GLOP).termination.reason.name,
      "| dual with HiGHS", mathopt.solve(dual_model, mathopt.SolverType.HIGHS).termination.reason.name)
old_prices = {row.name: primal.dual_values(row) for row in lp.model.linear_constraints()}
print(f"floor 2000: the floor-900 prices are still dual feasible, bound {price_bound(too_high.model, old_prices):,.1f}")
