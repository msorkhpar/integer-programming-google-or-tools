"""When a reference changes, its weight must change with it, or every exchange rate moves."""

from benefits import earliest_measures
from gridcap import generate
from value_function import REFERENCE, SWING_RATINGS, exchange_rates, ranking, raw, swing_weights, value

small = generate("small")
benefits = {pid: raw(m) for pid, m in earliest_measures(small).items()}
wider = {**REFERENCE, "reliability": 6_000_000}         # the board doubles the reliability swing

cases = {
    "old swing, old ratings": (REFERENCE, SWING_RATINGS),
    "wider swing, old ratings": (wider, SWING_RATINGS),
    "wider swing, re-rated": (wider, {**SWING_RATINGS, "reliability": 200}),
}
base = None
for label, (reference, ratings) in cases.items():
    weights = swing_weights(ratings)
    v = {p: value(b, reference, weights) for p, b in benefits.items()}
    rate = exchange_rates(reference, weights)["reliability"] * 1000
    base = base or v
    ratios = [v[p] / base[p] for p in v]
    print(f"{label:24}: ${rate:.2f} per customer-minute; top five {' '.join(ranking(v)[:5])};"
          f" value / old value between {min(ratios):.4f} and {max(ratios):.4f}")
