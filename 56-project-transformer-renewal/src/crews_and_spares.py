"""Lesson 14.3.4: crew-weeks per region and year, lead times, and spare units.

The fleet is generated (GridCap is fictional); the code is snapshot steps/04.
"""

from collections import Counter
from dataclasses import replace

import steps

steps.use(4)
from renewal.fleet import FIRST_YEAR, KINDS, generate_fleet     # noqa: E402
from renewal.plan import plan                                   # noqa: E402
from renewal.request import Request                             # noqa: E402

BUNDLES = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02, outage_cost=300, outages=2)
REQUEST = replace(BUNDLES, crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})

fleet = generate_fleet(500)
by_id = {t.tid: t for t in fleet}


def describe(name, replace_):
    weeks = Counter()
    early = Counter()
    for tid, y in replace_.items():
        t = by_id[tid]
        weeks[t.region, y] += KINDS[t.kind].crew_weeks
        if y < FIRST_YEAR + KINDS[t.kind].lead_years:
            early[t.kind] += 1
    over = sum(1 for w in weeks.values() if w > REQUEST.crew_weeks)
    print(f"{name:20}: {len(replace_):3} units; region-years over {REQUEST.crew_weeks} crew-weeks: {over} of 40, "
          f"most {max(weeks.values())}; units before their lead time: medium {early['medium']}, large {early['large']}")


before = plan(fleet, BUNDLES)
describe("bundles plan", before.replace)
after = plan(fleet, REQUEST)
describe("with crews and spares", after.replace)
print(f"risk removed: bundles plan ${before.value:,.0f}k, with crews and spares ${after.value:,.0f}k "
      f"(bound ${after.bound:,.0f}k, {after.status})")
by_kind = Counter(by_id[tid].kind for tid in after.replace)
print(f"replaced by kind: small {by_kind['small']}, medium {by_kind['medium']}, large {by_kind['large']}")
first_large = min(y for tid, y in after.replace.items() if by_id[tid].kind == "large")
print(f"large units replaced in {FIRST_YEAR}-{FIRST_YEAR + 2}: "
      f"{sum(1 for tid, y in after.replace.items() if by_id[tid].kind == 'large' and y < FIRST_YEAR + 3)}; "
      f"first large replacement {first_large}")

steps.show(4)
