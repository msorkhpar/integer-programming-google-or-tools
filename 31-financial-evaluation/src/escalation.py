"""Escalate P022's cost profile, quoted in 2027 prices, to the prices of the years it is paid in."""

from gridcap import generate

from finance import escalate

p = generate("small").project("P022")
price_year, e = 2027, 0.03
print(f"{p.project_id} cost profile in {price_year} dollars: {p.cost_profile}, total {p.capex:,}")
for start in p.starts():
    nominal = {start + k: escalate(c, e, start + k - price_year) for k, c in enumerate(p.cost_profile)}
    shown = ", ".join(f"{y}: {a:,.1f}" for y, a in nominal.items())
    print(f"start {start}: {shown}  total {sum(nominal.values()):,.1f}")
