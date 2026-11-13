"""Lesson 14.3.6: the aggregated and per-unit outage rows compared by size and LP bound.

The fleets are generated (GridCap is fictional); the code is snapshot steps/06. Everything printed
here is exact and repeats run to run; the timings of the lesson come from stronger_timing.py.
"""

from dataclasses import replace

import steps

steps.use(6)
from renewal.fleet import generate_fleet                # noqa: E402
from renewal.model import build                         # noqa: E402
from renewal.plan import lp_bound                       # noqa: E402
from renewal.request import Request                     # noqa: E402

REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02, outage_cost=300, outages=2,
                  crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})

for n in (500, 5000):
    fleet, request = generate_fleet(n), REQUEST.scaled(n // 500)
    print(f"{n} units:")
    bounds = {}
    for link in ("aggregated", "per-unit"):
        r = replace(request, link=link)
        model = build(fleet, r).model
        bounds[link] = lp_bound(fleet, r)
        print(f"  {link:10}: {model.get_num_variables():6} variables, {model.get_num_linear_constraints():6} rows, "
              f"LP bound ${bounds[link]:,.0f}k")
    print(f"  the per-unit LP bound is {1 - bounds['per-unit'] / bounds['aggregated']:.2%} lower")

steps.show(6)
