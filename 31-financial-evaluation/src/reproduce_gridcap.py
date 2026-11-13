"""Rebuild GridCap's whole NPV table from cash flows and compare it, entry by entry, with the stored one.

The cost side is checked once more against numpy-financial: each start's costs are laid on a
calendar-year array from the first plan year and discounted with npf.npv.
"""

import numpy_financial as npf

from finance import present_value, start_year_flows
from coefficients import coefficient_table
from gridcap_assumptions import benefit_assumptions

for size in ("tiny", "small", "medium"):
    portfolio, assumptions = benefit_assumptions(size)
    table = coefficient_table(portfolio, assumptions, portfolio.discount_rate)
    stored = {(p.project_id, t): v for p in portfolio.projects for t, v in p.npv.items()}
    wrong = [k for k in stored if table.get(k) != stored[k]]
    first, worst = portfolio.years[0], 0.0
    for p in portfolio.projects:
        for t in p.starts():
            values = [0.0] * (t - first) + [-c for c in p.cost_profile]
            ours = present_value(start_year_flows(p.cost_profile, {}, t), portfolio.discount_rate, first)
            worst = max(worst, abs(ours - npf.npv(portfolio.discount_rate, values)))
    print(f"{size:6}  entries {len(stored):>4}  rebuilt {len(table):>4}  different {len(wrong)}"
          f"  cost PV vs npf.npv: largest gap {worst:.1e}")
