"""The Weibull hazard for four shapes, and why a hazard is a rate, not a probability."""

from scipy.stats import weibull_min

from asset_curves import hazard, pof_next

ETA = 40
print(f"hazard h(t) per year, eta = {ETA} years")
print(f"{'shape beta':>10} " + " ".join(f"{'age ' + str(t):>8}" for t in (5, 20, 40, 60)) + "   trend")
for beta in (0.7, 1.0, 2.0, 3.5):
    h = [hazard(t, beta, ETA) for t in (5, 20, 40, 60)]
    trend = "falls" if h[-1] < h[0] else "flat" if h[-1] == h[0] else "rises"
    print(f"{beta:>10} " + " ".join(f"{v:>8.4f}" for v in h) + f"   {trend}")

curve = weibull_min(c=3.5, scale=ETA)
t = 40
print(f"beta 3.5 at age {t}: pdf/sf from scipy {curve.pdf(t) / curve.sf(t):.4f}, formula {hazard(t, 3.5, ETA):.4f}")

print("an old asset far past its scale (beta 4, eta 20):")
for age in (30, 40, 50):
    print(f"  age {age}: hazard {hazard(age, 4, 20):.3f} per year, PoF next year {pof_next(age, 4, 20):.3f}")
