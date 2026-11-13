"""Lesson 7.1.1: how one capital addition reaches customers' rates, year by year, under cost-of-service rules.

The formula is the textbook one (rate base x rate of return + operating expenses), with straight-line
depreciation and the average of each year's opening and closing net plant as the rate base. The
numbers (a $5,310k addition, a 30-year book life, a 7.5% allowed return) are invented for the lesson
and describe no real utility or rate case; taxes, working capital and O&M are left out.
"""

COST = 5_310          # $k placed in service at the start of year 1
LIFE = 30             # years of straight-line depreciation
RETURN = 0.075        # allowed rate of return on rate base


def schedule(cost: int, life: int, rate: float) -> list[tuple[int, float, float, float, float]]:
    """(year, average rate base, depreciation, return, revenue requirement) for each year of the life."""
    rows = []
    depreciation = cost / life
    net = float(cost)
    for year in range(1, life + 1):
        closing = net - depreciation
        rate_base = (net + closing) / 2
        earned = rate * rate_base
        rows.append((year, rate_base, depreciation, earned, depreciation + earned))
        net = closing
    return rows


rows = schedule(COST, LIFE, RETURN)
print(f"capital addition ${COST:,}k, book life {LIFE} years, allowed return {RETURN:.1%}")
print("year  rate base  depreciation  return  revenue requirement")
for year, base, dep, ret, req in rows:
    if year in (1, 2, 3, 10, 20, 30):
        print(f"{year:4} {base:10,.0f} {dep:13,.0f} {ret:7,.0f} {req:20,.0f}")
total = sum(r[4] for r in rows)
print(f"collected over {LIFE} years: ${total:,.0f}k  (capital ${COST:,}k, return ${total - COST:,.0f}k)")
print(f"the same ${COST:,}k as an operating expense: ${COST:,}k in the test year, no return")
