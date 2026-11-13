"""Run: plans for a tiny fleet under four versions of the failure curves, weighted
equally: one for their mean and one for their worst case, each valued under every version.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56. The
request's limits are scaled down to its size and its gap is loose, so the solve is quick. Nothing
is read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from dataclasses import replace

from renewal.fleet import Transformer, generate_fleet
from renewal.plan import plan
from renewal.report import outages, spend_by_year
from renewal.request import Plan, Request, Scenario
from renewal.risk import evaluate

UNITS, SEED = 25, 56
REQUEST = Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
                  crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})
#: Four versions of the curves, weighted equally.
SCENARIOS = (Scenario("base"), Scenario("younger", eta=0.85), Scenario("older", eta=1.15),
             Scenario("steeper", beta=1.25))


def show_plan(fleet: list[Transformer], got: Plan) -> None:
    print(f"{len(got.replace)} units replaced, risk removed ${got.value:,.0f}k ({got.status})")
    taken = outages(fleet, got.replace)
    for y, spend in spend_by_year(fleet, got.replace, REQUEST.outage_cost).items():
        units = sum(1 for year in got.replace.values() if year == y)
        print(f"  {y}: {units} units, {sum(1 for _, t in taken if t == y)} outages, ${spend:,}k")


def main() -> None:
    fleet = generate_fleet(UNITS, seed=SEED)
    print(f"fleet: {UNITS} fictional transformers, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    plans = {"expected": plan(fleet, replace(REQUEST, scenarios=SCENARIOS)),
             "worst case": plan(fleet, replace(REQUEST, scenarios=SCENARIOS, objective="worst"))}
    for name, got in plans.items():
        print(f"{name}:")
        show_plan(fleet, got)
    print("risk removed ($k) by each plan if the fleet fails as in each version:")
    print("            " + "".join(f"{s.name:>10}" for s in SCENARIOS))
    for name, got in plans.items():
        values = (evaluate(fleet, REQUEST, got.replace, s) for s in SCENARIOS)
        print(f"  {name:10}" + "".join(f"{v:10,.0f}" for v in values))


if __name__ == "__main__":
    main()
