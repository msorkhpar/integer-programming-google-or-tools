"""Adding raw measures: the unit of each measure decides which project wins."""

from benefits import CUSTOMERS_SERVED, earliest_measures
from gridcap import generate
from value_function import ranking, raw

tiny = generate("tiny")
benefits = {pid: raw(m) for pid, m in earliest_measures(tiny).items()}


def raw_sum(benefit: dict[str, float]) -> float:
    return sum(benefit.values())


in_minutes = {pid: raw_sum(b) for pid, b in benefits.items()}
# The same benefits, with reliability stated as SAIDI minutes instead of customer-minutes.
in_saidi = {pid: raw_sum({**b, "reliability": b["reliability"] / CUSTOMERS_SERVED}) for pid, b in benefits.items()}
print("raw sum, reliability in customer-minutes:", " ".join(ranking(in_minutes)))
print("raw sum, reliability in SAIDI minutes:   ", " ".join(ranking(in_saidi)))
for pid in ("P003", "P004"):
    print(f"  {pid}: {in_minutes[pid]:12,.1f} vs {in_saidi[pid]:8,.1f}")
