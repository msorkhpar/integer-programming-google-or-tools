"""Every tiny project's benefit in four measures, and how differently each measure ranks them."""

from benefits import earliest_measures
from gridcap import generate
from value_function import MEASURES, ranking

tiny = generate("tiny")
table = earliest_measures(tiny)
print("project kind         action      failures   cust-min  SAIDI  incidents  tCO2e  NPV $k")
for pid, m in table.items():
    p = tiny.project(pid)
    print(f"{pid}    {tiny.asset(p.asset_id).kind:12} {p.intervention:10} {m.failures:8.3f} {m.customer_minutes:10,.0f}"
          f" {m.saidi:6.2f} {m.incidents:10.3f} {m.tco2e:6.2f} {m.npv:7,}")

print()
for name, (field, unit) in MEASURES.items():
    order = ranking({pid: getattr(m, field) for pid, m in table.items()})
    print(f"best by {name:13} {"(" + unit + ")":18}: {' '.join(order)}")
