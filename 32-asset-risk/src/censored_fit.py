"""Fitting beta and eta from a fleet's history: the assets still working count too.

A fictional fleet of 300 poles with a known curve is observed until each pole is 35 years old.
Most poles are still standing then: their lives are right-censored at 35.
"""

import numpy as np
from scipy.stats import CensoredData, weibull_min

TRUE_BETA, TRUE_ETA, OBSERVED_TO = 3.0, 45.0, 35.0
lives = weibull_min.rvs(TRUE_BETA, scale=TRUE_ETA, size=300, random_state=np.random.default_rng(7))
failed = lives[lives <= OBSERVED_TO]
standing = np.full((lives > OBSERVED_TO).sum(), OBSERVED_TO)
print(f"true curve: beta {TRUE_BETA}, eta {TRUE_ETA}; failed by age {OBSERVED_TO:.0f}: {len(failed)}, "
      f"still working: {len(standing)}")

c, _, scale = weibull_min.fit(failed, floc=0)
print(f"fit to the failures only:      beta {c:.2f}, eta {scale:.1f}")

data = CensoredData(uncensored=failed, right=standing)
c, _, scale = weibull_min.fit(data, floc=0)
print(f"fit with the survivors counted: beta {c:.2f}, eta {scale:.1f}")
