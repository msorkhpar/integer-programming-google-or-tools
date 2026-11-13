"""The command line: `renewal --units 500 --out plan.md` writes the finance report."""

from __future__ import annotations

import argparse
from dataclasses import replace

from .finance import finance_report
from .fleet import generate_fleet
from .plan import plan
from .request import Request
from .solve import FOUND_NAMES

#: The request for a 500-unit fleet; larger fleets scale every limit (Request.scaled).
REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02, outage_cost=300, outages=2,
                  crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="renewal", description=__doc__)
    parser.add_argument("--units", type=int, default=500, help="fleet size (fictional fleet)")
    parser.add_argument("--seed", type=int, default=2027, help="the fleet generator's seed")
    parser.add_argument("--budget", type=int, help="$k per year (default: 10,000 per 500 units)")
    parser.add_argument("--gap", type=float, help="stop within this share of the bound (default 0.02)")
    parser.add_argument("--out", help="write the report here instead of printing it")
    args = parser.parse_args(argv)
    request = REQUEST.scaled(max(1, args.units // 500))
    if args.budget is not None:
        request = replace(request, budget=args.budget)
    if args.gap is not None:
        request = replace(request, gap=args.gap)
    fleet = generate_fleet(args.units, seed=args.seed)
    got = plan(fleet, request)
    report = finance_report(fleet, request, got)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
    else:
        print(report, end="")
    return 0 if got.status in FOUND_NAMES else 2
