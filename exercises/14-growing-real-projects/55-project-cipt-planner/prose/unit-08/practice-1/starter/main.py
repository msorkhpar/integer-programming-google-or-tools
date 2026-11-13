"""Run: plan the demo export, print the planners' report, why P003 was deferred, the trade
between NPV and risk, and what $1,000k more in 2028 and 2029 would change.

data/demo.json is GridCap tiny, a fictional utility's portfolio. Its path is taken from this
file's folder, never from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from pathlib import Path

from cipt.__main__ import main
from cipt.data import read_request
from cipt.goals import frontier
from cipt.scenario import Scenario, apply, diff
from cipt.solve import solve

DEMO = Path(__file__).resolve().parent / "data" / "demo.json"


def show_frontier() -> None:
    """One line per plan on the frontier, from the best NPV to the most risk removed."""
    print()
    print("NPV against risk removed:")
    for point in frontier(read_request(DEMO)):
        print(f"  NPV ${point.npv:,.0f}k  risk removed ${point.risk:,.1f}k  funds {', '.join(point.plan.funded)}")


def show_scenario() -> None:
    """The base plan against a scenario that adds $1,000k to the budgets of 2028 and 2029."""
    request = read_request(DEMO)
    more = Scenario("more money", budget={y: request.budget[y] + 1_000 for y in (2028, 2029)},
                    note="the rate case allows more capital")
    base, other = solve(request), solve(apply(request, more))
    d = diff(base, other)
    print()
    print(f"scenario {more.name}: NPV ${base.npv:,.0f}k -> ${other.npv:,.0f}k")
    print(f"  selected {', '.join(d.selected) or 'none'}; deferred {', '.join(d.deferred) or 'none'}")
    for pid, before, after in d.shifted:
        print(f"  shifted {pid} {before} -> {after}")


if __name__ == "__main__":
    status = main([str(DEMO), "--why", "P003"])
    show_frontier()
    show_scenario()
    raise SystemExit(status)
