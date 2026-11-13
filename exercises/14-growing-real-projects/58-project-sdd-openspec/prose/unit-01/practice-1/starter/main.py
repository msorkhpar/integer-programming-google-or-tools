"""Run: a three-year capital plan for a tiny portfolio.

The portfolio is GridCap's and invented: 12 projects drawn by capplan/portfolio.py from seed 58. The
request is scaled down to its size, so the solve is quick. Nothing is read from the working
directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from capplan.plan import plan
from capplan.portfolio import generate
from capplan.report import spend_by_year
from capplan.request import Request

PROJECTS, SEED = 12, 58
REQUEST = Request(budget=1_500, years=3)


def main() -> None:
    projects = generate(PROJECTS, seed=SEED, years=REQUEST.years)
    print(f"portfolio: {PROJECTS} fictional projects, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    got = plan(projects, REQUEST)
    print(f"{len(got.starts)} projects started, value ${got.value:,}k ({got.status})")
    for year, spend in spend_by_year(projects, got.starts).items():
        starts = sorted(pid for pid, y in got.starts.items() if y == year)
        print(f"  {year}: {len(starts)} starts, ${spend:,}k  {' '.join(starts)}")


if __name__ == "__main__":
    main()
