"""NPV of one project's cash flow, by hand and with numpy-financial, and the end-of-year variant.

The project is invented for this lesson: a feeder undergrounding that costs $1,200k in 2027 and
saves $180k of outage and repair cost in each of the ten years 2028-2037.
"""

import numpy_financial as npf

from finance import present_value

rate = 0.07
flows = {2027: -1_200, **{y: 180 for y in range(2028, 2038)}}
values = [flows[y] for y in sorted(flows)]

by_hand = present_value(flows, rate, 2027)
print(f"undiscounted sum       {sum(values):>9,.2f}")
print(f"NPV at 2027, by hand   {by_hand:>9,.2f}")
print(f"npf.npv(0.07, values)  {npf.npv(rate, values):>9,.2f}")

# The same flows one year later on the clock: every amount paid at the end of its year.
end_of_year = npf.npv(rate, [0] + values)
print(f"each flow a year later {end_of_year:>9,.2f}  (= {by_hand:,.2f} / 1.07 = {by_hand / 1.07:,.2f})")
