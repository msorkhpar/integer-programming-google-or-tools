"""Use a predicted RUL as the median remaining life: solve for the scale, then read PoF from the curve."""

from scipy.stats import weibull_min

from asset_curves import eta_from_rul, pof_next
from gridcap import generate

tiny = generate("tiny")
print(f"{'asset':5} {'age':>3} {'RUL':>3} {'beta':>5} | {'eta from RUL':>12} {'eta given':>9} | "
      f"{'PoF from RUL':>12} {'PoF given':>9}")
for a in tiny.assets:
    eta = eta_from_rul(a.age, a.rul, a.weibull_beta)
    curve = weibull_min(c=a.weibull_beta, scale=eta)
    assert abs(curve.sf(a.age + a.rul) / curve.sf(a.age) - 0.5) < 1e-9     # RUL is the median
    print(f"{a.asset_id:5} {a.age:>3} {a.rul:>3} {a.weibull_beta:>5} | {eta:>12.1f} {a.weibull_eta:>9} | "
          f"{pof_next(a.age, a.weibull_beta, eta):>12.4f} {pof_next(a.age, a.weibull_beta, a.weibull_eta):>9.4f}")
