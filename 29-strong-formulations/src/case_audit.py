"""An audit of the inherited GridCap medium model with the tools of lessons 6.7.1 to 6.7.3."""

from collections import Counter

from gridcap import generate
from derived_rows import already_a_row, conflicts, fixable
from strong_model import build, lp_bound, root_bound, size

medium = generate("medium")
steps = [("inherited", "aggregated", "aggregated"),
         ("fronts disaggregated", "disaggregated", "aggregated"),
         ("precedence cumulative", "disaggregated", "cumulative")]
print("step                    variables  rows  LP bound    HiGHS root bound")
for label, fronts, precedence in steps:
    lp = lp_bound(build(medium, integer=False, fronts=fronts, precedence=precedence).model).objective_value()
    milp = build(medium, fronts=fronts, precedence=precedence).model
    variables, rows = size(milp)
    print(f"{label:22}  {variables:9}  {rows:4}  {lp:10,.2f}  {root_bound(milp):,.0f}")

# 1. Where is the inherited LP fractional?
weak = build(medium, integer=False, fronts="aggregated", precedence="aggregated")
point = lp_bound(weak.model)
fronts = [point.variable_values(y) for y in weak.front.values()]
starts = [point.variable_values(v) for v in weak.x.values()]
print(f"inherited LP: fronts strictly between 0 and 1: {sum(1e-6 < f < 1 - 1e-6 for f in fronts)} of {len(fronts)} "
      f"(from {min(fronts):.2f} to {max(fronts):.2f}); starts: {sum(1e-6 < s < 1 - 1e-6 for s in starts)} of {len(starts)}")

# 2. Bounds and valid rows (lesson 6.7.2): the medium model has budget rows only.
fixed = fixable(medium, crews=False)
new = [p for p in conflicts(medium, fixed, crews=False) if not already_a_row(sorted(p), medium)]
print(f"starts fixable from the budget rows: {len(fixed)}; conflicts not already a row: {len(new)}")

# 3. Symmetry (lesson 6.7.3): projects that are identical in every number the model reads.
key = Counter((p.region, p.program, p.cost_profile, tuple(sorted(p.npv.items())), p.must_do, p.parent, p.alt_group)
              for p in medium.projects)
print(f"groups of identical projects: {sum(1 for n in key.values() if n > 1)}")
