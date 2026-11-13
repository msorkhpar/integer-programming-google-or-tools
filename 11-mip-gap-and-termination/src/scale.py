"""What 0.01% is in money: on a $2B objective, and on GridCap large."""

import statistics

from gridcap import generate
from selection import build, solve_highs

print(f"0.01% of $2,000,000k: ${2_000_000 * 0.0001:,.0f}k")

large = generate("large")
sel = build(large)
result = solve_highs(sel.model)
p = result.termination.objective_bounds.primal_bound
d = result.termination.objective_bounds.dual_bound
print(f"GridCap large: {len(large.projects):,} projects, budgets ${sum(large.budget.values()):,}k over "
      f"{len(large.years)} years")
print(f"HiGHS defaults: {result.termination.reason.name}, NPV ${p:,.0f}k, bound ${d:,.0f}k, "
      f"gap ${d - p:,.0f}k ({(d - p) / p:.4%}), {result.solve_stats.node_count} node(s)")
allowed = 0.0001 * p
values = [q.value for q in large.projects]
print(f"0.01% of this NPV: ${allowed:,.0f}k")
print(f"projects with NPV below that: {sum(v < allowed for v in values):,} of {len(values):,}; "
      f"median project NPV ${statistics.median(values):,.0f}k")
