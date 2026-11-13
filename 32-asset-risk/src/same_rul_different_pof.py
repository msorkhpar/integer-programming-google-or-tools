"""Two assets with the same age and the same median RUL, and very different chances of failing soon."""

from scipy.optimize import brentq

from asset_curves import cumulative, pof_next, residual_median

AGE, RUL = 30, 10
print(f"both assets: age {AGE}, median remaining life {RUL} years")
for beta in (1.0, 6.0):
    eta = brentq(lambda e: residual_median(AGE, beta, e) - RUL, 1, 500)
    within_5 = 1 - (1 - cumulative(AGE + 5, beta, eta)) / (1 - cumulative(AGE, beta, eta))
    print(f"  beta {beta}: eta {eta:5.1f}, PoF next year {pof_next(AGE, beta, eta):.3f}, "
          f"fails within 5 years {within_5:.3f}")
