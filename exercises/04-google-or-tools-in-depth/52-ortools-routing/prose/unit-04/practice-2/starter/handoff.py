from __future__ import annotations

from ortools.constraint_solver import pywrapcp


def add_handoffs(routing, manager, distance_dim, pairs: list[tuple[int, int]]) -> None:
    """Each (pickup, delivery) pair is served by one vehicle, which reaches the pickup first."""
    # TODO: declare each pair, and the rows that keep it on one vehicle and in order.
    return None


def build(distance: list[list[int]], vehicles: int, pairs: list[tuple[int, int]]):
    """Given: routes from the depot (node 0), priced by distance, with a Distance dimension."""
    manager = pywrapcp.RoutingIndexManager(len(distance), vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def arc(from_index, to_index):
        return distance[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    handle = routing.RegisterTransitCallback(arc)
    routing.SetArcCostEvaluatorOfAllVehicles(handle)
    routing.AddDimension(handle, 0, 10_000, True, "Distance")
    add_handoffs(routing, manager, routing.GetDimensionOrDie("Distance"), pairs)
    return manager, routing


if __name__ == "__main__":
    manager, routing = build([[0, 4, 6], [4, 0, 3], [6, 3, 0]], 1, [(1, 2)])
    print(routing.ReadAssignmentFromRoutes([[2, 1]], True) is None)
