"""A cutoff stop that the solver reports and the 9.15 Python wrapper cannot read."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

milp = build(generate("small")).model            # its optimum is $22,532k
for cutoff in (20_000.0, 30_000.0):
    for solver in (mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT):
        params = mathopt.SolveParameters(cutoff_limit=cutoff)
        try:
            result = solve(milp, solver, params)
            print(f"cutoff {cutoff:,.0f} {solver.name:<6}: {result.termination.reason.name}"
                  f" {result.objective_value():,.0f}")
        except ValueError as error:
            print(f"cutoff {cutoff:,.0f} {solver.name:<6}: ValueError: {error}")
print("Limit members:", [limit.name for limit in mathopt.Limit])
