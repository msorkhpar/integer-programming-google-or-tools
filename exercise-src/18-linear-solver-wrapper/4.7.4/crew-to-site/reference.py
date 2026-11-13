from __future__ import annotations

from ortools.graph.python import linear_sum_assignment


def assign(crews: list[str], sites: list[str], cost: dict):
    """Each site gets one crew, each crew at most one site, at least total cost.

    cost: {(crew, site): whole-number cost} over the allowed pairs only. Returns
    (total, {crew: site}) for the crews that got a site, or None if no such assignment exists.
    """
    lsa = linear_sum_assignment.SimpleLinearSumAssignment()
    for (crew, site), c in cost.items():
        lsa.add_arc_with_cost(crews.index(crew), sites.index(site), c)
    for dummy in range(len(sites), len(crews)):              # "no site": any crew, cost 0
        for i in range(len(crews)):
            lsa.add_arc_with_cost(i, dummy, 0)
    if lsa.solve() != lsa.OPTIMAL:
        return None
    plan = {crews[i]: sites[lsa.right_mate(i)] for i in range(len(crews)) if lsa.right_mate(i) < len(sites)}
    return lsa.optimal_cost(), plan


if __name__ == "__main__":
    print(assign(["A", "B"], ["north", "south"], {("A", "north"): 3, ("A", "south"): 5, ("B", "north"): 4, ("B", "south"): 9}))
