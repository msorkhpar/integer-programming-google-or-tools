# Adapted from the OR-Tools example tsp_cities.py, https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/tsp_cities.py (Apache-2.0)
"""One inspection crew's tour of five GridCap substations with the routing library (lesson 4.1.1).

GridCap is fictional; so are these grid positions.
"""

from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

names = ["Depot", "S1 Hilltop", "S2 Riverside", "S3 Harbor", "S4 Prairie", "S5 Mesa"]
where = [(0, 0), (2, 6), (5, 5), (8, 1), (4, -3), (-3, 3)]     # km east, km north
km = [[abs(a[0] - b[0]) + abs(a[1] - b[1]) for b in where] for a in where]

manager = pywrapcp.RoutingIndexManager(len(names), 1, 0)      # stops, vehicles, depot
routing = pywrapcp.RoutingModel(manager)


def distance(from_index: int, to_index: int) -> int:
    return km[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(distance))
params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
solution = routing.SolveWithParameters(params)

status = routing_enums_pb2.RoutingSearchStatus.Value.Name(routing.status())
print("status:", status)
print("possible statuses:", ", ".join(routing_enums_pb2.RoutingSearchStatus.Value.keys()))
index, stops = routing.Start(0), []
while not routing.IsEnd(index):
    stops.append(names[manager.IndexToNode(index)].split()[0])
    index = solution.Value(routing.NextVar(index))
stops.append(names[manager.IndexToNode(index)].split()[0])
print("route:", " -> ".join(stops))
print("length:", solution.ObjectiveValue(), "km")
