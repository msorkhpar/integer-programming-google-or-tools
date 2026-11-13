"""Solver cuts on the five-year selection model: SCIP with its cuts on and off, and HiGHS refusing the switch."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import five_year, solve_quiet

medium = generate("medium")
relaxed = mathopt.solve(five_year(medium, integer=False).model, mathopt.SolverType.GLOP)
print(f"LP relaxation bound: {relaxed.objective_value():,.1f}")

model = five_year(medium).model
for label, cuts in (("cuts on (default)", None), ("cuts off", mathopt.Emphasis.OFF)):
    result = solve_quiet(model, mathopt.SolverType.GSCIP, mathopt.SolveParameters(cuts=cuts))
    print(f"SCIP, {label:17}: {result.termination.reason.name}, value {result.objective_value():,.0f}, "
          f"nodes {result.solve_stats.node_count:,}")

try:
    solve_quiet(model, mathopt.SolverType.HIGHS, mathopt.SolveParameters(cuts=mathopt.Emphasis.OFF))
except Exception as error:      # OR-Tools 9.15 raises AttributeError; HiGHS's reason is on __context__
    print(f"HiGHS, cuts off: refused ({type(error).__name__})")
    print(f"  raised : {error}")
    print(f"  reason : {str(error.__context__).split(' [')[0]}")
