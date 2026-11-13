"""Run: the five-year plan for a tiny fleet, its LP bound under both outage links,
the checker's verdict, and a rolling-horizon plan.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56. The
request's limits are scaled down to its size and its gap is loose, so the solve is quick. Nothing
is read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from dataclasses import replace

from renewal.check import violations
from renewal.fleet import Transformer, generate_fleet
from renewal.plan import lp_bound, plan
from renewal.report import outages, spend_by_year
from renewal.request import Plan, Request
from renewal.rolling import rolling

UNITS, SEED = 25, 56
REQUEST = Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
                  crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})


def show_plan(fleet: list[Transformer], got: Plan) -> None:
    print(f"{len(got.replace)} units replaced, risk removed ${got.value:,.0f}k ({got.status})")
    taken = outages(fleet, got.replace)
    for y, spend in spend_by_year(fleet, got.replace, REQUEST.outage_cost).items():
        units = sum(1 for year in got.replace.values() if year == y)
        print(f"  {y}: {units} units, {sum(1 for _, t in taken if t == y)} outages, ${spend:,}k")


def main() -> None:
    fleet = generate_fleet(UNITS, seed=SEED)
    print(f"fleet: {UNITS} fictional transformers, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    weak, strong = lp_bound(fleet, replace(REQUEST, link="aggregated")), lp_bound(fleet, REQUEST)
    print(f"LP bound: aggregated outage rows ${weak:,.0f}k, per-unit rows ${strong:,.0f}k")
    got = plan(fleet, REQUEST)
    show_plan(fleet, got)
    print(f"rules broken: {len(violations(fleet, REQUEST, got.replace))}")
    roll = rolling(fleet, REQUEST, window=2, keep=1)
    print(f"rolling, window 2 keep 1: {len(roll.replace)} units, risk removed ${roll.value:,.0f}k, "
          f"rules broken {len(violations(fleet, REQUEST, roll.replace))}")


if __name__ == "__main__":
    main()
