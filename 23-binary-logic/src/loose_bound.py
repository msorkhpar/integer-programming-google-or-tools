"""Lesson 6.1.4: the bound written into the product rows decides the LP bound, and a wrong one the answer.

GridCap is a fictional utility's portfolio. The clearance-width model of clearance_width.py is solved
as an LP relaxation (GLOP) and as a MILP (HiGHS) with different values of the width's upper bound in
the rows: the true 6 metres, looser values, and one below the true bound.
"""

from ortools.math_opt.python import mathopt

from clearance_width import width_model
from gridcap import generate
from selection_model import EXACT, solve_highs

small = generate("small")
print("bound in rows | LP bound     | MILP        | q in the MILP")
for high in (6.0, 60.0, 600.0, 5.0):
    sel, q, w = width_model(small, integer=False, high_in_rows=high)
    lp = mathopt.solve(sel.model, mathopt.SolverType.GLOP)
    sel, q, w = width_model(small, high_in_rows=high)
    milp = solve_highs(sel.model, EXACT)
    print(f"{high:13.0f} | ${lp.objective_value():,.2f}k | ${milp.objective_value():,.1f}k | "
          f"{milp.variable_values(q):.3f}")

sel, q, w = width_model(small, integer=False, high_in_rows=60.0)
lp = mathopt.solve(sel.model, mathopt.SolverType.GLOP)
fractional = {i: (round(lp.variable_values(sel.x[i]), 3), round(lp.variable_values(w[i]), 2))
              for i in w if 1e-6 < lp.variable_values(sel.x[i]) < 1 - 1e-6}
print("bound 60, LP's fractional vegetation projects (x, w):", fractional)
