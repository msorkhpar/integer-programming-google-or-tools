"""SCIP on the five-year model with its primal heuristics on and off: same answer, different search."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import five_year, solve_quiet

model = five_year(generate("medium")).model
for label, heuristics in (("heuristics on (default)", None), ("heuristics off", mathopt.Emphasis.OFF)):
    result = solve_quiet(model, mathopt.SolverType.GSCIP, mathopt.SolveParameters(heuristics=heuristics))
    print(f"SCIP, {label:23}: {result.termination.reason.name}, value {result.objective_value():,.0f}, "
          f"nodes {result.solve_stats.node_count:,}, LP iterations {result.solve_stats.simplex_iterations:,}")
