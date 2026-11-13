"""Lesson 14.3.6: solve times at 5,000 units, aggregated against per-unit rows, and a rolling horizon.

The fleet is generated (GridCap is fictional); the code is snapshot steps/06. Times depend on the
machine and change from run to run. The full run takes about half an hour, so by default the
program only says how to start it:

    python3 src/stronger_timing.py --full
"""

import datetime
import sys
import time
from dataclasses import replace

import steps

steps.use(6)
from ortools.math_opt.python import mathopt              # noqa: E402
from renewal.check import violations                    # noqa: E402
from renewal.fleet import generate_fleet                # noqa: E402
from renewal.model import build                         # noqa: E402
from renewal.request import Request                     # noqa: E402
from renewal.rolling import rolling                     # noqa: E402
from renewal.solve import read_plan, solve_quietly      # noqa: E402

REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.001, outage_cost=300, outages=2,
                  crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})
LIMIT = datetime.timedelta(seconds=900)

if "--full" not in sys.argv:
    print("pass --full to run the 5,000-unit timings (about half an hour)")
    sys.exit(0)

fleet, request = generate_fleet(5000), REQUEST.scaled(10)
best_bound = float("inf")
for link in ("aggregated", "per-unit"):
    r = replace(request, link=link)
    built = build(fleet, r)
    start = time.perf_counter()
    result = solve_quietly(built.model, mathopt.SolveParameters(relative_gap_tolerance=r.gap, time_limit=LIMIT))
    seconds = time.perf_counter() - start
    got = read_plan(built, result)
    best_bound = min(best_bound, got.bound)
    print(f"{link:10} gap 0.1%, limit 900 s: {seconds:6.1f} s, {got.status}, plan ${got.value:,.0f}k, "
          f"bound ${got.bound:,.0f}k, gap {(got.bound - got.value) / got.bound:.3%}, "
          f"nodes {result.solve_stats.node_count}")
for window, keep in ((3, 1), (5, 2)):
    start = time.perf_counter()
    got = rolling(fleet, request, window=window, keep=keep)
    seconds = time.perf_counter() - start
    print(f"rolling window {window} keep {keep}: {seconds:6.1f} s, plan ${got.value:,.0f}k, "
          f"{(best_bound - got.value) / best_bound:.3%} below the best bound, "
          f"rules broken {len(violations(fleet, request, got.replace))}")
print(f"best bound known ${best_bound:,.0f}k")
