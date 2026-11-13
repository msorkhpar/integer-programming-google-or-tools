"""What beta and eta say about a fleet: F(eta), the median, the mean and the B10 life, from scipy."""

from scipy.stats import weibull_min

from gridcap import generate

tiny = generate("tiny")
print(f"{'asset':5} {'kind':12} {'beta':>5} {'eta':>5} | {'F(eta)':>6} {'B10 life':>8} {'median':>6} {'mean':>5}")
for a in tiny.assets:
    curve = weibull_min(c=a.weibull_beta, scale=a.weibull_eta)
    print(f"{a.asset_id:5} {a.kind:12} {a.weibull_beta:>5} {a.weibull_eta:>5} | {curve.cdf(a.weibull_eta):>6.3f} "
          f"{curve.ppf(0.10):>8.1f} {curve.median():>6.1f} {curve.mean():>5.1f}")
