"""Lesson 14.3.1: the asset team's worst-first list against a model, on a fictional 500-unit fleet.

The fleet is generated (GridCap is fictional); the code is snapshot steps/01.
"""

from collections import Counter

import steps

steps.use(1)
from renewal.fleet import generate_fleet, risk          # noqa: E402
from renewal.plan import plan                           # noqa: E402
from renewal.rank import worst_first                    # noqa: E402
from renewal.report import summarize                    # noqa: E402
from renewal.request import Request                     # noqa: E402

BUDGET = 10_000                                         # $k for 2027


def best_ratio_first(fleet, budget):
    """A better ranking: risk removed per $k, skipping any unit that no longer fits."""
    chosen, spent = [], 0
    for t in sorted(fleet, key=lambda t: (-risk(t) / t.cost, t.tid)):
        if spent + t.cost <= budget:
            chosen.append(t.tid)
            spent += t.cost
    return chosen


fleet = generate_fleet(500)
by_id = {t.tid: t for t in fleet}
kinds = Counter(t.kind for t in fleet)
print(f"fleet: {len(fleet)} units in {len({t.substation for t in fleet})} substations; "
      f"{kinds['small']} small, {kinds['medium']} medium, {kinds['large']} large; "
      f"risk this year ${sum(risk(t) for t in fleet):,.0f}k")

ranking = worst_first(fleet, BUDGET)
ratio = best_ratio_first(fleet, BUDGET)
model = plan(fleet, Request(budget=BUDGET))
lists = {"worst first": ranking, "risk per $ first": ratio, "model": sorted(model.replace)}
for name, chosen in lists.items():
    s = summarize(fleet, chosen)
    print(f"{name:16}: {s.units:2} units, ${s.spend:,}k of ${BUDGET:,}k, risk removed ${s.risk_removed:,.0f}k")
print(f"model status {model.status}, bound ${model.bound:,.0f}k")

print("the worst-first list, top five:")
for tid in ranking[:5]:
    t = by_id[tid]
    print(f"  {tid} {t.kind:6} age {t.age}  condition {t.condition:3}  PoF {t.pof:.3f}  CoF ${t.cof:,}k  "
          f"risk ${risk(t):,.0f}k  cost ${t.cost:,}k  in model: {'yes' if tid in model.replace else 'no'}")
print(f"units on both lists: {len(set(ranking) & set(model.replace))} of {len(ranking)}")

left = BUDGET - summarize(fleet, ratio).spend
print(f"risk per $ first leaves ${left:,}k unspent; the model removes "
      f"${model.value - summarize(fleet, ratio).risk_removed:,.0f}k more")

steps.show(1)
