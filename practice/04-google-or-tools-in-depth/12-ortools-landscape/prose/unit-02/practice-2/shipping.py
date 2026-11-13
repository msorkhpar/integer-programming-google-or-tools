from __future__ import annotations

from ortools.graph.python import min_cost_flow


def ship(lanes: list[tuple[int, int, int, int]], supply: dict[int, int]) -> int | str:
    """The least total cost, or the status name when the solver's status is not OPTIMAL."""
    # TODO: add each lane, set each node's supply, solve, and check the status before the cost.
    return -1


if __name__ == "__main__":
    print(ship([(0, 1, 5, 2), (0, 2, 5, 4), (2, 1, 5, 1)], {0: 7, 1: -7}))
