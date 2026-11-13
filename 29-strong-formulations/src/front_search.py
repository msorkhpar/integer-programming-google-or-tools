"""What HiGHS makes of the two front forms on GridCap small: its root bound and its search."""

from gridcap import generate
from strong_model import EXACT, build, lp_bound, root_bound, solve_highs

small = generate("small")
print("form           LP bound   HiGHS root bound  optimum  nodes")
for form in ("aggregated", "disaggregated"):
    lp = lp_bound(build(small, integer=False, fronts=form).model).objective_value()
    model = build(small, fronts=form).model
    result = solve_highs(model, EXACT)
    print(f"{form:13}  {lp:9,.2f}  {root_bound(model):16,.0f}  {result.objective_value():7,.0f}  "
          f"{result.solve_stats.node_count:5}")
