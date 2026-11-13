"""Run: this year's replacement list for a tiny fleet, by the ranking and by the model.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56, with
a budget scaled down to its size. Nothing is read from the working directory, so the report is the
same wherever Run starts.
"""

from __future__ import annotations

from renewal.fleet import generate_fleet
from renewal.plan import plan
from renewal.rank import worst_first
from renewal.report import summarize
from renewal.request import Request

UNITS, SEED, BUDGET = 25, 56, 2_000      # $k this year


def main() -> None:
    fleet = generate_fleet(UNITS, seed=SEED)
    print(f"fleet: {UNITS} fictional transformers, seed {SEED}; budget ${BUDGET:,}k in 2027")
    s = summarize(fleet, worst_first(fleet, BUDGET))
    print(f"worst first: {s.units} units, ${s.spend:,}k, risk removed ${s.risk_removed:,.0f}k")
    got = plan(fleet, Request(BUDGET))
    s = summarize(fleet, list(got.replace))
    print(f"model      : {s.units} units, ${s.spend:,}k, risk removed ${s.risk_removed:,.0f}k ({got.status})")


if __name__ == "__main__":
    main()
