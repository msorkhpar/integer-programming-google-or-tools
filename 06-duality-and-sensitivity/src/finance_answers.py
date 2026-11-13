"""Lesson 2.3.4: turn prices into answers a finance partner can use, and check each one by re-solving."""

from budget_lp import build, clean, solve_glop, work_per_crew_month
from gridcap import generate

tiny = generate("tiny")
lp = build(tiny)
result = solve_glop(lp.model)
base = result.objective_value()
price_2028 = result.dual_values(lp.cash[2028])
print(f"plan value {base:,.1f}; 2028 cash price {clean(price_2028)}")

for extra in (500, 6000):
    lp_more = build(tiny, budget={**tiny.budget, 2028: tiny.budget[2028] + extra})
    actual = solve_glop(lp_more.model).objective_value() - base
    print(f"2028 budget +{extra:,}: price x amount says +{price_2028 * extra:,.1f}, re-solve gives +{actual:,.1f}")

floor_price = result.dual_values(lp.floor)
without = solve_glop(build(tiny, floor=None).model).objective_value()
print(f"vegetation floor of 900: price {clean(floor_price)} x 900 says {floor_price * 900:,.1f}; "
      f"dropping the floor gives +{without - base:,.1f}")

k = work_per_crew_month(tiny)
print(f"{'crew row':24} {'price per $k':>12} {'$k per crew-month':>18} {'value of a crew-month':>22}")
for y in tiny.years:
    for g in ("distribution", "vegetation"):
        row = lp.crew[g, y]
        price = result.dual_values(row)
        print(f"{row.name:24} {clean(price):>12} {k[g]:>18} {clean(price * k[g], 1):>22}")
