"""This lesson's selection model against lesson 3.3.2's: the same rows, plus budget rows for years 6 to 10."""

import math

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

medium = generate("medium")
sel = build(medium)
years = sorted(sel.budget)
print(f"plan years {years[0]}-{years[-1]}: {len(years)} budget rows, {len(list(sel.model.linear_constraints()))} rows in all")

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)   # prove each optimum, no 0.01% stop
result = solve_highs(sel.model, EXACT)
print(f"every year capped (this lesson):         optimum {result.objective_value():,.0f}")

for y in years[5:]:
    sel.budget[y].upper_bound = math.inf     # drop the cap of years 6 to 10: lesson 3.3.2's model
first_five = solve_highs(sel.model, EXACT)
print(f"first five years capped (lesson 3.3.2): optimum {first_five.objective_value():,.0f}")

print("lesson 3.3.2's plan, spend against the caps lesson 3.3.2 leaves out:")
values = first_five.variable_values()
for y in years[5:]:
    spent = sum(t.coefficient * values[t.variable] for t in sel.budget[y].terms())
    flag = "over" if spent > medium.budget[y] + 1e-6 else "within"
    print(f"  {y}  spend {spent:9,.0f}  budget {medium.budget[y]:9,}  {flag}")
