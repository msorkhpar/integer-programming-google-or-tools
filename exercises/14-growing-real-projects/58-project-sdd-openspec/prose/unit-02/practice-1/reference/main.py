"""Run: a three-year capital plan with a Plains share, and a strict check of the project's specs.

The portfolio is GridCap's and invented: 12 projects drawn by capplan/portfolio.py from seed 58. The
request is scaled down to its size, so the solve is quick. Nothing is read from the working
directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from pathlib import Path

from capplan.plan import plan
from capplan.portfolio import generate
from capplan.report import share_by_year, spend_by_year
from capplan.request import Request
from specs_check import passes, requirements, sections, validate

PROJECTS, SEED = 12, 58
REQUEST = Request(budget=1_500, years=3, shares={"plains": 25})


def main() -> None:
    projects = generate(PROJECTS, seed=SEED, years=REQUEST.years)
    print(f"portfolio: {PROJECTS} fictional projects, seed {SEED}; budget ${REQUEST.budget:,}k a year")
    got = plan(projects, REQUEST)
    print(f"{len(got.starts)} projects started, value ${got.value:,}k ({got.status})")
    plains = share_by_year(projects, got.starts, "plains")
    for year, spend in spend_by_year(projects, got.starts).items():
        starts = sorted(pid for pid, y in got.starts.items() if y == year)
        print(f"  {year}: {len(starts)} starts, ${spend:,}k, plains {plains[year]:.0f}%  {' '.join(starts)}")
    root = Path(__file__).resolve().parent
    specs = sorted((root / "openspec" / "specs").glob("*/spec.md"))
    reqs = [r for spec in specs for r in requirements(dict(sections(spec.read_text(encoding="utf-8")))["Requirements"])]
    verdict = "passed" if all(passes(issues) for issues in validate(root).values()) else "FAILED"
    print(f"openspec: {len(specs)} specs, {len(reqs)} requirements, "
          f"{sum(len(r.scenarios) for r in reqs)} scenarios; strict validation {verdict}")


if __name__ == "__main__":
    main()
