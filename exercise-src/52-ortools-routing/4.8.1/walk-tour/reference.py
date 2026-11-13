from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def build(cost: list[list[int]], depot: int):
    """Given: a one-vehicle routing model whose arc from node a to node b costs cost[a][b]."""
    manager = pywrapcp.RoutingIndexManager(len(cost), 1, depot)
    routing = pywrapcp.RoutingModel(manager)

    def arc(from_index, to_index):
        return cost[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(arc))
    return manager, routing


def solve_tour(cost: list[list[int]], depot: int) -> tuple[list[int], int]:
    """The tour as nodes, from the depot back to the depot, and its total cost."""
    manager, routing = build(cost, depot)
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(params)
    index, tour, total = routing.Start(0), [], 0
    while not routing.IsEnd(index):
        tour.append(manager.IndexToNode(index))
        following = solution.Value(routing.NextVar(index))
        total += routing.GetArcCostForVehicle(index, following, 0)
        index = following
    tour.append(manager.IndexToNode(index))
    return tour, total


if __name__ == "__main__":
    print(solve_tour([[0, 2, 9, 10], [1, 0, 6, 4], [15, 7, 0, 8], [6, 3, 12, 0]], 0))
