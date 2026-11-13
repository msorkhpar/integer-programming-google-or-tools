"""Lesson 6.3.1: with several capacity rows, no single value-per-cost ratio ranks the projects.

Three greedy rules fill the multi-dimensional knapsack of GridCap small, and are compared with the
optimum and with the LP relaxation. GridCap is a fictional utility's portfolio.
"""

from gridcap import generate
from knapsack_models import EXACT, capital_row, discretionary, knapsack_model, solve_highs, year_rows

small = generate("small")
projects = discretionary(small)
rows = [capital_row(small)] + year_rows(small)


def greedy(score) -> tuple[int, int]:
    """Take projects best score first, each one only if it still fits every row."""
    left = {row.name: row.capacity for row in rows}
    value = count = 0
    for p in sorted(projects, key=score, reverse=True):
        if all(row.weight.get(p.project_id, 0) <= left[row.name] for row in rows):
            for row in rows:
                left[row.name] -= row.weight.get(p.project_id, 0)
            value, count = value + p.value, count + 1
    return value, count


def scaled_use(p) -> float:
    """The share of each row's capacity the project uses, added up over the rows."""
    return sum(row.weight.get(p.project_id, 0) / row.capacity for row in rows)


rules = {
    "value / capex": lambda p: p.value / p.capex,
    "value / first-year spend": lambda p: p.value / p.cost_profile[0],
    "value / scaled use of all rows": lambda p: p.value / scaled_use(p),
}
values = {p.project_id: p.value for p in projects}
model, x = knapsack_model(values, rows)
optimum = solve_highs(model, EXACT).objective_value()
for name, score in rules.items():
    value, count = greedy(score)
    print(f"greedy by {name:<31} ${value:,}k with {count} projects ({value - optimum:+,.0f})")
print(f"optimum                                  ${optimum:,.0f}k")

model, x = knapsack_model(values, rows, integer=False)
result = solve_highs(model)
fractional = {i: result.variable_values(v) for i, v in x.items() if 1e-6 < result.variable_values(v) < 1 - 1e-6}
print(f"LP relaxation ${result.objective_value():,.2f}k; {len(fractional)} fractional projects, {len(rows)} rows:")
print("  " + ", ".join(f"{i} {v:.3f}" for i, v in fractional.items()))
