"""Arc costs must be integers: what a float callback does, and how scaling keeps precision."""

import math

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import MINUTES_PER_KM, sites

places = sites(urgent_only=True)


def solve_tour(cost):
    """A one-crew tour of `places` whose arc cost is cost(from_node, to_node)."""
    manager = pywrapcp.RoutingIndexManager(len(places), 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    callback = routing.RegisterTransitCallback(
        lambda i, j: cost(manager.IndexToNode(i), manager.IndexToNode(j)))
    routing.SetArcCostEvaluatorOfAllVehicles(callback)
    parameters = pywrapcp.DefaultRoutingSearchParameters()
    parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(parameters)
    index, tour = routing.Start(0), []
    while not routing.IsEnd(index):
        tour.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    return solution.ObjectiveValue(), tour + [0]


def exact_minutes(a: int, b: int) -> float:
    return MINUTES_PER_KM * math.dist((places[a].x, places[a].y), (places[b].x, places[b].y))


try:
    solve_tour(exact_minutes)
except Exception as error:   # the solver cannot use a float arc cost
    print(f"float callback: {type(error).__name__}")

for scale, unit in ((1, "whole minutes"), (10, "tenths of a minute")):
    objective, tour = solve_tour(lambda a, b: round(scale * exact_minutes(a, b)))
    true_length = sum(exact_minutes(a, b) for a, b in zip(tour, tour[1:]))
    print(f"cost in {unit}: objective {objective} = {objective / scale:.1f} min, "
          f"tour {tour}, exact length {true_length:.2f} min")
