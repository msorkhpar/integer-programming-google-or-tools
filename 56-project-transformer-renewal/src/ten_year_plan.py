"""Lesson 14.3.2: a ten-year plan under one budget per year, valued with Weibull failure curves.

The fleet is generated (GridCap is fictional); the code is snapshot steps/02.
"""

from dataclasses import replace

import steps

steps.use(2)
from renewal.fleet import FIRST_YEAR, generate_fleet    # noqa: E402
from renewal.plan import plan                           # noqa: E402
from renewal.report import spend_by_year                # noqa: E402
from renewal.request import Request                     # noqa: E402
from renewal.risk import pof_next, risk_removed         # noqa: E402

REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02)

fleet = generate_fleet(500)
by_id = {t.tid: t for t in fleet}
t = by_id["T00076"]
print(f"{t.tid}: {t.kind}, age {t.age}, CoF ${t.cof:,}k; PoF column {t.pof:.4f}, curve {pof_next(t.age, t.kind):.4f}")
print("  PoF by year if kept: " + ", ".join(f"{FIRST_YEAR + k}: {pof_next(t.age + k, t.kind):.3f}"
                                             for k in (0, 3, 6, 9)))
for window in (10, 20):
    request = replace(REQUEST, window=window)
    print(f"rr[start] over {window} years: " + ", ".join(
        f"{y}: {risk_removed(t, y, request):,.0f}" for y in (2027, 2030, 2033, 2036)))

print(f"candidates (age >= {REQUEST.min_age}): {sum(1 for u in fleet if u.age >= REQUEST.min_age)} of {len(fleet)}")
plans = {}
for window in (10, 20):
    plans[window] = got = plan(fleet, replace(REQUEST, window=window))
    late = sum(1 for y in got.replace.values() if y >= 2034)
    print(f"window {window}: {len(got.replace)} units replaced, {late} of them in 2034-2036, "
          f"risk removed ${got.value:,.0f}k (bound ${got.bound:,.0f}k, {got.status})")
moved = {tid for tid in plans[10].replace.keys() | plans[20].replace.keys()
         if plans[10].replace.get(tid) != plans[20].replace.get(tid)}
print(f"units placed differently by the two windows: {len(moved)}")

got = plan(fleet, REQUEST)
spend = spend_by_year(fleet, got.replace)
for y in REQUEST.plan_years():
    units = sorted(tid for tid, year in got.replace.items() if year == y)
    print(f"  {y}: {len(units):2} units, ${spend.get(y, 0):,}k, mean age {sum(by_id[u].age for u in units) / len(units):.0f}")
print(f"gap to the bound: {(got.bound - got.value) / got.bound:.2%}")

steps.show(2)
