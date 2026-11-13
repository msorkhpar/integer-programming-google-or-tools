"""Lesson 6.1.4: a product of two binaries in the objective, as written and as rows HiGHS accepts.

GridCap is a fictional utility's portfolio. The invented bonus: two distribution projects in the
same region, funded together, share one crew mobilization, which planners value at $150k.
"""

import itertools

from ortools.math_opt.python import mathopt

from gridcap import REGIONS, generate
from selection_model import EXACT, build, ids, solve_highs

small = generate("small")
BONUS = 150
pairs = [pair for r in REGIONS for pair in itertools.combinations(ids(small, program="distribution", region=r), 2)]
print(f"{len(pairs)} pairs of same-region distribution projects")

sel = build(small)
npv = sel.model.objective.as_linear_expression()
sel.model.maximize(npv + sum(BONUS * sel.x[a] * sel.x[b] for a, b in pairs))
try:
    solve_highs(sel.model, EXACT)
except Exception as error:                    # OR-Tools 9.15 hides the reason in __context__
    print("HiGHS, product in the objective:", error.__context__)
scip = mathopt.solve(sel.model, mathopt.SolverType.GSCIP, params=EXACT)
print(f"SCIP, product in the objective: {scip.termination.reason.name}, ${scip.objective_value():,.0f}k")

lin = build(small)
model, x = lin.model, lin.x
z = {}
for a, b in pairs:
    z[a, b] = model.add_binary_variable(name=f"z_{a}_{b}")
    model.add_linear_constraint(z[a, b] <= x[a], name=f"z_le_{a}_{b}")
    model.add_linear_constraint(z[a, b] <= x[b], name=f"z_le_{b}_{a}")
    model.add_linear_constraint(z[a, b] >= x[a] + x[b] - 1, name=f"z_ge_{a}_{b}")
model.maximize(model.objective.as_linear_expression() + sum(BONUS * v for v in z.values()))
result = solve_highs(model, EXACT)
together = [pair for pair, v in z.items() if result.variable_values(v) > 0.5]
print(f"HiGHS, product replaced by z: {result.termination.reason.name}, ${result.objective_value():,.0f}k, "
      f"{len(together)} pairs funded together")
