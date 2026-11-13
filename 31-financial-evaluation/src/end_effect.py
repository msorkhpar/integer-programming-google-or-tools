"""Cutting a benefit stream at the end of the plan makes every later start look worse.

An invented mains relining: $600k in each of two years of work, then $120k a year of avoided
breaks for a 25-year life. The plan runs 2027-2031; the valuation date is the start of 2027.
"""

from finance import present_value, start_year_flows

rate, plan_end, life = 0.07, 2031, 25
costs = (600, 600)
print("start  full life  cut at 2031  benefit years counted")
for t in (2027, 2028, 2029, 2030):
    benefits = {k: 120 for k in range(len(costs), len(costs) + life)}
    full = start_year_flows(costs, benefits, t)
    cut = {y: a for y, a in full.items() if y <= plan_end}
    counted = sum(1 for k in benefits if t + k <= plan_end)
    print(f"{t}  {present_value(full, rate, 2027):>9.1f}  {present_value(cut, rate, 2027):>11.1f}  {counted:>4} of {life}")
