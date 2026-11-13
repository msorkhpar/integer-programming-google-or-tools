"""One GridCap asset's failure curve: F, R and f by age, checked against scipy.stats.weibull_min."""

from scipy.stats import weibull_min

from asset_curves import cumulative, density, survival
from gridcap import generate

tiny = generate("tiny")
a = tiny.asset("A006")
beta, eta = a.weibull_beta, a.weibull_eta
print(f"A006 ({a.kind}): beta {beta}, eta {eta} years, age today {a.age}")
print(f"{'age':>4} {'F(t) failed by t':>17} {'R(t) still working':>19} {'f(t) per year':>14}")
for t in (10, 30, 50, 57.8, 70, 90):
    print(f"{t:>4} {cumulative(t, beta, eta):>17.4f} {survival(t, beta, eta):>19.4f} {density(t, beta, eta):>14.4f}")

curve = weibull_min(c=beta, scale=eta)
worst = max(max(abs(curve.cdf(t) - cumulative(t, beta, eta)), abs(curve.sf(t) - survival(t, beta, eta)),
                abs(curve.pdf(t) - density(t, beta, eta))) for t in range(1, 121))
print(f"largest difference from scipy.stats.weibull_min over ages 1-120: {worst:.1e}")
