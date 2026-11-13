"""Lesson 6.5.3: repair and replace of one asset as alternatives, with and without the group row.

GridCap is a fictional utility's portfolio, generated for this course.
"""

from gridcap import generate
from planning_model import build, groups_of, money, schedule, solve_highs

small = generate("small")
groups = groups_of(small)

for g, members in groups.items():
    print(g, "asset", small.project(members[0]).asset_id, "|",
          "; ".join(f"{i} {small.project(i).intervention} {small.project(i).capex:,} may start "
                    f"{list(small.project(i).starts())}" for i in members))
for label, alternatives in [("with alt rows", True), ("without", False)]:
    plan = build(small, alternatives=alternatives)
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    chosen = {g: [f"{i} {small.project(i).intervention} {starts[i]}" for i in m if i in starts]
              for g, m in groups.items()}
    print(f"{label:14} NPV {money(result.objective_value())}  {chosen}")
