"""The facts of the MIP log, read from the log's table and from the SolveResult; then the solve proved exactly."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from mip_log import SOURCES, progress, relative_gap
from selection import five_year, solve_quiet, solve_with_log

model = five_year(generate("medium")).model
result, log = solve_with_log(model)

print("new incumbents, in the order HiGHS found them:")
for row in progress(log):
    if row.src:
        gap = f"{relative_gap(row.bound, row.sol):.4%}" if row.bound != float("inf") else "none yet"
        print(f"  {row.src} {SOURCES[row.src]:20} value {row.sol:>9,.0f}  bound {row.bound:>13,.3f}  "
              f"gap {gap:>9}  (log says {row.gap})")

bounds = result.termination.objective_bounds
print("from the SolveResult:")
print(f"  termination {result.termination.reason.name}")
print(f"  primal bound {bounds.primal_bound:,.0f}, dual bound {bounds.dual_bound:,.0f}, "
      f"gap {relative_gap(bounds.dual_bound, bounds.primal_bound):.5%}")
print(f"  nodes {result.solve_stats.node_count}, LP iterations {result.solve_stats.simplex_iterations:,}")

exact = solve_quiet(model, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
print("the same model with relative_gap_tolerance=0:")
print(f"  termination {exact.termination.reason.name}, value {exact.objective_value():,.0f}, "
      f"dual bound {exact.termination.objective_bounds.dual_bound:,.0f}, nodes {exact.solve_stats.node_count}")
