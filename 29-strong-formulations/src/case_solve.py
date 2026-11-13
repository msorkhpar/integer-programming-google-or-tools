"""The inherited and the reformulated GridCap medium models, each solved by HiGHS to its default gap."""

from gridcap import generate
from strong_model import build, solve_highs

medium = generate("medium")
plans = {}
print("model          plan value  proven bound  gap      nodes")
for label, fronts, precedence in (("inherited", "aggregated", "aggregated"),
                                  ("reformulated", "disaggregated", "cumulative")):
    sm = build(medium, fronts=fronts, precedence=precedence)
    result = solve_highs(sm.model)          # HiGHS's default relative gap: 1e-4
    value, bound = result.objective_value(), result.best_objective_bound()
    plans[label] = {s for s, v in sm.x.items() if result.variable_values(v) > 0.5}
    print(f"{label:13}  {value:10,.0f}  {bound:12,.0f}  {(bound - value) / value:.4%}  "
          f"{result.solve_stats.node_count:5,}  {result.termination.reason.name}")
same = plans["inherited"] == plans["reformulated"]
print(f"same plan: {same}; starts that differ: {len(plans['inherited'] ^ plans['reformulated'])}")
