"""Lesson 6.3.3: covers of GridCap tiny's budget row, and the LP point they cut off.

GridCap is a fictional utility's portfolio. The must-do project is paid for first, as in lesson 3.2.4.
"""

import itertools

from gridcap import generate
from knapsack_models import capital_row, discretionary, knapsack_model, solve_highs
from covers import is_cover

tiny = generate("tiny")
row = capital_row(tiny)
values = {p.project_id: p.value for p in discretionary(tiny)}
print(f"budget row: {' + '.join(f'{w} x_{i}' for i, w in row.weight.items())} <= {row.capacity}")

names = list(row.weight)
covers = [list(c) for n in range(1, len(names) + 1) for c in itertools.combinations(names, n) if is_cover(row, list(c))]
minimal = [c for c in covers if not any(is_cover(row, [j for j in c if j != i]) for i in c)]
print(f"{len(covers)} covers, {len(minimal)} of them minimal:")
for c in minimal:
    print(f"  {{{', '.join(c)}}} weighs {sum(row.weight[i] for i in c):,}: at most {len(c) - 1} of them")

model, x = knapsack_model(values, [row], integer=False)
added = 0
while True:
    result = solve_highs(model)
    xstar = {i: result.variable_values(v) for i, v in x.items()}
    shown = ", ".join(f"{i} {v:.3f}" for i, v in xstar.items() if v > 1e-6)
    print(f"LP bound {result.objective_value():,.2f}: {shown}")
    broken = [c for c in minimal if sum(xstar[i] for i in c) > len(c) - 1 + 1e-6]
    if not broken:
        break
    c = max(broken, key=lambda c: sum(xstar[i] for i in c) - (len(c) - 1))
    print(f"  cut: {' + '.join(f'x_{i}' for i in c)} <= {len(c) - 1}  (LP point gives {sum(xstar[i] for i in c):.3f})")
    model.add_linear_constraint(sum(x[i] for i in c) <= len(c) - 1, name=f"cover_{added}")
    added += 1

model, x = knapsack_model(values, [row])
print(f"best whole plan: {solve_highs(model).objective_value():,.0f}")
