"""Run: a five-year replacement plan for a tiny fleet.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56. The
request's limits are scaled down to its size and its gap is loose, so the solve is quick. Nothing
is read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from renewal.fleet import generate_fleet
from renewal.plan import plan
from renewal.report import spend_by_year
from renewal.request import Request

UNITS, SEED = 25, 56
REQUEST = Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02)


def main() -> None:
    fleet = generate_fleet(UNITS, seed=SEED)
    print(f"fleet: {UNITS} fictional transformers, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    got = plan(fleet, REQUEST)
    print(f"{len(got.replace)} units replaced, risk removed ${got.value:,.0f}k ({got.status})")
    for y, spend in spend_by_year(fleet, got.replace).items():
        units = sum(1 for year in got.replace.values() if year == y)
        print(f"  {y}: {units} units, ${spend:,}k")


if __name__ == "__main__":
    main()
