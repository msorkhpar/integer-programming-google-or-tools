"""Lesson 3.2.1: branch the tiny selection model until every leaf is infeasible or integral (no pruning by bound)."""

from bnb import branch_and_bound, show
from gridcap import generate
from selection import build

search = branch_and_bound(build(generate("tiny")), prune=False)
show(search)
leaves = [s for s in search.steps if not s.action.startswith("branch")]
print(f"{len(search.steps)} nodes, {len(leaves)} leaves; best integral leaf {search.value:,.0f}: {', '.join(search.plan)}")
