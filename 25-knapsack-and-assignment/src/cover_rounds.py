"""Lesson 6.3.3: rounds of cover cuts lower the LP bound of GridCap small's six-row knapsack.

Each round solves the LP, separates one cover per row, and adds every row the LP point breaks. The
whole plans are unchanged: the MILP with all the cuts has the same optimum. GridCap is fictional.
"""

from gridcap import generate
from knapsack_models import EXACT, capital_row, discretionary, knapsack_model, solve_highs, year_rows
from covers import extension, minimal, separate

small = generate("small")
rows = [capital_row(small)] + year_rows(small)
values = {p.project_id: p.value for p in discretionary(small)}
model, x = knapsack_model(values, rows)
optimum = solve_highs(model, EXACT).objective_value()


def cut_rounds(extend: bool) -> list[list[str]]:
    model, x = knapsack_model(values, rows, integer=False)
    cuts, bounds = [], []
    while True:
        result = solve_highs(model)
        bounds.append(result.objective_value())
        xstar = {i: result.variable_values(v) for i, v in x.items()}
        new = []
        for row in rows:
            cover, slack = separate(row, xstar)
            if slack >= 1 - 1e-9:
                continue
            cover = minimal(row, cover, xstar)
            left = cover + (extension(row, cover) if extend else [])
            if sum(xstar[i] for i in left) > len(cover) - 1 + 1e-6:
                new.append((left, len(cover) - 1))
        if not new:
            break
        for left, rhs in new:
            model.add_linear_constraint(sum(x[i] for i in left) <= rhs, name=f"cover_{len(cuts)}")
            cuts.append((left, rhs))
    gap = bounds[0] - optimum
    print(f"{'extended' if extend else 'plain'} covers: {len(bounds) - 1} rounds, {len(cuts)} cuts")
    print("  bound by round: " + " ".join(f"{b:,.0f}" for b in bounds))
    print(f"  root gap {gap:,.2f} -> {bounds[-1] - optimum:,.2f}: {(bounds[0] - bounds[-1]) / gap:.1%} of it closed")
    return cuts


print(f"best whole plan ${optimum:,.0f}k")
for extend in (False, True):
    cuts = cut_rounds(extend)
    model, x = knapsack_model(values, rows)
    for left, rhs in cuts:
        model.add_linear_constraint(sum(x[i] for i in left) <= rhs)
    print(f"  MILP with these cuts: ${solve_highs(model, EXACT).objective_value():,.0f}k")
