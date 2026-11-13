"""Lesson 3.2.3: the three node rules on the small portfolio with one budget row per year."""

from bnb import branch_and_bound
from gridcap import generate
from selection import build

small = generate("small")
print(f"small: {len(small.projects)} projects, budgets " + ", ".join(f"{y} ${b:,}k" for y, b in small.budget.items()))
sel = build(small, yearly=True)
print(f"{'node rule':<9} {'nodes':>6} {'LPs':>6} {'most waiting':>12} {'first plan at node':>18} {'best':>7}")
for node_rule in ("depth", "best", "breadth"):
    search = branch_and_bound(sel, node_rule=node_rule)
    first = next(k for k, s in enumerate(search.steps, start=1) if "new incumbent" in s.action)
    print(f"{node_rule:<9} {len(search.steps):>6,} {search.lps:>6,} {search.most_open:>12,} {first:>18,} {search.value:>7,.0f}")
