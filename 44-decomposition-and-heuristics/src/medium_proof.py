"""The monolithic MILP of GridCap medium with crews, solved to a proven optimum (it takes a while)."""

from gridcap import generate

from capital import EXACT, build, solve_highs, violations, schedule

medium = generate("medium")
cap = build(medium, crews=True)
result = solve_highs(cap.model, EXACT)
print(f"{result.termination.reason.name}: plan {result.objective_value():,.0f},"
      f" bound {result.termination.objective_bounds.dual_bound:,.0f}, {result.solve_stats.node_count:,} nodes,"
      f" breaks {violations(medium, schedule(cap, result), crews=True) or 'nothing'}")
