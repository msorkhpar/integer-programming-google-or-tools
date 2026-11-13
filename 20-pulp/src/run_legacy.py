"""Run the inherited PuLP selection script on GridCap small and look inside what it built."""

import warnings

from gridcap import generate
from legacy_selection import solve_legacy

small = generate("small")
with warnings.catch_warnings(record=True) as caught:      # what `python -W default` would show
    warnings.simplefilter("always")
    status, total, funded, prob = solve_legacy(small)
print(f"{status}: value ${total:,.0f}k, {len(funded)} of {len(small.projects)} funded")
print(f"variables {prob.numVariables()}, rows {prob.numConstraints()}, objective named {prob.objective.name!r}")
x = {v.name: v for v in prob.variables()}
print("a variable:", x["x_P001"].name, x["x_P001"].cat, x["x_P001"].lowBound, x["x_P001"].upBound,
      "value", x["x_P001"].varValue)
names = [row.name for row in prob.constraints()]
print("rows:", ", ".join(names[:4]), "...", names[-1])
budget = prob.get_constraint_by_name("budget")
print(f"budget row: sense {budget.sense}, rhs {-budget.constant:,.0f}, slack {budget.slack + 0:,.0f}")
deprecated = sorted({str(w.message).split(";")[0] for w in caught if w.category is DeprecationWarning})
print("DeprecationWarnings raised by the script:")
for message in deprecated:
    print("  " + message)
