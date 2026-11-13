from __future__ import annotations

from ortools.sat.python import cp_model


def plan_depot(buses: dict[str, list[tuple[str, int]]]) -> dict[tuple[str, int], int]:
    """Start hour of each step (bus, k), so the last bus leaves as early as possible."""
    # TODO: an interval per step, a NoOverlap per bay, an order row per pair of steps of a bus,
    # and minimize the latest end. Every start below is a placeholder.
    return {(bus, k): -1 for bus, steps in buses.items() for k in range(len(steps))}


if __name__ == "__main__":
    print(plan_depot({"bus1": [("wash", 1), ("service", 3)], "bus2": [("service", 2), ("wash", 1)]}))
