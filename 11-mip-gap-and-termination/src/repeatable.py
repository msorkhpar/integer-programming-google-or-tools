"""Run the same node-limited solve twice: the same work, so the same stop."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, plan, solve_highs

sel = build(generate("medium"))
params = mathopt.SolveParameters(node_limit=200, relative_gap_tolerance=0.0)
first = solve_highs(sel.model, params)
second = solve_highs(sel.model, params)

for name, r in (("first", first), ("second", second)):
    print(f"{name}:  {r.termination.limit.name}, incumbent {r.objective_value():,.0f}, "
          f"bound {r.best_objective_bound():,.0f}, nodes {r.solve_stats.node_count}")
print(f"same plan: {plan(sel, first) == plan(sel, second)}")
print(f"same solve_time: {first.solve_stats.solve_time == second.solve_stats.solve_time}")
