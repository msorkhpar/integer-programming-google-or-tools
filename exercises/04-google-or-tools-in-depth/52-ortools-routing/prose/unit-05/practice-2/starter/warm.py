from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def replan(routing, yesterday: list[list[int]], params):
    """Search from yesterday's routes when they still fit, from scratch when they do not.
    Returns (yesterday's cost today, or None when the routes no longer fit; today's solution)."""
    # TODO
    return None, None


def build(distance: list[list[int]], demands: list[int], capacities: list[int]):
    """Given: routes from the depot (node 0) priced by distance, with a load limit per vehicle."""
    manager = pywrapcp.RoutingIndexManager(len(distance), len(capacities), 0)
    routing = pywrapcp.RoutingModel(manager)
    arc = routing.RegisterTransitCallback(
        lambda i, j: distance[manager.IndexToNode(i)][manager.IndexToNode(j)])
    routing.SetArcCostEvaluatorOfAllVehicles(arc)
    load = routing.RegisterUnaryTransitCallback(lambda i: demands[manager.IndexToNode(i)])
    routing.AddDimensionWithVehicleCapacity(load, 0, capacities, True, "Load")
    return manager, routing


def parameters():
    """Given: a fixed strategy, guided local search, and 50 solutions."""
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.solution_limit = 50
    return params


if __name__ == "__main__":
    manager, routing = build([[0, 4, 6], [4, 0, 3], [6, 3, 0]], [0, 1, 1], [2])
    start, solution = replan(routing, [[2, 1]], parameters())
    print(start, solution.ObjectiveValue() if solution else None)
