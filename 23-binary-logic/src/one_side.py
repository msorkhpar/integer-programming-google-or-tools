"""Lesson 6.1.2: an OR variable needs only the side of its rows that the model would exploit.

GridCap is a fictional utility's portfolio. y[r] = 1 means "region r gets distribution work":
the OR of the region's distribution projects.
"""

from gridcap import REGIONS, generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")
members = {r: ids(small, program="distribution", region=r) for r in REGIONS}


def with_regions(sides: set[str], cap: int | None = None, credit: int = 0):
    sel = build(small)
    model, x = sel.model, sel.x
    y = {r: model.add_binary_variable(name=f"y_{r}") for r in REGIONS}
    for r in REGIONS:
        if "up" in sides:     # any distribution project in r pushes y[r] up to 1
            for i in members[r]:
                model.add_linear_constraint(y[r] >= x[i], name=f"up_{r}_{i}")
        if "down" in sides:   # no distribution project in r pushes y[r] down to 0
            model.add_linear_constraint(y[r] <= sum(x[i] for i in members[r]), name=f"down_{r}")
    if cap is not None:
        model.add_linear_constraint(sum(y.values()) <= cap, name="regions")
    if credit:
        model.maximize(model.objective.as_linear_expression() + credit * sum(y.values()))
    result = solve_highs(model, EXACT)
    plan = funded(sel, result)
    served = [r for r in REGIONS if any(i in plan for i in members[r])]
    claimed = [r for r in REGIONS if result.variable_values(y[r]) > 0.5]
    npv = sum(small.project(i).value for i in plan)
    return result.objective_value(), npv, served, claimed


print("Rule: distribution work in at most 2 regions")
for sides in ({"up", "down"}, {"up"}, {"down"}):
    obj, npv, served, claimed = with_regions(sides, cap=2)
    print(f"  rows {'+'.join(sorted(sides)):8} NPV ${npv:,.0f}k  regions served {served}")

print("Credit: $150k for each region that gets distribution work")
for sides in ({"up", "down"}, {"down"}, {"up"}):
    obj, npv, served, claimed = with_regions(sides, credit=150)
    true = npv + 150 * len(served)
    print(f"  rows {'+'.join(sorted(sides)):8} claims ${obj:,.0f}k for {len(claimed)} regions; "
          f"plan serves {served}, worth ${true:,.0f}k")
