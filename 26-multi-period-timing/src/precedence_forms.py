"""Two ways to write "the child starts at least `lag` years after its parent", compared by LP bound."""

from dataclasses import replace

from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build

small = generate("small")
# Scenario: a rate case freezes the first two years' budgets.
frozen = replace(small, budget={y: (0 if y in small.years[:2] else v) for y, v in small.budget.items()})
child = frozen.project("P023")
print(f"P023 needs {child.parent} with lag {child.parent_lag}; P023 may start {list(child.starts())}, "
      f"P022 may start {list(frozen.project('P022').starts())}")

exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)
for form in ("aggregated", "cumulative"):
    lp = build(frozen, integer=False, precedence=form)
    relaxed = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    milp = mathopt.solve(build(frozen, precedence=form).model, mathopt.SolverType.HIGHS, params=exact)
    rows = sum(1 for c in lp.model.linear_constraints() if c.name.startswith(("after_", "needs_")))
    print(f"{form:10} precedence rows {rows}  LP bound {relaxed.objective_value():,.1f}  MILP {milp.objective_value():,.1f}")
    print("           P022", {t: round(relaxed.variable_values(lp.x["P022", t]), 3) for t in (2027, 2028, 2029)},
          " P023", {2029: round(relaxed.variable_values(lp.x["P023", 2029]), 3)})
