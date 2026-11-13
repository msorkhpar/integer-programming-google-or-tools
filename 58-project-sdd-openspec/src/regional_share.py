"""Lesson 14.4.2: a regional spend share, from proposal to archive.

The portfolio is generated (GridCap is fictional). The code is snapshot steps/01, then steps/02.
"""

import changes
import steps

BUDGET, YEARS = 3_000, 5


def plains_share(portfolio, starts):
    spend, plains = {}, {}
    region = {p.pid: p.region for p in portfolio}
    cost = {p.pid: p.cost for p in portfolio}
    for pid, year in starts.items():
        spend[year] = spend.get(year, 0) + cost[pid]
        plains[year] = plains.get(year, 0) + (cost[pid] if region[pid] == "plains" else 0)
    return " ".join(f"{100 * plains.get(y, 0) / spend[y]:3.0f}%" if y in spend else "  - "
                    for y in range(2027, 2027 + YEARS))


steps.use(1)
from capplan.plan import plan              # noqa: E402
from capplan.portfolio import generate     # noqa: E402
from capplan.request import Request        # noqa: E402

PORTFOLIO = generate(40, seed=58, years=YEARS)
before = plan(PORTFOLIO, Request(budget=BUDGET, years=YEARS))
print(f"Plains has {sum(p.region == 'plains' for p in PORTFOLIO)} of the 40 projects; "
      "the Plains projects that may start in each year: "
      + " ".join(str(sum(p.region == "plains" and p.earliest <= y <= p.latest for p in PORTFOLIO))
                 for y in range(2027, 2027 + YEARS)))
print(f"steps/01, no share      : value ${before.value:,}k, Plains share by year {plains_share(PORTFOLIO, before.starts)}")

steps.use(2)
from capplan.model import build            # noqa: E402
from capplan.plan import plan              # noqa: E402
from capplan.request import Request        # noqa: E402

request = Request(budget=BUDGET, years=YEARS, shares={"plains": 25})
after = plan(PORTFOLIO, request)
print(f"steps/02, Plains at 25% : value ${after.value:,}k, Plains share by year {plains_share(PORTFOLIO, after.starts)}")
print(f"the share costs ${before.value - after.value:,}k of value ({after.status})")
names = [c.name for c in build(PORTFOLIO, request).model.proto.constraints if c.name.startswith("share_")]
print(f"share rows: {len(names)}, {names[0]} to {names[-1]}")
for shares in ({"plains": 60, "coast": 50}, {"south": 10}):
    try:
        plan(PORTFOLIO, Request(budget=BUDGET, years=YEARS, shares=shares))
    except ValueError as error:
        print(f"shares {shares}: refused, {error}")

print("\n== validate --strict, the change proposed")
changes.validate(2, 2)
print()
steps.show(2)
print("\n== archive")
changes.archive(2)
