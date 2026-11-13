"""The value table does not depend on the units the measures are stated in."""

from benefits import CUSTOMERS_SERVED, measures
from gridcap import generate
from value_function import REFERENCE, WEIGHTS, ranking, raw, value, value_table

small = generate("small")
v = value_table(small)

units = {"reliability": 1 / CUSTOMERS_SERVED, "safety": 100.0, "environmental": 1_000.0, "financial": 1 / 1_000}
reference = {k: REFERENCE[k] * units[k] for k in REFERENCE}
w = {}
for p in small.projects:
    for t in p.starts():
        benefit = {k: b * units[k] for k, b in raw(measures(small, p, t)).items()}
        w[p.project_id, t] = value(benefit, reference, WEIGHTS)
print("new units: SAIDI minutes, incidents per 100, kg CO2e, $M")
print(f"largest change in any coefficient: {max(abs(v[key] - w[key]) for key in v):.1e}")
print("same order of all", len(v), "coefficients:", ranking(v) == ranking(w))

forgot = {k: (REFERENCE[k] if k == "reliability" else reference[k]) for k in REFERENCE}
u = {}
for p in small.projects:
    for t in p.starts():
        benefit = {k: b * units[k] for k, b in raw(measures(small, p, t)).items()}
        u[p.project_id, t] = value(benefit, forgot, WEIGHTS)
print("reliability reference left in customer-minutes: same order:", ranking(v) == ranking(u),
      "| top three", ranking(u)[:3], "instead of", ranking(v)[:3])
