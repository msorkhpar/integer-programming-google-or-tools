"""Run: a three-year plan with a Plains share, a must-do and carry-over, a request that sets the retired
start cap, and a strict check of the specs.

The portfolio is GridCap's and invented: 12 projects drawn by capplan/portfolio.py from seed 58. The
request is scaled down to its size, so the solve is quick. Nothing is read from the working
directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from capplan.plan import plan
from capplan.portfolio import generate
from capplan.report import carry_by_year, overrides, share_by_year, spend_by_year
from capplan.request import Request
from specs_check import passes, requirements, sections, validate

PROJECTS, SEED = 12, 58
REQUEST = Request(budget=1_500, years=3, shares={"plains": 25},
                  must_do={"P010": "Storm damage on the Ridge line, inspection report IR-31"}, carry=20)


def main() -> None:
    projects = generate(PROJECTS, seed=SEED, years=REQUEST.years)
    print(f"portfolio: {PROJECTS} fictional projects, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    got = plan(projects, REQUEST)
    print(f"{len(got.starts)} projects started, value ${got.value:,}k ({got.status})")
    for line in overrides(REQUEST):
        print(f"  must-do {line}")
    plains = share_by_year(projects, got.starts, "plains")
    carried = carry_by_year(projects, got.starts, REQUEST)
    spend = spend_by_year(projects, got.starts)
    for year in REQUEST.plan_years():
        starts = sorted(pid for pid, y in got.starts.items() if y == year)
        print(f"  {year}: {len(starts)} starts, ${spend.get(year, 0):,}k, plains {plains.get(year, 0):.0f}%, "
              f"carries ${carried.get(year, 0):,}k  {' '.join(starts)}".rstrip())
    try:
        plan(projects, replace(REQUEST, max_starts=3))
        print("a request that sets max_starts=3: accepted")
    except ValueError as error:
        print(f"a request that sets max_starts=3: refused, {error}")
    root = Path(__file__).resolve().parent
    specs = sorted((root / "openspec" / "specs").glob("*/spec.md"))
    reqs = [r for spec in specs for r in requirements(dict(sections(spec.read_text(encoding="utf-8")))["Requirements"])]
    verdict = "passed" if all(passes(issues) for issues in validate(root).values()) else "FAILED"
    print(f"openspec: {len(specs)} specs, {len(reqs)} requirements, "
          f"{sum(len(r.scenarios) for r in reqs)} scenarios; strict validation {verdict}")


if __name__ == "__main__":
    main()
