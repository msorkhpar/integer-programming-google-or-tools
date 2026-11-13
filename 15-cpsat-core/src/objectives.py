"""Lesson 4.4.3: the objective, its bound, and what OPTIMAL means when a gap limit is set.

GridCap is a fictional utility's portfolio; the model is lesson 4.4.1's selection on GridCap medium.
"""

from gridcap import generate
from cpsat_models import one_worker, selection

medium = generate("medium")
sel = selection(medium, native=True)
print("has objective:", sel.model.has_objective())

for gap in (0.0, 0.001, 0.01):
    solver = one_worker()
    solver.parameters.relative_gap_limit = gap
    status = solver.solve(sel.model)
    objective, bound = solver.objective_value, solver.best_objective_bound
    print(f"relative_gap_limit {gap:<6} {solver.status_name(status)}  objective {objective:,.0f}"
          f"  bound {bound:,.0f}  gap {(bound - objective) / objective:.3%}")

# A second call replaces the objective: now the fewest projects that still meet every rule.
sel.model.minimize(sum(sel.x.values()))
solver = one_worker()
status = solver.solve(sel.model)
print(f"after minimize(): {solver.status_name(status)}  objective {solver.objective_value:,.0f}"
      f"  (must-do projects: {sum(p.must_do for p in medium.projects)})")
