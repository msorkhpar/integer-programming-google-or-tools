"""How many plans GridCap allows: every plan checked on tiny, a counted lower bound on small and medium."""

from itertools import combinations
from math import gcd

from gridcap import generate
from selection import broken_rows


def ways_by_project(costs: list[int], budget: int):
    """After each project, ways[b]: how many subsets of the projects so far cost exactly b."""
    ways = [1] + [0] * budget                           # one way to spend nothing: the empty plan
    yield ways
    for c in costs:
        for b in range(budget, c - 1, -1):              # downward, so each project is used at most once
            ways[b] += ways[b - c]
        yield ways


def count_within(costs: list[int], budget: int) -> int:
    """How many subsets of `costs` total at most `budget`."""
    step = 0
    for c in costs:
        step = gcd(step, c)
    step = gcd(step, budget) or 1                       # GridCap costs are multiples of 10: count in steps
    for ways in ways_by_project([c // step for c in costs], budget // step):
        pass
    return sum(ways)


def free_projects(portfolio) -> list:
    """Projects no rule but the budget touches: not must-do, no parent, in no alternative group."""
    return [p for p in portfolio.projects if not p.must_do and not p.parent and not p.alt_group]


if __name__ == "__main__":
    print("costs (2, 3, 4), budget 6: ways[0..6] after each project")
    for k, ways in enumerate(ways_by_project([2, 3, 4], 6)):
        print(f"  after {k} projects: {ways}  total {sum(ways)}")
    tiny = generate("tiny")
    ids = [p.project_id for p in tiny.projects]
    allowed = sum(not broken_rows(tiny, set(c)) for k in range(len(ids) + 1) for c in combinations(ids, k))
    print(f"tiny:     {2 ** len(ids):,} plans, {allowed} allowed")
    for size in ("small", "medium"):
        portfolio = generate(size)
        room = portfolio.capital_budget - sum(p.capex for p in portfolio.projects if p.must_do)
        free = free_projects(portfolio)
        at_least = count_within([p.capex for p in free], room)
        print(f"{size + ':':<9} 2^{len(portfolio.projects)} = {2 ** len(portfolio.projects):.2e} plans, "
              f"at least {at_least:.2e} allowed ({len(free)} free projects, {room:,} left after must-dos)")
