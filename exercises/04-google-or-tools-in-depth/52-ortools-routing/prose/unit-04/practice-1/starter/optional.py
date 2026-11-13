from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def make_optional(routing, manager, penalties: dict[int, int]) -> None:
    """Each node in penalties may be skipped at its penalty; every other stop stays required."""
    # TODO: one disjunction per optional node.
    return None


def skipped(routing, manager, solution) -> list[int]:
    """The nodes on no route, in increasing order."""
    # TODO
    return []


def build(distance, demands, capacities, penalties):
    """Given: routes from the depot (node 0) priced by distance, with a load limit per vehicle."""
    manager = pywrapcp.RoutingIndexManager(len(distance), len(capacities), 0)
    routing = pywrapcp.RoutingModel(manager)

    def arc(from_index, to_index):
        return distance[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    def demand(from_index):
        return demands[manager.IndexToNode(from_index)]

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(arc))
    routing.AddDimensionWithVehicleCapacity(routing.RegisterUnaryTransitCallback(demand), 0, capacities, True, "Load")
    make_optional(routing, manager, penalties)
    return manager, routing


def solve(routing):
    """Given: PATH_CHEAPEST_ARC, then the default local search."""
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.time_limit.FromSeconds(5)   # a safety net only: the search ends at a local minimum first
    return routing.SolveWithParameters(params)


if __name__ == "__main__":
    manager, routing = build([[0, 4, 6], [4, 0, 3], [6, 3, 0]], [0, 2, 3], [4], {2: 10})
    print(skipped(routing, manager, solve(routing)))
