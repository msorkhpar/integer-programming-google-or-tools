"""Run: plan the demo export, print the planners' report, why P003 was deferred, and the trade
between NPV and risk.

data/demo.json is GridCap tiny, a fictional utility's portfolio. Its path is taken from this
file's folder, never from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from pathlib import Path

from cipt.__main__ import main
from cipt.data import read_request
from cipt.goals import frontier

DEMO = Path(__file__).resolve().parent / "data" / "demo.json"


def show_frontier() -> None:
    """One line per plan on the frontier, from the best NPV to the most risk removed."""
    print()
    print("NPV against risk removed:")
    for point in frontier(read_request(DEMO)):
        print(f"  NPV ${point.npv:,.0f}k  risk removed ${point.risk:,.1f}k  funds {', '.join(point.plan.funded)}")


if __name__ == "__main__":
    status = main([str(DEMO), "--why", "P003"])
    show_frontier()
    raise SystemExit(status)
