"""The HiGHS log of the funding LP on GridCap medium, and the same facts read from the result."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate
from solver_log import solve_with_log

lp = build(generate("medium"))
result, log = solve_with_log(lp.model, mathopt.SolverType.HIGHS)
for line in log:
    print(line)

print("--- read from the SolveResult ---")
print(f"cash rows {len(lp.cash)}, must rows {len(lp.must)}; share variables {len(lp.f)}, carry variables {len(lp.carry)}")
print(f"termination: {result.termination.reason.name}")
print(f"simplex iterations: {result.solve_stats.simplex_iterations}")
print(f"objective: {result.objective_value():.4f}")
