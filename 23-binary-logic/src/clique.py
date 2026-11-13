"""Lesson 6.1.3: "at most one of these" as one row, or as one row per pair.

GridCap is a fictional utility's portfolio. The invented rule: the Valley transmission line can be
taken out once in the plan, so at most one Valley transmission project may be funded. Both forms
allow the same 0/1 plans; their LP relaxations (solved with GLOP) differ.
"""

import itertools

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection_model import EXACT, build, ids, solve_highs

small = generate("small")
valley = ids(small, program="transmission", region="Valley")


def at_most_one(sel, form: str) -> int:
    x = sel.x
    if form == "one row":
        sel.model.add_linear_constraint(sum(x[i] for i in valley) <= 1, name="valley_line")
        return 1
    pairs = list(itertools.combinations(valley, 2))
    for a, b in pairs:
        sel.model.add_linear_constraint(x[a] + x[b] <= 1, name=f"valley_{a}_{b}")
    return len(pairs)


print(f"Valley transmission projects: {valley}")
for form in ("one row", "pairs"):
    lp = build(small, integer=False)
    rows = at_most_one(lp, form)
    relaxed = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    shares = {i: round(relaxed.variable_values(lp.x[i]), 3) for i in valley if relaxed.variable_values(lp.x[i]) > 1e-6}
    milp = build(small)
    at_most_one(milp, form)
    best = solve_highs(milp.model, EXACT).objective_value()
    print(f"{form:8} {rows:2} row{'s' if rows != 1 else ' '}  LP bound ${relaxed.objective_value():,.2f}k  MILP ${best:,.0f}k  "
          f"gap ${relaxed.objective_value() - best:,.2f}k")
    print(f"         LP shares of the Valley projects: {shares}, sum {sum(shares.values()):.3f}")
