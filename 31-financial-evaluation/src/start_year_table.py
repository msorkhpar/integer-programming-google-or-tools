"""P022's NPV for each start year, built from its cash flows, beside the value GridCap stores."""

from finance import discount_factor, present_value, start_year_flows
from coefficients import gridcap_benefits
from gridcap_assumptions import benefit_assumptions

small, assumptions = benefit_assumptions("small")
p = small.project("P022")
ratio, decay = assumptions["P022"]
benefits_for = gridcap_benefits(p, ratio, decay)
rate, valuation = small.discount_rate, small.years[0]
print(f"P022 costs {p.cost_profile}, starts {list(p.starts())}, benefit ratio {ratio:.4f}, decay {decay:.4f}")
print("start  benefit  PV benefit  PV cost   NPV      stored")
for t in p.starts():
    benefit = benefits_for(t)[0]
    pv_benefit = benefit * discount_factor(rate, t - valuation)
    pv_cost = -present_value(start_year_flows(p.cost_profile, {}, t), rate, valuation)
    npv = present_value(start_year_flows(p.cost_profile, benefits_for(t), t), rate, valuation)
    print(f"{t}  {benefit:>7.1f}  {pv_benefit:>10.1f}  {pv_cost:>7.1f}  {npv:>7.1f}  {p.npv[t]:>6}")
print("cash flow if P022 starts in 2028:",
      {y: round(a, 1) for y, a in sorted(start_year_flows(p.cost_profile, benefits_for(2028), 2028).items())})
