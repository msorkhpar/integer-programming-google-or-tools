"""The incumbent and the best bound of GridCap medium's selection MILP, as HiGHS is allowed more nodes."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

medium = generate("medium")
sel = build(medium)
size = (len(list(sel.model.variables())), len(list(sel.model.linear_constraints())))
print(f"GridCap medium selection MILP: {size[0]} binary variables, {size[1]} rows")

relaxed = solve_highs(build(medium, integer=False).model)
print(f"LP relaxation (every x between 0 and 1): {relaxed.objective_value():,.2f}")
print()

print(f"{'node limit':>10} {'stopped':>8} {'incumbent':>10} {'best bound':>11} {'abs gap':>8} {'rel gap':>8}")
for limit in (1, 1000, 4000, 7000, 10000, 12000):
    result = solve_highs(sel.model, mathopt.SolveParameters(node_limit=limit, relative_gap_tolerance=0.0))
    incumbent = result.objective_value()
    bound = result.best_objective_bound()
    absolute = bound - incumbent
    relative = absolute / abs(incumbent)
    print(f"{limit:>10} {result.termination.limit.name:>8} {incumbent:>10,.0f} {bound:>11,.0f} "
          f"{absolute:>8,.0f} {relative:>8.3%}")

exact = solve_highs(sel.model, mathopt.SolveParameters(relative_gap_tolerance=0.0))
bounds = exact.termination.objective_bounds
print()
print(f"run to the end: {exact.termination.reason.name}, incumbent {bounds.primal_bound:,.0f}, "
      f"best bound {bounds.dual_bound:,.0f}, {exact.solve_stats.node_count:,} nodes")
