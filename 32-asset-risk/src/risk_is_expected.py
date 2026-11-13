"""Risk is an expected cost: simulate one asset's failures over many years and average the cost."""

import numpy as np

from asset_curves import pof_next
from gridcap import generate

a = generate("tiny").asset("A006")
pof = pof_next(a.age, a.weibull_beta, a.weibull_eta)
print(f"A006: PoF next year {pof:.4f}, CoF ${a.cof:,}k, risk = PoF x CoF = ${pof * a.cof:,.1f}k per year")

rng = np.random.default_rng(2027)
fails = rng.random(100_000) < pof              # 100,000 imagined copies of next year
cost = np.where(fails, a.cof, 0)
print(f"in 100,000 simulated years: failure years {fails.sum():,}, cost in any one year: "
      f"{sorted(set(cost.tolist()))}, average ${cost.mean():,.1f}k")
