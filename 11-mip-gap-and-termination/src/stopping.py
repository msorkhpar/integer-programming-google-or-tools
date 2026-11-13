"""GridCap medium's selection MILP on HiGHS, stopped by one limit at a time."""

import datetime

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

sel = build(generate("medium"))

limits = {
    "relative gap 1%": mathopt.SolveParameters(relative_gap_tolerance=0.01),
    "relative gap 0.1%": mathopt.SolveParameters(relative_gap_tolerance=0.001),
    "absolute gap 100": mathopt.SolveParameters(absolute_gap_tolerance=100, relative_gap_tolerance=0.0),
    "100 nodes": mathopt.SolveParameters(node_limit=100, relative_gap_tolerance=0.0),
    "1 solution": mathopt.SolveParameters(solution_limit=1, relative_gap_tolerance=0.0),
}
print(f"{'limit':<18} {'reason':<9} {'limit hit':<9} {'incumbent':>9} {'bound':>9} {'gap':>6} {'rel gap':>8} {'nodes':>5}")
for name, params in limits.items():
    result = solve_highs(sel.model, params)
    t = result.termination
    p, d = t.objective_bounds.primal_bound, t.objective_bounds.dual_bound
    hit = t.limit.name if t.limit is not None else "-"
    print(f"{name:<18} {t.reason.name:<9} {hit:<9} {p:>9,.0f} {d:>9,.0f} {d - p:>6,.0f} {(d - p) / p:>8.3%} "
          f"{result.solve_stats.node_count:>5}")

timed = solve_highs(sel.model, mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=1),
                                                       relative_gap_tolerance=0.0))
print()
print(f"1 second: {timed.termination.reason.name}, limit {timed.termination.limit.name}, "
      f"has a plan: {timed.has_primal_feasible_solution()}")

first = mathopt.solve(sel.model, mathopt.SolverType.CP_SAT, params=mathopt.SolveParameters(solution_limit=1))
print(f"CP-SAT, 1 solution: {first.termination.reason.name}, limit {first.termination.limit.name}")
