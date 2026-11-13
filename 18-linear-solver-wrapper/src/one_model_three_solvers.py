"""Lesson 4.7.2: the ported GridCap selection model, built once and handed to three solvers.

In pywraplp the same switch means building the model again in a new solver object. GridCap is a
fictional utility's portfolio.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from ported_selection import build, quiet_solve

small = generate("small")
model, x = build(small)
for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT):
    result = quiet_solve(model, solver, mathopt.SolveParameters(relative_gap_tolerance=0.0))
    funded = sum(result.variable_values(v) > 0.5 for v in x.values())
    print(f"{solver.name:7} {result.termination.reason.name}: value ${result.objective_value():,.0f}k, {funded} funded")
