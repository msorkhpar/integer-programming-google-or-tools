"""Lesson 14.3.5: the same request on fleets of 500 to 5,000 units: model size, build time, solve time.

The fleets are generated (GridCap is fictional); the code is snapshot steps/05. The sizes are exact.
The times are from one machine and change from run to run; each is the median of three runs.
"""

import statistics
import time

import steps

steps.use(5)
from ortools.math_opt.python import mathopt              # noqa: E402
from renewal.fleet import generate_fleet                # noqa: E402
from renewal.model import build, candidates             # noqa: E402
from renewal.reference import build_reference           # noqa: E402
from renewal.request import Request                     # noqa: E402
from renewal.risk import risk_removed, risk_table       # noqa: E402
from renewal.solve import read_plan, solve_quietly      # noqa: E402

REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02, outage_cost=300, outages=2,
                  crew_weeks=12, lead_times=True, spares={"medium": 2, "large": 1})
SIZES = (500, 1000, 2000, 5000)


def median_seconds(work, repeats=3):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        work()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


fleets = {n: generate_fleet(n) for n in SIZES}
big = REQUEST.scaled(10)
print(f"request for 5,000 units: budget ${big.budget:,}k a year, {big.outages} outages and {big.crew_weeks} "
      f"crew-weeks per region-year, spares {big.spares}")
print("size of the model (exact):")
for n in SIZES:
    request = REQUEST.scaled(n // 500)
    model = build(fleets[n], request).model
    nonzeros = sum(1 for _ in model.linear_constraint_matrix_entries())
    print(f"  {n:5} units: {len(candidates(fleets[n], request)):5} candidates, {model.get_num_variables():6} variables, "
          f"{model.get_num_linear_constraints():5} rows, {nonzeros:7} nonzeros")

print("build time, median of 3 (s):")
for n in SIZES:
    request = REQUEST.scaled(n // 500)
    slow = median_seconds(lambda: build_reference(fleets[n], request))
    fast = median_seconds(lambda: build(fleets[n], request))
    print(f"  {n:5} units: reference {slow:6.2f}  fast {fast:6.2f}")

units = candidates(fleets[5000], big)
loops = median_seconds(lambda: [[risk_removed(t, y, big) for y in big.plan_years()] for t in units])
arrays = median_seconds(lambda: risk_table(units, big))
print(f"coefficients at 5,000 units (s): one call per unit and year {loops:.2f}, one array computation {arrays:.3f}")

print("phases at 5,000 units, one run (s):")
start = time.perf_counter()
fleet = generate_fleet(5000)
generated = time.perf_counter()
built = build(fleet, big)
model_built = time.perf_counter()
result = solve_quietly(built.model, mathopt.SolveParameters(relative_gap_tolerance=big.gap))
solved = time.perf_counter()
got = read_plan(built, result)
print(f"  generate {generated - start:.2f}  build {model_built - generated:.2f}  solve {solved - model_built:.2f}")
print(f"  {len(got.replace)} units replaced, gap {(got.bound - got.value) / got.bound:.2%}, {got.status}")

steps.show(5)
