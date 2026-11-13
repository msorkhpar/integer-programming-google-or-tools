"""How far the safety rating can move before the top of the ranking changes."""

from benefits import earliest_measures
from gridcap import generate
from value_function import REFERENCE, SWING_RATINGS, ranking, raw, swing_weights, value

small = generate("small")
benefits = {pid: raw(m) for pid, m in earliest_measures(small).items()}

previous = None
for rating in range(0, 201, 10):
    weights = swing_weights({**SWING_RATINGS, "safety": rating})
    top = ranking({p: value(b, REFERENCE, weights) for p, b in benefits.items()})[:5]
    if top != previous or rating == 200:
        print(f"safety rating {rating:3} (weight {weights['safety']:.3f}): top five {' '.join(top)}")
    previous = top
