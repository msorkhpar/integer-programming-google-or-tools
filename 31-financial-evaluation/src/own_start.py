"""The mistake of discounting each start to its own start year, on P022."""

from finance import present_value, start_year_flows
from coefficients import gridcap_benefits
from gridcap_assumptions import benefit_assumptions

small, assumptions = benefit_assumptions("small")
p = small.project("P022")
benefits_for = gridcap_benefits(p, *assumptions["P022"])
rate = small.discount_rate
print("start  to 2027   to own start")
for t in p.starts():
    flows = start_year_flows(p.cost_profile, benefits_for(t), t)
    print(f"{t}  {present_value(flows, rate, 2027):>8.1f}  {present_value(flows, rate, t):>12.1f}")

cost_only = {t: present_value(start_year_flows(p.cost_profile, {}, t), rate, t) for t in p.starts()}
print("cost alone, each to its own start:", {t: round(v, 1) for t, v in cost_only.items()})
