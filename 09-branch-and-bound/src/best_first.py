"""Lesson 3.2.3: the tiny tree taken best bound first, next to the depth-first tree of lesson 3.2.2."""

from bnb import branch_and_bound, show
from gridcap import generate
from selection import build

sel = build(generate("tiny"))
best = branch_and_bound(sel, node_rule="best")
show(best)
depth = branch_and_bound(sel, node_rule="depth")
for name, search in (("best-first", best), ("depth-first", depth)):
    print(f"{name:<11}: {len(search.steps):>2} nodes, {search.lps:>2} LPs, at most {search.most_open} waiting, best {search.value:,.0f}")
