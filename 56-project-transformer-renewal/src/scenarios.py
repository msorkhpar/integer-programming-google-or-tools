"""Lesson 14.3.7: on 5,000 units, plans under four versions of the failure curves, a plan for their mean, and a plan
for their worst case, each valued under every version.

The fleet is generated (GridCap is fictional); the code is snapshot steps/07.
"""

from dataclasses import replace

import steps

steps.use(7)
from renewal.fleet import generate_fleet                # noqa: E402
from renewal.plan import plan                           # noqa: E402
from renewal.request import Request, Scenario           # noqa: E402
from renewal.risk import evaluate                       # noqa: E402

PILOT = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.005, outage_cost=300, outages=2,
                crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})
REQUEST = PILOT.scaled(10)                              # the 5,000-unit fleet, at a 0.5% gap
SCENARIOS = (Scenario("base", weight=2), Scenario("younger", eta=0.85), Scenario("older", eta=1.15),
             Scenario("steeper", beta=1.25))

fleet = generate_fleet(5000)
plans = {}
for s in SCENARIOS:
    plans[s.name] = plan(fleet, replace(REQUEST, scenarios=(s,)))
plans["expected"] = plan(fleet, replace(REQUEST, scenarios=SCENARIOS))
plans["worst case"] = plan(fleet, replace(REQUEST, scenarios=SCENARIOS, objective="worst"))
for name, got in plans.items():
    print(f"{name:10}: {len(got.replace):3} units, objective ${got.value:,.0f}k, "
          f"gap {(got.bound - got.value) / got.bound:.3%}, {got.status}")

value = {(p, s.name): evaluate(fleet, REQUEST, plans[p].replace, s) for p in plans for s in SCENARIOS}
print("risk removed ($k) by each plan (rows) if the fleet fails as in each scenario (columns):")
print("            " + "".join(f"{s.name:>10}" for s in SCENARIOS) + "  most regret")
for p in plans:
    regret = max(value[s.name, s.name] - value[p, s.name] for s in SCENARIOS)
    print(f"  {p:10}" + "".join(f"{value[p, s.name]:10,.0f}" for s in SCENARIOS) + f"  {regret:10,.0f}")

base = plans["base"].replace
every = set.intersection(*(set(plans[s.name].replace) for s in SCENARIOS))
some = set.union(*(set(plans[s.name].replace) for s in SCENARIOS))
print(f"units in every scenario's plan: {len(every)}; in some but not all: {len(some - every)}")
for p in plans:
    if p != "base":
        moved = {t for t in base.keys() | plans[p].replace.keys() if base.get(t) != plans[p].replace.get(t)}
        added = len(plans[p].replace.keys() - base.keys())
        print(f"  {p:10} against base: {len(moved):3} units placed differently, {added} added, "
              f"{len(base.keys() - plans[p].replace.keys())} dropped")

steps.show(7)
