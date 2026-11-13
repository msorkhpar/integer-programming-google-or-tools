"""GridCap's predicted RUL next to the remaining-life distribution its own Weibull curve implies."""

from scipy.stats import weibull_min

from asset_curves import residual_median
from gridcap import generate

tiny = generate("tiny")


def residual_quantile(curve, age: float, q: float) -> float:
    """Years until the chance of having failed, given working at `age`, reaches q."""
    return curve.isf((1 - q) * curve.sf(age)) - age


print(f"{'asset':5} {'age':>3} {'eta':>5} | {'RUL':>3} {'eta-age':>7} | {'median':>6} {'mean':>5} {'P10':>5} {'P90':>5}")
for a in tiny.assets:
    curve = weibull_min(c=a.weibull_beta, scale=a.weibull_eta)
    mean = curve.expect(lambda t: t, lb=a.age, conditional=True) - a.age
    median = residual_median(a.age, a.weibull_beta, a.weibull_eta)
    assert abs(median - residual_quantile(curve, a.age, 0.5)) < 1e-9
    print(f"{a.asset_id:5} {a.age:>3} {a.weibull_eta:>5} | {a.rul:>3} {a.weibull_eta - a.age:>7.1f} | "
          f"{median:>6.1f} {mean:>5.1f} {residual_quantile(curve, a.age, 0.1):>5.1f} {residual_quantile(curve, a.age, 0.9):>5.1f}")
