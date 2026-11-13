"""Lesson 14.3.3: one outage per substation and year, its cost, and a limit per region and year.

The fleet is generated (GridCap is fictional); the code is snapshot steps/03.
"""

from collections import Counter
from dataclasses import replace

import steps

steps.use(3)
from renewal.fleet import generate_fleet                # noqa: E402
from renewal.plan import plan                           # noqa: E402
from renewal.report import outages, spend_by_year       # noqa: E402
from renewal.request import Request                     # noqa: E402

TEN_YEARS = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02)
REQUEST = replace(TEN_YEARS, outage_cost=300, outages=2)

fleet = generate_fleet(500)
region = {t.substation: t.region for t in fleet}


def describe(name, request, replace_):
    taken = outages(fleet, replace_)
    spend = spend_by_year(fleet, replace_, REQUEST.outage_cost)
    over = sum(1 for y in spend if spend[y] > REQUEST.budget)
    per_region = Counter((region[s], y) for s, y in taken)
    busiest = max(per_region.values())
    print(f"{name:22}: {len(replace_):3} units, {len(taken):3} outages ({len(replace_) / len(taken):.2f} units each), "
          f"years over budget {over}, most outages in a region-year {busiest}")


first = plan(fleet, TEN_YEARS)
describe("ten-year plan, costed", TEN_YEARS, first.replace)
costed = plan(fleet, replace(TEN_YEARS, outage_cost=300))
describe("outage cost only", replace(TEN_YEARS, outage_cost=300), costed.replace)
both = plan(fleet, REQUEST)
describe("cost and region limit", REQUEST, both.replace)
for name, got in (("ten-year plan", first), ("outage cost only", costed), ("cost and region limit", both)):
    print(f"{name:22}: risk removed ${got.value:,.0f}k (bound ${got.bound:,.0f}k, {got.status})")

steps.show(3)
