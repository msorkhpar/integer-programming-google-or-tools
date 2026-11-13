"""Lesson 3.2.2: every plan's value is a whole number of $k, so a bound can be rounded down before the test."""

import math

from bnb import branch_and_bound
from gridcap import generate
from selection import build

print(f"a node with LP bound 25,336.4 against an incumbent of 25,336: "
      f"{'prune' if math.floor(25336.4) <= 25336 else 'branch'} after rounding")
sel = build(generate("small"))
for round_bound in (False, True):
    search = branch_and_bound(sel, round_bound=round_bound)
    print(f"small, bound rounded down: {round_bound!s:5}  {len(search.steps)} nodes, {search.lps} LPs,"
          f" best {search.value:,.0f}")
