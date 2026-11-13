"""python -m renewal: a ten-year replacement plan for a fictional 500-unit fleet, with outages, crews and spares."""

from .fleet import generate_fleet
from .plan import plan
from .report import outages, spend_by_year
from .request import Request

REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02, outage_cost=300, outages=2,
                  crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})

if __name__ == "__main__":
    fleet = generate_fleet(500)
    got = plan(fleet, REQUEST)
    print(f"{len(got.replace)} units replaced, risk removed ${got.value:,.0f}k "
          f"(bound ${got.bound:,.0f}k, {got.status})")
    taken = outages(fleet, got.replace)
    for y, spend in spend_by_year(fleet, got.replace, REQUEST.outage_cost).items():
        units = sum(1 for year in got.replace.values() if year == y)
        print(f"  {y}: {units:3} units, {sum(1 for _, t in taken if t == y):2} outages, ${spend:,}k")
