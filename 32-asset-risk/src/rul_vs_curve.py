"""GridCap small: how far the predicted RUL sits from the median remaining life of each asset's curve."""

from asset_curves import residual_median
from gridcap import generate

small = generate("small")
pairs = [(a, residual_median(a.age, a.weibull_beta, a.weibull_eta)) for a in small.assets]
floor = [(a, m) for a, m in pairs if a.rul == 1]
rest = [(a, m) for a, m in pairs if a.rul > 1]
print(f"{len(pairs)} assets; {len(floor)} have RUL 1, the floor the prediction cannot go below")
print(f"  their curves' median remaining life: {min(m for _, m in floor):.1f} to {max(m for _, m in floor):.1f} years")
gap = sum(a.rul - m for a, m in rest) / len(rest)
print(f"the other {len(rest)}: RUL minus the curve's median, on average {gap:+.1f} years")
