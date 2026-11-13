"""References taken from the candidates move when a candidate leaves, and the ranking moves with them."""

from benefits import earliest_measures
from gridcap import generate
from value_function import MEASURES, REFERENCE, WEIGHTS, ranking, raw, value

small = generate("small")
benefits = {pid: raw(m) for pid, m in earliest_measures(small).items()}
others = [pid for pid in benefits if pid != "P006"]       # the 39 projects ranked in every row


def best_of(pids):
    return {k: max(benefits[p][k] for p in pids) for k in MEASURES}


print("top five of the 39 projects other than P006, by the reference used:")
for label, reference in (("best of all 40 (P006 in)", best_of(benefits)),
                         ("best of the 39 (P006 withdrawn)", best_of(others)),
                         ("fixed swing, P006 in", REFERENCE),
                         ("fixed swing, P006 withdrawn", REFERENCE)):
    order = ranking({p: value(benefits[p], reference, WEIGHTS) for p in others})
    print(f"  {label:31}: {' '.join(order[:5])}")
print("measures in which P006 is the best of all 40:",
      [k for k in MEASURES if benefits["P006"][k] == best_of(benefits)[k]])
print(f"P006's reliability score against the fixed swing: {benefits['P006']['reliability'] / REFERENCE['reliability']:.2f}")
