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
    # TODO: solve with PATH_CHEAPEST_ARC, then walk vehicle 0's route.
    return [depot, depot], 0


if __name__ == "__main__":
    print(solve_tour([[0, 2, 9, 10], [1, 0, 6, 4], [15, 7, 0, 8], [6, 3, 12, 0]], 0))
