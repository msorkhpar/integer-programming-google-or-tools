"""Rescale the mixed-unit loan model one step at a time, and watch its ranges and HiGHS's warnings."""

from gridcap import generate
from loan_model import HUGE_M, MIXED, TIGHT, Units, build, coefficient_ranges, solve

small = generate("small")
STEPS = (
    MIXED,
    Units(objective=1, rows=0.001, big_m=1e9, name="objective in $k"),
    HUGE_M,
    TIGHT,
)

plans = {}
for units in STEPS:
    lm = build(small, units)
    result, log = solve(lm.model)
    ranges = coefficient_ranges(lm.model)
    values = result.variable_values()
    plans[units.name] = sorted(i for i, v in lm.x.items() if values[v] > 0.5)
    print(f"{units.name}")
    print("  " + "  ".join(f"{k} [{lo:.0e}, {hi:.0e}]" for k, (lo, hi) in ranges.items()))
    for line in log:
        if line.startswith("WARNING"):
            print("  " + line)
    loans = {y: round(values[lm.loan[y]] / units.rows) for y in small.years if values[lm.take[y]] > 0.5}
    print(f"  {result.termination.reason.name}, objective {result.objective_value():,.1f}"
          f" = ${lm.in_k(result.objective_value()):,.1f}k, {len(plans[units.name])} projects, loans $k {loans}")
print("same projects in every step:", len({tuple(p) for p in plans.values()}) == 1)
