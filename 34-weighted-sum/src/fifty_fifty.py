"""GridCap small: the NPV plan, the risk plan, and the plan the board's 50/50 weights pick."""

from gridcap import generate
from two_objectives import build, score, weighted

small = generate("small")
sm = build(small)

for name, w_npv, w_risk in (("max NPV", 1, 0), ("max risk removed", 0, 1), ("50/50 weighted sum", 0.5, 0.5)):
    plan = weighted(sm, w_npv, w_risk)
    npv, risk = score(sm, plan)
    print(f"{name:18} w=({w_npv}, {w_risk}): {len(plan)} projects, NPV ${npv:,}k, risk removed ${risk:,.0f}k")

best_npv, best_risk = score(sm, weighted(sm, 1, 0))[0], score(sm, weighted(sm, 0, 1))[1]
npv, risk = score(sm, weighted(sm, 0.5, 0.5))
print(f"50/50 plan: {npv / best_npv:.1%} of the best NPV, {risk / best_risk:.1%} of the most risk removed")
