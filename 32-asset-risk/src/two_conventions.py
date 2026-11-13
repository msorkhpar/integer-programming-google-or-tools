"""Two ways to count next year's failures: the chance of at least one, or the expected number."""

from asset_curves import failures_next, pof_next
from gridcap import generate

small = generate("small")
gaps = [(failures_next(a.age, a.weibull_beta, a.weibull_eta) - pof_next(a.age, a.weibull_beta, a.weibull_eta), a)
        for a in small.assets]
gap, a = max(gaps, key=lambda g: g[0])
print(f"GridCap small: largest gap {gap:.4f}, on {a.asset_id} (age {a.age}, beta {a.weibull_beta}, "
      f"eta {a.weibull_eta}): PoF {pof_next(a.age, a.weibull_beta, a.weibull_eta):.4f}, "
      f"expected failures {failures_next(a.age, a.weibull_beta, a.weibull_eta):.4f}")
print("one invented worn-out asset, beta 4, eta 20:")
for age in (20, 30, 40):
    print(f"  age {age}: PoF {pof_next(age, 4, 20):.3f}, expected failures {failures_next(age, 4, 20):.3f}")
