from __future__ import annotations

from ortools.sat.python import cp_model


def cheapest_runs(runs: dict[str, tuple[list[int], list[int]]], deadline: int) -> tuple[int, dict[str, tuple[int, int]]]:
    """(total cost, run -> (vehicle index, start hour)) of the cheapest plan that ends by the deadline."""
    # TODO: a vehicle index per run, its hours and cost read by element (or Booleans), an interval
    # with the hours as its size, one NoOverlap, and minimize the total cost. Placeholders below.
    return -1, {r: (-1, -1) for r in runs}


if __name__ == "__main__":
    print(cheapest_runs({"north": ([4, 2], [20, 35]), "harbor": ([3, 1], [15, 30])}, 5))
