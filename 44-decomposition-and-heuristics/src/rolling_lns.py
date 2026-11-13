"""Rolling horizon, then LNS, on GridCap medium with crews; every plan measured against the best bound."""

from ortools.math_opt.python import mathopt

from gridcap import generate

from capital import build, schedule, solve_highs, value, violations
from lns import lns
from rolling import rolling_horizon

medium = generate("medium")
lp = solve_highs(build(medium, integer=False, crews=True).model).objective_value()
print(f"LP relaxation bound {lp:,.1f}")

print("monolithic MILP stopped after a node budget:")
bound, early = lp, None
for nodes in (200, 2000, 8000):
    params = mathopt.SolveParameters(node_limit=nodes, relative_gap_tolerance=0.0)
    cap = build(medium, crews=True)
    r = solve_highs(cap.model, params)
    early = early or schedule(cap, r)                     # the plan after 200 nodes
    bound = min(bound, r.termination.objective_bounds.dual_bound)
    print(f"  {nodes:5} nodes  plan {r.objective_value():9,.0f}  bound {r.termination.objective_bounds.dual_bound:11,.1f}"
          f"  gap {100 * (r.termination.objective_bounds.dual_bound - r.objective_value()) / r.objective_value():.2f}%")

print("rolling horizon (window, years kept per window):")
plans = {}
for window, keep in ((3, 1), (4, 2), (5, 2)):
    plan, solves, nodes = rolling_horizon(medium, window, keep)
    plans[window, keep] = plan
    print(f"  window {window}, keep {keep}:  plan {value(medium, plan):9,}  {solves} MIP solves, {nodes:5} nodes"
          f"  gap to best bound {100 * (bound - value(medium, plan)) / value(medium, plan):.2f}%"
          f"  breaks {violations(medium, plan, crews=True) or 'nothing'}")

for start, kind, label in ((plans[4, 2], "region", "the window-4 plan"), (plans[4, 2], "years", "the window-4 plan"),
                           (early, "years", "the 200-node plan")):
    print(f"LNS from {label}, neighborhoods by {kind}:")
    plan, nodes = lns(medium, start, kind, 8)
    print(f"  final plan {value(medium, plan):,}  {nodes} nodes  gap to best bound"
          f" {100 * (bound - value(medium, plan)) / value(medium, plan):.2f}%"
          f"  breaks {violations(medium, plan, crews=True) or 'nothing'}")
