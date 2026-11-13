from __future__ import annotations

from ortools.constraint_solver import pywrapcp


def build(cost: list[list[int]], depot: int):
    """A one-vehicle routing model whose arc from node a to node b costs cost[a][b]."""
    manager = pywrapcp.RoutingIndexManager(len(cost), 1, depot)
    routing = pywrapcp.RoutingModel(manager)
    # TODO: a transit callback that prices one arc, registered, and set as every vehicle's arc cost.
    return manager, routing


def scaled(km: list[list[float]], scale: int) -> list[list[int]]:
    """Integer arc costs: every distance times scale, rounded to the nearest integer."""
    # TODO
    return [[0 for d in row] for row in km]


if __name__ == "__main__":
    grid = scaled([[0, 1.25, 2.5], [1.25, 0, 1.8], [2.5, 1.8, 0]], 100)
    manager, routing = build(grid, 0)
    plan = routing.ReadAssignmentFromRoutes([[1, 2]], True)
    print(grid, plan.ObjectiveValue() if plan else None)
