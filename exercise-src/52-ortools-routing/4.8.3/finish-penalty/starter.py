from __future__ import annotations

from ortools.constraint_solver import pywrapcp


def add_overtime_cost(routing, time_dim, finish_by: list[int], cost_per_minute: int) -> None:
    """Each crew v should be back by finish_by[v]; every minute later costs cost_per_minute."""
    # TODO: a soft upper bound on each crew's return.
    return None


def build(travel: list[list[int]], service: list[int], finish_by: list[int], cost_per_minute: int):
    """Given: one route per crew from the depot (node 0), priced in travel minutes, with a Time
    dimension that starts every crew at 0 and adds the work at each stop to the travel."""
    manager = pywrapcp.RoutingIndexManager(len(travel), len(finish_by), 0)
    routing = pywrapcp.RoutingModel(manager)

    def drive(from_index, to_index):
        return travel[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    def busy(from_index, to_index):
        here = manager.IndexToNode(from_index)
        return service[here] + travel[here][manager.IndexToNode(to_index)]

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(drive))
    routing.AddDimension(routing.RegisterTransitCallback(busy), 0, 24 * 60, True, "Time")
    add_overtime_cost(routing, routing.GetDimensionOrDie("Time"), finish_by, cost_per_minute)
    return manager, routing


if __name__ == "__main__":
    manager, routing = build([[0, 5, 9], [5, 0, 6], [9, 6, 0]], [0, 20, 20], [40, 40], 3)
    plan = routing.ReadAssignmentFromRoutes([[1, 2], []], True)
    print(plan.ObjectiveValue() if plan else None)
