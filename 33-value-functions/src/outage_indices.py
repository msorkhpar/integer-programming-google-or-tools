"""SAIFI, SAIDI and CAIDI from one year's outage log, and one project's share of them."""

from benefits import CONSEQUENCE, CUSTOMERS_SERVED, Outage, failures_avoided, reliability_indices
from gridcap import generate

# A year of GridCap outages (invented): customers interrupted and minutes until restored.
log = [Outage(12_000, 240), Outage(4_000, 300), Outage(9_000, 3), Outage(1_500, 180),
       Outage(400, 360), Outage(6_000, 90), Outage(20_000, 2), Outage(1_200, 150)]
indices = reliability_indices(log, CUSTOMERS_SERVED)
print(f"customers served {CUSTOMERS_SERVED:,}; {len(log)} outages, "
      f"{sum(o.minutes <= 5 for o in log)} of them momentary")
print(f"SAIFI {indices['SAIFI']:.4f} interruptions per customer")
print(f"SAIDI {indices['SAIDI']:.2f} minutes per customer")
print(f"CAIDI {indices['CAIDI']:.1f} minutes per interrupted customer")

tiny = generate("tiny")
p = tiny.project("P003")
kind = tiny.asset(p.asset_id).kind
c = CONSEQUENCE[kind]
f = failures_avoided(tiny, p, p.earliest_start)
print(f"\n{p.project_id} {p.name}: {f:.3f} expected failures avoided")
print(f"  each cuts off {c.customers:,} customers for {c.minutes} minutes")
print(f"  customer interruptions avoided  {f * c.customers:,.0f}  -> SAIFI cut {f * c.customers / CUSTOMERS_SERVED:.4f}")
print(f"  customer-minutes avoided  {f * c.customers * c.minutes:,.0f}  -> SAIDI cut {f * c.customers * c.minutes / CUSTOMERS_SERVED:.2f}")
