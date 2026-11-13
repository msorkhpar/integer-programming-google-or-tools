"""Scaling both weights changes nothing; changing an objective's unit changes what the weights mean."""

from gridcap import generate
from two_objectives import build, score, weighted

small = generate("small")
sm = build(small)

print("weights (w_npv, w_risk) -> plan")
for w_npv, w_risk in ((0.5, 0.5), (1, 1), (3, 3), (0.2, 0.8), (2, 8)):
    npv, risk = score(sm, weighted(sm, w_npv, w_risk))
    print(f"  ({w_npv}, {w_risk}): price {w_npv / w_risk:.2f}, NPV ${npv:,}k, risk removed ${risk:,.0f}k")

# The ends of the trade-off (lesson 7.3.4), used by the two normalizations below.
npv_hi, risk_lo = score(sm, weighted(sm, 1, 0))
npv_lo, risk_hi = score(sm, weighted(sm, 0, 1))
scales = {                                 # what each objective is divided by before 50/50 is applied
    "both in $k":              (1, 1),
    "risk in $M, NPV in $k":   (1, 1000),
    "each / its range":        (npv_hi - npv_lo, risk_hi - risk_lo),
    "each / its best value":   (npv_hi, risk_hi),
}
print("50/50 on objectives stated differently -> price of $1k NPV in $k of risk removed, plan")
for name, (s_npv, s_risk) in scales.items():
    w_npv, w_risk = 0.5 / s_npv, 0.5 / s_risk          # the weights on the $k objectives
    npv, risk = score(sm, weighted(sm, w_npv, w_risk))
    print(f"  {name:22}: price {w_npv / w_risk:8.3f}, NPV ${npv:,}k, risk removed ${risk:,.0f}k")
