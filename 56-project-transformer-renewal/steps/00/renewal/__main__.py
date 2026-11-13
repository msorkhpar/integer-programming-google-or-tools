"""python -m renewal: this year's replacement list for a fictional 500-unit fleet."""

from .fleet import generate_fleet
from .rank import worst_first
from .report import summarize

BUDGET = 10_000   # $k this year

if __name__ == "__main__":
    fleet = generate_fleet(500)
    s = summarize(fleet, worst_first(fleet, BUDGET))
    print(f"worst first: {s.units} units, ${s.spend:,}k of ${BUDGET:,}k, risk removed ${s.risk_removed:,.0f}k")
