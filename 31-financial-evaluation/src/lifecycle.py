"""Lifecycle cost and equivalent annual cost of replacing or repairing one GridCap transformer.

The two options are invented for this lesson (GridCap stores no O&M costs or asset lives). Both
work on asset A006, a Valley substation transformer. All amounts in 2027 dollars, real rate 7%.
"""

import numpy_financial as npf

from finance import annuity_factor, equivalent_annual_cost, present_value

rate = 0.07
options = {
    # name: (capex now, O&M each year, life in years, {year of life: one-off cost})
    "replace": (1_970, 25, 40, {20: 300}),
    "repair": (290, 150, 10, {}),
}
print("option   life  capex  PV O&M  PV one-off  lifecycle  EAC     npf.pmt")
for name, (capex, om, life, one_off) in options.items():
    pv_om = om * annuity_factor(rate, life)
    pv_one_off = present_value(one_off, rate, 0)
    lcc = capex + pv_om + pv_one_off
    eac = equivalent_annual_cost(lcc, rate, life)
    print(f"{name:8} {life:>4}  {capex:>5}  {pv_om:>6.1f}  {pv_one_off:>10.1f}  {lcc:>9.1f}"
          f"  {eac:>6.1f}  {-npf.pmt(rate, life, lcc):>6.1f}")

# The same choice over one 40-year horizon: four repairs in a row, each like the first.
repair_lcc = 290 + 150 * annuity_factor(rate, 10)
chain = present_value({0: repair_lcc, 10: repair_lcc, 20: repair_lcc, 30: repair_lcc}, rate, 0)
replace_lcc = 1_970 + 25 * annuity_factor(rate, 40) + present_value({20: 300}, rate, 0)
print(f"over 40 years: four repairs {chain:.1f}, one replacement {replace_lcc:.1f}")
