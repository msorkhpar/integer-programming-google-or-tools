"""Scores added across projects need zero to mean no benefit; a min-max scale moves the zero."""

from benefits import earliest_measures
from gridcap import generate
from value_function import MEASURES, WEIGHTS, raw

tiny = generate("tiny")
benefits = {pid: raw(m) for pid, m in earliest_measures(tiny).items()}
low = {k: min(b[k] for b in benefits.values()) for k in MEASURES}
high = {k: max(b[k] for b in benefits.values()) for k in MEASURES}


def min_max(b):          # 0 at the worst candidate, 1 at the best
    return sum(WEIGHTS[k] * (b[k] - low[k]) / (high[k] - low[k]) for k in MEASURES)


def from_zero(b):        # 0 at no benefit, 1 at the best candidate
    return sum(WEIGHTS[k] * b[k] / high[k] for k in MEASURES)


for name, score in (("min-max  ", min_max), ("from zero", from_zero)):
    v = {pid: score(b) for pid, b in benefits.items()}
    pair, single = v["P005"] + v["P008"], v["P002"]
    better = "P005 + P008" if pair > single else "P002"
    print(f"{name}: P005 {v['P005']:.3f} + P008 {v['P008']:.3f} = {pair:.3f}  vs  P002 {single:.3f}  -> {better}")
print("P005's benefit in each measure:", {k: round(benefits["P005"][k], 3) for k in MEASURES})
print("lowest candidate in each measure:", {k: round(low[k], 3) for k in MEASURES})
