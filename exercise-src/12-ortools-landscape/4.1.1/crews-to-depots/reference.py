from __future__ import annotations

from ortools.graph.python import linear_sum_assignment


def pair(hours: list[list[int | None]]) -> tuple[int, list[int]] | None:
    """Least total hours with depot_of[k] for each crew k; None when no full pairing exists."""
    solver = linear_sum_assignment.SimpleLinearSumAssignment()
    for k, row in enumerate(hours):
        for d, h in enumerate(row):
            if h is not None:
                solver.add_arc_with_cost(k, d, h)
    if solver.solve() != solver.OPTIMAL:
        return None
    return solver.optimal_cost(), [solver.right_mate(k) for k in range(len(hours))]


if __name__ == "__main__":
    print(pair([[4, 3, None], [2, 5, 6], [7, None, 4]]))
