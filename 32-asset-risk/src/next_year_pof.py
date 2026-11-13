"""Next year's PoF, conditional on working today, three ways: survival ratio, scipy, cumulative hazard."""

import math

from scipy.stats import weibull_min

from asset_curves import cumulative, cumulative_hazard, pof_next
from gridcap import generate

tiny = generate("tiny")
print(f"{'asset':5} {'age':>3} {'beta':>5} {'eta':>5} | {'PoF next':>8} {'scipy':>7} {'1-e^-dL':>8} | {'F(a+1)-F(a)':>11} {'F(a)':>6}")
for a in tiny.assets:
    b, e, age = a.weibull_beta, a.weibull_eta, a.age
    conditional = pof_next(age, b, e)
    curve = weibull_min(c=b, scale=e)
    from_scipy = 1 - curve.sf(age + 1) / curve.sf(age)
    from_hazard = 1 - math.exp(-(cumulative_hazard(age + 1, b, e) - cumulative_hazard(age, b, e)))
    unconditional = cumulative(age + 1, b, e) - cumulative(age, b, e)
    failed_by_now = curve.cdf(age)
    print(f"{a.asset_id:5} {age:>3} {b:>5} {e:>5} | {conditional:>8.4f} {from_scipy:>7.4f} {from_hazard:>8.4f} | {unconditional:>11.4f} {failed_by_now:>6.4f}")
