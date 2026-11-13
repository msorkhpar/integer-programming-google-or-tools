from __future__ import annotations

from ortools.graph.python import linear_sum_assignment


def assign(crews: list[str], sites: list[str], cost: dict):
    """Each site gets one crew, each crew at most one site, at least total cost.

    cost: {(crew, site): whole-number cost} over the allowed pairs only. Returns
    (total, {crew: site}) for the crews that got a site, or None if no such assignment exists.
    """
    # TODO: build a SimpleLinearSumAssignment, square it if needed, solve, and read the plan.
    return 0, {}


if __name__ == "__main__":
    print(assign(["A", "B"], ["north", "south"], {("A", "north"): 3, ("A", "south"): 5, ("B", "north"): 4, ("B", "south"): 9}))
