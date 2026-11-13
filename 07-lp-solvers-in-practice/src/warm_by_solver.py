"""Does the next solve start from the last one? GLOP, HiGHS and PDLP through MathOpt (GridCap large)."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate

large = generate("large")


def iterations(result: mathopt.SolveResult) -> int:
    stats = result.solve_stats
    return stats.simplex_iterations + stats.barrier_iterations + stats.first_order_iterations


for solver_type in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP):
    lp = build(large)
    solver = mathopt.IncrementalSolver(lp.model, solver_type)
    base = solver.solve()
    lp.cash[2030].upper_bound *= 0.9
    warm = solver.solve()
    cold = mathopt.solve(lp.model, solver_type)
    solver.close()
    print(f"{solver_type.name:5} iterations: base {iterations(base):5}  after the cut, warm {iterations(warm):5}"
          f"  cold {iterations(cold):5}")
