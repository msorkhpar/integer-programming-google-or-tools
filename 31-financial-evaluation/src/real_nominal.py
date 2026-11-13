"""Real flows at the real rate equal nominal flows at the nominal rate; the two mixes do not.

P022 (GridCap small) started in 2028, its costs quoted in 2027 dollars. Inflation is 2.5% and
the real discount rate 4%; both numbers are assumptions for this lesson.
"""

from gridcap import generate

from finance import escalate, present_value, real_rate

p = generate("small").project("P022")
inflation, real = 0.025, 0.04
nominal = (1 + real) * (1 + inflation) - 1
print(f"nominal rate {nominal:.4%} (the sum {real + inflation:.4%} is the approximation)")
print(f"real rate back from nominal: {real_rate(nominal, inflation):.4%}")

start, price_year = 2028, 2027
real_flows = {start + k: -c for k, c in enumerate(p.cost_profile)}
nominal_flows = {y: escalate(a, inflation, y - price_year) for y, a in real_flows.items()}
cases = [("real flows,    real rate   ", real_flows, real),
         ("nominal flows, nominal rate", nominal_flows, nominal),
         ("nominal flows, real rate   ", nominal_flows, real),
         ("real flows,    nominal rate", real_flows, nominal),
         ("nominal flows, approx rate ", nominal_flows, real + inflation)]
for label, flows, rate in cases:
    print(f"{label}  PV {present_value(flows, rate, price_year):>9,.2f}")

labour = 0.045
print(f"labour escalating {labour:.1%} with inflation {inflation:.1%}: "
      f"real escalation {real_rate(labour, inflation):.4%}")
