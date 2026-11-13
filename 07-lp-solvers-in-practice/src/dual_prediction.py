"""A dual value predicts the effect of a small budget cut; a re-solve measures a large one (GridCap medium)."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate

lp = build(generate("medium"))
solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
base = solver.solve()
price = base.dual_values(lp.cash[2030])
budget_2030 = lp.cash[2030].upper_bound
print(f"dual value of cash_2030: {price:.4f} of objective per $k; 2030 budget {budget_2030:,.0f}")

for cut in (100, 1000, round(0.1 * budget_2030), round(0.3 * budget_2030)):
    lp.cash[2030].upper_bound = budget_2030 - cut
    result = solver.solve()
    predicted = base.objective_value() - price * cut
    error = round(predicted - result.objective_value(), 4) + 0.0      # + 0.0 prints -0.0 as 0.0
    print(f"cut {cut:6,}: predicted {predicted:12.4f}  re-solved {result.objective_value():12.4f}"
          f"  error {error:8.4f}  iterations {result.solve_stats.simplex_iterations}")
    lp.cash[2030].upper_bound = budget_2030
solver.close()
