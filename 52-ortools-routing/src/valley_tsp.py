"""One crew, the eight urgent Valley sites: the shortest drive that visits each once (a TSP).

Adapted onto GridCap from the OR-Tools example tsp_cities.py,
https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/tsp_cities.py
The drive times are fictional (valley.py invents the map from a seed).
"""

from itertools import permutations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import drive_minutes, sites

places = sites(urgent_only=True)
minutes = drive_minutes(places)
YARD = 0

manager = pywrapcp.RoutingIndexManager(len(places), 1, YARD)
routing = pywrapcp.RoutingModel(manager)


def drive(from_index, to_index):
    """Minutes from one stop to the next; the solver speaks in indices, the matrix in nodes."""
    return minutes[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


drive_index = routing.RegisterTransitCallback(drive)
routing.SetArcCostEvaluatorOfAllVehicles(drive_index)

parameters = pywrapcp.DefaultRoutingSearchParameters()
parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
solution = routing.SolveWithParameters(parameters)


def route_of(vehicle: int) -> list[int]:
    """The nodes vehicle drives through, from its start to its end, read off the NextVar values."""
    index, nodes = routing.Start(vehicle), []
    while not routing.IsEnd(index):
        nodes.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    return nodes + [manager.IndexToNode(index)]


tour = route_of(0)
print("route:", " -> ".join(places[n].name for n in tour))
print("nodes:", tour)
print(f"drive minutes (objective): {solution.ObjectiveValue()}")
print("drive minutes, arc by arc:", " + ".join(str(minutes[a][b]) for a, b in zip(tour, tour[1:])))

# A check the routing library does not give: try every order of the 8 sites (8! = 40,320 tours).
best = min(permutations(range(1, len(places))),
           key=lambda order: sum(minutes[a][b] for a, b in zip((YARD, *order), (*order, YARD))))
best_minutes = sum(minutes[a][b] for a, b in zip((YARD, *best), (*best, YARD)))
print(f"brute force over every order: best {best_minutes} minutes")
