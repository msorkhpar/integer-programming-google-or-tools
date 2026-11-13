"""Lesson 3.2.3: every node rule with every variable rule, on the small portfolio with a budget per year."""

from bnb import branch_and_bound, fractional
from gridcap import generate
from selection import build

small = generate("small")
for yearly in (False, True):
    search = branch_and_bound(build(small, yearly=yearly))
    counts = [len(fractional(s.lp.x)) for s in search.steps if s.lp is not None and s.lp.value is not None]
    rows = "one budget row per year" if yearly else "one capital budget row"
    print(f"{rows:<24}: at most {max(counts)} fractional variables at a node")

sel = build(small, yearly=True)
values = set()
print(f"\n{'node rule':<9} {'variable rule':<13} {'nodes':>6} {'LPs':>6} {'most waiting':>12} {'first plan at node':>18}")
for node_rule in ("depth", "best", "breadth"):
    for var_rule in ("first", "most", "strong"):
        search = branch_and_bound(sel, node_rule=node_rule, var_rule=var_rule)
        first = next(k for k, s in enumerate(search.steps, start=1) if "new incumbent" in s.action)
        values.add(round(search.value))
        print(f"{node_rule:<9} {var_rule:<13} {len(search.steps):>6,} {search.lps:>6,} {search.most_open:>12,} {first:>18,}")
print("best plan of each run:", ", ".join(f"{v:,}" for v in sorted(values)))
