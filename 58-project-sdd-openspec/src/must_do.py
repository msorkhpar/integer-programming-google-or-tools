"""Lesson 14.4.3: a must-do override that needs a recorded reason.

The portfolio is generated (GridCap is fictional). The code is snapshot steps/02, then steps/03.
"""

import changes
import steps

BUDGET, YEARS, SHARES = 3_000, 5, {"plains": 25}

steps.use(2)
from capplan.plan import plan              # noqa: E402
from capplan.portfolio import generate     # noqa: E402
from capplan.request import Request        # noqa: E402

PORTFOLIO = generate(40, seed=58, years=YEARS)
before = plan(PORTFOLIO, Request(budget=BUDGET, years=YEARS, shares=SHARES))
left_out = [p for p in PORTFOLIO if p.pid not in before.starts]
forced = min(left_out, key=lambda p: (p.value / p.cost, p.pid))
print(f"steps/02 plan: {len(before.starts)} started, value ${before.value:,}k; {len(left_out)} left out")
print(f"least value per $k among them: {forced.pid}, {forced.region}, ${forced.cost:,}k for ${forced.value:,}k, "
      f"may start {forced.earliest}-{forced.latest}")

steps.use(3)
from capplan.plan import plan              # noqa: E402
from capplan.report import overrides       # noqa: E402
from capplan.request import Request        # noqa: E402

REASON = "Regulator order RO-7, Plainsview feeder"
request = Request(budget=BUDGET, years=YEARS, shares=SHARES, must_do={forced.pid: REASON})
after = plan(PORTFOLIO, request)
print(f"steps/03 plan, {forced.pid} must-do: {len(after.starts)} started, value ${after.value:,}k ({after.status}); "
      f"{forced.pid} starts in {after.starts.get(forced.pid)}")
print(f"the override costs ${before.value - after.value:,}k of value")
for line in overrides(request):
    print(f"report: must-do {line}")
for must_do in ({forced.pid: ""}, {forced.pid: "   "}, {"P999": REASON}):
    try:
        plan(PORTFOLIO, Request(budget=BUDGET, years=YEARS, shares=SHARES, must_do=must_do))
        print(f"must_do {must_do}: accepted")
    except ValueError as error:
        print(f"must_do {must_do}: refused, {error}")
for text in ("   ", "\t ", "\t\n"):
    print(f"not {text!r} is {not text}; {text!r}.strip() is {text.strip()!r}")

print("\n== list, the change proposed")
changes.listing(3)
print("\n== validate --strict, the change proposed")
changes.validate(3, 3)
print()
steps.show(3)
print("\n== archive")
changes.archive(3)
