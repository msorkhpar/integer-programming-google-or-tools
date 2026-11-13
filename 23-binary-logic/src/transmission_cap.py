"""Lesson 6.1.1: a counting row caps how many transmission projects GridCap small may fund.

GridCap is a fictional utility's portfolio. The cap is the number of transmission outages the
(fictional) system operator will approve for the plan.
"""

from gridcap import generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")
transmission = ids(small, program="transmission")


def with_cap(cap: int | None):
    sel = build(small)
    if cap is not None:
        sel.model.add_linear_constraint(sum(sel.x[i] for i in transmission) <= cap, name="outages")
    result = solve_highs(sel.model, EXACT)
    return result.objective_value(), funded(sel, result)


npv0, plan0 = with_cap(None)
print(f"{len(transmission)} transmission candidates; the uncapped plan funds "
      f"{sum(i in transmission for i in plan0)}, NPV ${npv0:,.0f}k")
for cap in (6, 5, 4, 3):
    npv, plan = with_cap(cap)
    kept = [i for i in plan if i in transmission]
    print(f"cap {cap}: NPV ${npv:,.0f}k ({npv - npv0:+,.0f}), {len(plan)} projects, transmission {kept}")
