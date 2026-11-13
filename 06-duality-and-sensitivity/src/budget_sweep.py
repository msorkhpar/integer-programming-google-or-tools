"""Lesson 2.3.3: a shadow price is a slope that holds over a range. Sweep the 2028 budget."""

from budget_lp import build, clean, solve_glop
from gridcap import generate

tiny = generate("tiny")
print(f"{'2028 budget':>11} {'value':>9} {'price':>7}  {'transm. 2028':>12} {'carry 2028':>10}")
for b in (2750, 2979, 2980, 3280, 5000, 8140, 8500, 9750):
    lp = build(tiny, budget={**tiny.budget, 2028: b})
    result = solve_glop(lp.model)
    print(f"{b:>11,} {result.objective_value():>9,.1f} {clean(result.dual_values(lp.cash[2028])):>7}  "
          f"{clean(result.variable_values(lp.spend['transmission', 2028]), 1):>12} "
          f"{clean(result.variable_values(lp.carry[2028]), 1):>10}")
