"""The four coefficient ranges of the loan model, computed from the model and read from HiGHS's log."""

from gridcap import generate
from loan_model import TIGHT, build, coefficient_ranges, solve

lm = build(generate("small"), TIGHT)
_, log = solve(lm.model)
start = log.index("Coefficient ranges:")
print("HiGHS's log:")
for line in log[start - 1:start + 5]:
    print("  " + line)
print("coefficient_ranges(model):")
for kind, (low, high) in coefficient_ranges(lm.model).items():
    print(f"  {kind:7} [{low:.0e}, {high:.0e}]   exact: {low:g} to {high:,g}   span {high / low:,.0f}")
