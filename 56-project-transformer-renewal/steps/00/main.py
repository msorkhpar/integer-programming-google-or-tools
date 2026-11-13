"""Run: this year's replacement list for a tiny fleet, and what it removes.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56, with
a budget scaled down to its size. Nothing is read from the working directory, so the report is the
same wherever Run starts.
"""

from __future__ import annotations

from renewal.fleet import generate_fleet
from renewal.rank import worst_first
from renewal.report import summarize

UNITS, SEED, BUDGET = 25, 56, 2_000      # $k this year


def main() -> None:
    fleet = generate_fleet(UNITS, seed=SEED)
    print(f"fleet: {UNITS} fictional transformers, seed {SEED}; budget ${BUDGET:,}k in 2027")
    s = summarize(fleet, worst_first(fleet, BUDGET))
    print(f"worst first: {s.units} units, ${s.spend:,}k, risk removed ${s.risk_removed:,.0f}k")


if __name__ == "__main__":
    main()
