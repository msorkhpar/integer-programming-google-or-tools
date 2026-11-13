"""Dividing each measure by a reference in the same unit: the units cancel, so the ranking stays."""

from benefits import CUSTOMERS_SERVED, earliest_measures
from gridcap import generate
from value_function import REFERENCE, WEIGHTS, normalized, ranking, raw, value

tiny = generate("tiny")
benefits = {pid: raw(m) for pid, m in earliest_measures(tiny).items()}

# Second unit system: SAIDI minutes, $M and kg CO2e. Each reference is restated in its new unit too.
scale = {"reliability": 1 / CUSTOMERS_SERVED, "safety": 1.0, "environmental": 1_000.0, "financial": 1 / 1_000}
benefits_2 = {pid: {k: b[k] * scale[k] for k in b} for pid, b in benefits.items()}
reference_2 = {k: REFERENCE[k] * scale[k] for k in REFERENCE}

print("reference, first units: ", REFERENCE)
print("reference, second units:", {k: round(r, 3) for k, r in reference_2.items()})
p3_1 = normalized(benefits["P003"], REFERENCE)
p3_2 = normalized(benefits_2["P003"], reference_2)
print("P003 scores, first units: ", {k: round(s, 4) for k, s in p3_1.items()})
print("P003 scores, second units:", {k: round(s, 4) for k, s in p3_2.items()})

v1 = {pid: value(b, REFERENCE, WEIGHTS) for pid, b in benefits.items()}
v2 = {pid: value(b, reference_2, WEIGHTS) for pid, b in benefits_2.items()}
print("normalized, first units: ", " ".join(ranking(v1)))
print("normalized, second units:", " ".join(ranking(v2)))
print("largest difference in value:", f"{max(abs(v1[p] - v2[p]) for p in v1):.1e}")
