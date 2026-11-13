"""One LP, four ways: GLOP's two simplex methods, HiGHS's barrier and PDLP, on GridCap medium."""

from ortools.math_opt.python import mathopt

from funding_lp import build, in_between
from gridcap import generate

medium = generate("medium")
lp = build(medium)
print(f"funding LP: {len(list(lp.model.variables()))} variables, "
      f"{len(list(lp.model.linear_constraints()))} rows")

RUNS = [
    ("GLOP  primal simplex", mathopt.SolverType.GLOP, mathopt.LPAlgorithm.PRIMAL_SIMPLEX),
    ("GLOP  dual simplex", mathopt.SolverType.GLOP, mathopt.LPAlgorithm.DUAL_SIMPLEX),
    ("HiGHS dual simplex", mathopt.SolverType.HIGHS, mathopt.LPAlgorithm.DUAL_SIMPLEX),
    ("HiGHS barrier", mathopt.SolverType.HIGHS, mathopt.LPAlgorithm.BARRIER),
    ("PDLP  first order", mathopt.SolverType.PDLP, mathopt.LPAlgorithm.FIRST_ORDER),
]

for label, solver, algorithm in RUNS:
    result = mathopt.solve(lp.model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
    stats = result.solve_stats
    print(f"{label:21} {result.termination.reason.name}  objective {result.objective_value():.4f}  "
          f"iterations: simplex {stats.simplex_iterations:3}, barrier {stats.barrier_iterations:2}, "
          f"first-order {stats.first_order_iterations:3}  in-between {in_between(lp, result)}")

result = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
partly = sum(1 for v in lp.f.values() if 1e-6 < result.variable_values(v) < 1 - 1e-6)
carrying = sum(1 for v in lp.carry.values() if result.variable_values(v) > 1e-6)
print(f"GLOP's vertex: {partly} projects partly funded, {carrying} years carrying money")

# No lp_algorithm: each solver runs its default. The pivot counts say which simplex form that is.
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS):
    default = mathopt.solve(lp.model, solver)
    print(f"{solver.name} default: {default.termination.reason.name}, "
          f"simplex iterations {default.solve_stats.simplex_iterations}")
