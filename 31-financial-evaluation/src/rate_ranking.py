"""Two invented projects whose NPV ranking depends on the discount rate.

Both cost $500k now. The circuit clearing pays back fast and stops; the undergrounding pays a
little each year for twenty years.
"""

import numpy_financial as npf

clearing = [-500] + [150] * 5
undergrounding = [-500] + [60] * 20

print("rate   clearing  undergrounding  better")
for rate in (0.00, 0.03, 0.05, 0.07, 0.10):
    a, b = npf.npv(rate, clearing), npf.npv(rate, undergrounding)
    print(f"{rate:4.0%}  {a:>9.1f}  {b:>14.1f}  {'clearing' if a > b else 'undergrounding'}")

print(f"IRR clearing       {npf.irr(clearing):.4f}")
print(f"IRR undergrounding {npf.irr(undergrounding):.4f}")
difference = [a - b for a, b in zip(clearing + [0] * 15, undergrounding)]
print(f"crossover rate     {npf.irr(difference):.4f}")
