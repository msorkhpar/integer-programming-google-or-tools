from __future__ import annotations

from ortools.graph.python import linear_sum_assignment


def pair(hours: list[list[int | None]]) -> tuple[int, list[int]] | None:
    """Least total hours with depot_of[k] for each crew k; None when no full pairing exists."""
    # TODO: one arc per cleared pair, solve, check the status, read the cost and each crew's depot.
    return 0, []


if __name__ == "__main__":
    print(pair([[4, 3, None], [2, 5, 6], [7, None, 4]]))
