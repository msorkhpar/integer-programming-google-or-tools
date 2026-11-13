"""Finance cuts 2030 by 10%: edit the row's bound in place and re-solve, warm and cold (GridCap medium)."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate

lp = build(generate("medium"))
solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)

base = solver.solve()
print(f"base        objective {base.objective_value():.4f}  simplex iterations {base.solve_stats.simplex_iterations}")

budget_2030 = lp.cash[2030].upper_bound
lp.cash[2030].upper_bound = 0.9 * budget_2030          # the data change: one number in one row
warm = solver.solve()                                  # same solver object: starts from the last basis
cold = mathopt.solve(lp.model, mathopt.SolverType.GLOP)  # a fresh solve of the same edited model
print(f"cut, warm   objective {warm.objective_value():.4f}  simplex iterations {warm.solve_stats.simplex_iterations}")
print(f"cut, cold   objective {cold.objective_value():.4f}  simplex iterations {cold.solve_stats.simplex_iterations}")

lp.cash[2030].upper_bound = budget_2030                # undo the change before the next scenario
back = solver.solve()
print(f"restored    objective {back.objective_value():.4f}  simplex iterations {back.solve_stats.simplex_iterations}")
solver.close()

# The same cut and restore on fresh solvers, once with GLOP's default and once asking for dual simplex.
DUAL = mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX)
for label, params in (("primal simplex", mathopt.SolveParameters()), ("dual simplex", DUAL)):
    lp = build(generate("medium"))
    solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
    base = solver.solve(params=params)
    lp.cash[2030].upper_bound = 0.9 * budget_2030
    log: list[str] = []
    cut = solver.solve(params=params, msg_cb=log.extend)  # keep the cut's log to see which phases ran
    lp.cash[2030].upper_bound = budget_2030
    back = solver.solve(params=params)
    solver.close()
    phases = list(dict.fromkeys(line.split(",")[0] for line in log if "phase, iteration" in line))
    print(f"{label:14}  pivots: base {base.solve_stats.simplex_iterations:3}, cut {cut.solve_stats.simplex_iterations:2}, "
          f"restore {back.solve_stats.simplex_iterations:2}; cut objective {cut.objective_value():.4f}")
    print(f"{'':14}  phases of the cut: {', '.join(phases)}")
