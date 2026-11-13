# Adapted from the OR-Tools example tsp_cities.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/tsp_cities.py
# (Apache-2.0). Same data and calls; the printing is shortened.
"""The OR-Tools TSP example: one vehicle, 13 cities, distances in miles, the depot is city 0."""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

distance_matrix = [
    [0, 2451, 713, 1018, 1631, 1374, 2408, 213, 2571, 875, 1420, 2145, 1972],
    [2451, 0, 1745, 1524, 831, 1240, 959, 2596, 403, 1589, 1374, 357, 579],
    [713, 1745, 0, 355, 920, 803, 1737, 851, 1858, 262, 940, 1453, 1260],
    [1018, 1524, 355, 0, 700, 862, 1395, 1123, 1584, 466, 1056, 1280, 987],
    [1631, 831, 920, 700, 0, 663, 1021, 1769, 949, 796, 879, 586, 371],
    [1374, 1240, 803, 862, 663, 0, 1681, 1551, 1765, 547, 225, 887, 999],
    [2408, 959, 1737, 1395, 1021, 1681, 0, 2493, 678, 1724, 1891, 1114, 701],
    [213, 2596, 851, 1123, 1769, 1551, 2493, 0, 2699, 1038, 1605, 2300, 2099],
    [2571, 403, 1858, 1584, 949, 1765, 678, 2699, 0, 1744, 1645, 653, 600],
    [875, 1589, 262, 466, 796, 547, 1724, 1038, 1744, 0, 679, 1272, 1162],
    [1420, 1374, 940, 1056, 879, 225, 1891, 1605, 1645, 679, 0, 1017, 1200],
    [2145, 357, 1453, 1280, 586, 887, 1114, 2300, 653, 1272, 1017, 0, 504],
    [1972, 579, 1260, 987, 371, 999, 701, 2099, 600, 1162, 1200, 504, 0],
]
num_vehicles, depot = 1, 0

# 1. The index manager: number of nodes, number of vehicles, the depot node.
manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
# 2. The routing model, built on the manager.
routing = pywrapcp.RoutingModel(manager)


# 3. The transit callback: the solver passes two routing indices; turn them into nodes, look up the arc.
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
# 4. The arc cost: every vehicle pays the callback's value for every arc it drives.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# 5. The search parameters: how to build the first solution.
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

# 6. Solve, then walk vehicle 0's route from its start to its end.
solution = routing.SolveWithParameters(search_parameters)
print(f"Objective: {solution.ObjectiveValue()} miles")
index = routing.Start(0)
stops, route_distance = [], 0
while not routing.IsEnd(index):
    stops.append(manager.IndexToNode(index))
    previous_index = index
    index = solution.Value(routing.NextVar(index))
    route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
stops.append(manager.IndexToNode(index))
print("Route for vehicle 0:", " -> ".join(map(str, stops)))
print(f"Route distance: {route_distance} miles")
