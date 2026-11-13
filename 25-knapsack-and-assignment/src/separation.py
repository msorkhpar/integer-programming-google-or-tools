"""Lesson 6.3.3: finding the cover the LP point breaks most is a knapsack of its own.

The LP point is GridCap small's multi-dimensional knapsack relaxation (lesson 6.3.1). GridCap is a
fictional utility's portfolio.
"""

from gridcap import generate
from knapsack_models import capital_row, discretionary, knapsack_model, solve_highs, year_rows
from covers import extension, minimal, separate

small = generate("small")
rows = [capital_row(small)] + year_rows(small)
values = {p.project_id: p.value for p in discretionary(small)}
model, x = knapsack_model(values, rows, integer=False)
result = solve_highs(model)
xstar = {i: result.variable_values(v) for i, v in x.items()}
print(f"LP bound {result.objective_value():,.2f}")

for row in rows:
    cover, slack = separate(row, xstar)
    if not cover:
        print(f"{row.name}: no cover at all, every project on the row fits at once")
        continue
    if slack >= 1 - 1e-9:
        print(f"{row.name}: no broken cover (least sum of 1 - x* is {slack:.3f})")
        continue
    small_cover = minimal(row, cover, xstar)
    lhs = sum(xstar[i] for i in small_cover)
    print(f"{row.name}: cover of {len(cover)}, minimal {len(small_cover)}: {' '.join(small_cover)}")
    print(f"  LP point gives {lhs:.3f} > {len(small_cover) - 1}; extension adds {' '.join(extension(row, small_cover)) or '-'}")
