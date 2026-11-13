"""Lesson 14.4.5: retiring the yearly start cap, a REMOVED requirement.

The portfolio is generated (GridCap is fictional). The code is snapshot steps/04, then steps/05.
"""

from collections import Counter
from dataclasses import replace

import changes
import steps

BUDGET, YEARS = 3_000, 5
FIELDS = dict(shares={"plains": 25}, must_do={"P039": "Regulator order RO-7, Plainsview feeder"}, carry=20)


def describe(label, got):
    per_year = Counter(got.starts.values())
    print(f"{label:28} {len(got.starts):2} started, value ${got.value:,}k ({got.status}); starts by year "
          + " ".join(str(per_year[y]) for y in range(2027, 2027 + YEARS)))


steps.use(4)
from capplan.plan import plan              # noqa: E402
from capplan.portfolio import generate     # noqa: E402
from capplan.request import Request        # noqa: E402

PORTFOLIO = generate(40, seed=58, years=YEARS)
describe("steps/04, default request", plan(PORTFOLIO, Request(budget=BUDGET, years=YEARS, **FIELDS)))

steps.use(5)
from capplan.plan import plan              # noqa: E402
from capplan.request import Request        # noqa: E402

request = Request(budget=BUDGET, years=YEARS, **FIELDS)
describe("steps/05, default request", plan(PORTFOLIO, request))
for cap in (3, 0):
    try:
        plan(PORTFOLIO, replace(request, max_starts=cap))
        print(f"max_starts={cap}: accepted")
    except ValueError as error:
        print(f"max_starts={cap}: refused, {error}")

print("\n== the tests of steps/04 on the code of steps/05")
for o in steps.outcomes(5, 4):
    if o.result != "passed":
        print(f"  {o.result.upper():6} {o.test} ({o.kind})")
        print(f"         {o.message.removeprefix('AssertionError: ')[:96]}")

print("\n== validate --strict, the change proposed")
changes.validate(5, 5)
print()
steps.show(5)
print("\n== archive")
changes.archive(5)
living = (steps.step_dir(5) / "openspec" / "specs" / "capital-plan" / "spec.md").read_text(encoding="utf-8")
print(f"'Yearly start cap' in the living spec after archive: {'Yearly start cap' in living}")
