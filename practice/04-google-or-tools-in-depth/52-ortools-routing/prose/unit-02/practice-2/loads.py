from __future__ import annotations

from ortools.constraint_solver import pywrapcp


def add_loads(routing, manager, demands: dict[str, list[int]], capacities: dict[str, list[int]]) -> None:
    """One dimension per kind of load, named after it: demands[kind][node] is what a stop adds,
    capacities[kind][v] is the most vehicle v may carry of that kind."""
    # TODO: for each kind, a unary demand callback and a capacity dimension named after the kind.
    return None


def build(distance: list[list[int]], vehicles: int, demands, capacities):
    """Given: one route per vehicle from the depot (node 0), priced by distance."""
    manager = pywrapcp.RoutingIndexManager(len(distance), vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def arc(from_index, to_index):
        return distance[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(arc))
    add_loads(routing, manager, demands, capacities)
    return manager, routing


if __name__ == "__main__":
    manager, routing = build([[0, 4, 5], [4, 0, 3], [5, 3, 0]], 1,
                             {"crates": [0, 2, 3], "kg": [0, 40, 70]}, {"crates": [6], "kg": [100]})
    print(routing.ReadAssignmentFromRoutes([[1, 2]], True) is not None)
