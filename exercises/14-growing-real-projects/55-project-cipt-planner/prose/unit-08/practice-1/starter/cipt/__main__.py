"""python -m cipt EXPORT.json [--why PROJECT]: plan the export and print the report."""

from __future__ import annotations

import argparse

from .data import read_request
from .diagnose import why_deferred, why_infeasible
from .report import render
from .solve import solve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cipt", description="Plan a capital portfolio.")
    parser.add_argument("export", help="the planning export, a JSON file")
    parser.add_argument("--why", metavar="PROJECT", help="explain why PROJECT was not funded")
    args = parser.parse_args(argv)
    request = read_request(args.export)
    plan = solve(request)
    print(render(request, plan))
    if plan.status == "infeasible":
        print(why_infeasible(request).message)
        return 1
    if args.why and args.why not in plan.starts:
        d = why_deferred(request, plan, args.why)
        if d.conflict:
            print(f"{args.why} cannot be funded. {d.conflict.message}")
        else:
            print(f"Funding {args.why} costs ${d.npv_cost:,.0f}k of NPV and drops {', '.join(d.displaced) or 'nothing'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
