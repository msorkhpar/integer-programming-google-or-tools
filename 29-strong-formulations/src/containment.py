"""Is one formulation's LP region inside the other's? A proof by rows, and a check on 30 objectives."""

import random

from gridcap import generate
from strong_model import build, fronts_of, lp_bound

small = generate("small")

# The proof: every aggregated row is the sum of its front's disaggregated rows.
#   sum_i (started_i - y) <= 0   summed over the n projects of a front   is   sum_i started_i - n y <= 0
weak = build(small, integer=False, fronts="aggregated")
strong = build(small, integer=False, fronts="disaggregated")
rows = {c.name: c for c in strong.model.linear_constraints()}
weak_rows = {c.name: c for c in weak.model.linear_constraints()}
same = 0
for (region, program), members in fronts_of(small).items():
    name = f"front_{region}_{program}"
    total = {}
    for pid in members:
        for term in rows[f"{name}_{pid}"].terms():
            total[term.variable.name] = total.get(term.variable.name, 0) + term.coefficient
    aggregated = {t.variable.name: t.coefficient for t in weak_rows[name].terms()}
    same += total == aggregated
print(f"aggregated rows equal to a sum of disaggregated rows: {same} of {len(fronts_of(small))}")

# The evidence: the same comparison under 30 other objectives (NPVs and fees scaled at random).
rng = random.Random(29)
lower = equal = higher = 0
for _ in range(30):
    scale = {v: rng.uniform(0.5, 1.5) for v in strong.x}
    fee = {k: rng.uniform(0.0, 3.0) for k in strong.front}
    bounds = []
    for sm in (weak, strong):
        sm.model.maximize(sum(small.project(i).npv[t] * scale[i, t] * v for (i, t), v in sm.x.items())
                          - sum(sm.fee[k] * fee[k] * y for k, y in sm.front.items()))
        bounds.append(lp_bound(sm.model).objective_value())
    if bounds[1] < bounds[0] - 1e-6:
        lower += 1
    elif bounds[1] > bounds[0] + 1e-6:
        higher += 1
    else:
        equal += 1
print(f"30 objectives: disaggregated bound lower in {lower}, equal in {equal}, higher in {higher}")
