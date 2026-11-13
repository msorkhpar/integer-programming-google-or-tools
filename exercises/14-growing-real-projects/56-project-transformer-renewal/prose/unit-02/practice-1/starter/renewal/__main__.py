"""python -m renewal: this year's replacement list for a fictional 500-unit fleet."""

from .fleet import generate_fleet
from .plan import plan
from .rank import worst_first
from .report import summarize
from .request import Request

BUDGET = 10_000   # $k this year

if __name__ == "__main__":
    fleet = generate_fleet(500)
    for name, chosen in (("worst first", worst_first(fleet, BUDGET)),
                         ("model", list(plan(fleet, Request(BUDGET)).replace))):
        s = summarize(fleet, chosen)
        print(f"{name:11}: {s.units} units, ${s.spend:,}k of ${BUDGET:,}k, risk removed ${s.risk_removed:,.0f}k")
