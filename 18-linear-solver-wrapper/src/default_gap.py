"""Lesson 4.7.2: which relative gap SCIP stops at when MathOpt passes none.

MathOpt sends `relative_gap_tolerance` only when it is set; left at None, SCIP keeps its own default.
The program solves the port on GridCap medium with the gap unset and with 1e-4, pywraplp's default,
and prints the plan's value, the proven bound and the gap between them. GridCap is a fictional
utility's portfolio.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from ported_selection import build, quiet_solve

medium = generate("medium")
for gap in (None, 1e-4):
    model, _ = build(medium)
    result = quiet_solve(model, mathopt.SolverType.GSCIP,
                         mathopt.SolveParameters(relative_gap_tolerance=gap))
    value = result.objective_value()
    bound = result.termination.objective_bounds.dual_bound
    print(f"relative_gap_tolerance {gap}: {result.termination.reason.name}  plan ${value:,.0f}k  "
          f"bound ${bound:,.0f}k  gap {(bound - value) / value:.6f}")
