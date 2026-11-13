"""Lesson 3.2.2: the tiny tree again, now pruning every node that cannot beat the incumbent."""

from bnb import branch_and_bound, show
from gridcap import generate
from selection import build

search = branch_and_bound(build(generate("tiny")), prune=True)
show(search)
print(f"{len(search.steps)} nodes, {search.lps} LPs; best plan {search.value:,.0f}: {', '.join(search.plan)}")

print("\nwhere the optimum can be, printed each time the range changes")
incumbent, last = None, None
for step in search.steps:
    if "new incumbent" in step.action:
        incumbent = step.lp.value
    high = max(b for b in (step.waiting_bound, incumbent) if b is not None)
    low = "no plan yet" if incumbent is None else f"{incumbent:,.0f}"
    if (low, high) != last:
        print(f"after node {step.node.id:>2}: between {low} and {high:,.1f}")
        last = (low, high)
