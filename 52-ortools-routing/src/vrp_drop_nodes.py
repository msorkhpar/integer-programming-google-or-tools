# Adapted from the OR-Tools example vrp_drop_nodes.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_drop_nodes.py
# (Apache-2.0). Same data and model. One change: the example stops guided local search after
# 1 second; this copy stops it after 100 solutions, so every run prints the same routes.
"""Demands sum to 70 but four vehicles carry 60: every location is optional, at a penalty of 1000."""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from guide_data import depot, distance_matrix, num_vehicles, vehicle_capacities
from guide_data import drop_demands as demands

manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)
transit_callback_index = routing.RegisterTransitCallback(
    lambda i, j: distance_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)])
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
demand_callback_index = routing.RegisterUnaryTransitCallback(lambda i: demands[manager.IndexToNode(i)])
routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, vehicle_capacities, True, "Capacity")

# Allow to drop nodes: one disjunction per location, each holding that one location.
penalty = 1000
for node in range(1, len(distance_matrix)):
    routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
search_parameters.solution_limit = 100
solution = routing.SolveWithParameters(search_parameters)

print(f"Objective: {solution.ObjectiveValue()}")
dropped_nodes = [manager.IndexToNode(node) for node in range(routing.Size())
                 if not routing.IsStart(node) and not routing.IsEnd(node)
                 and solution.Value(routing.NextVar(node)) == node]
print("Dropped nodes:", *dropped_nodes, f"(demand {sum(demands[n] for n in dropped_nodes)})")
distance = 0
for vehicle_id in range(num_vehicles):
    index, stops = routing.Start(vehicle_id), []
    while not routing.IsEnd(index):
        stops.append(manager.IndexToNode(index))
        previous_index, index = index, solution.Value(routing.NextVar(index))
        distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
    print(f"vehicle {vehicle_id}: {' -> '.join(map(str, stops + [depot]))}  load {sum(demands[n] for n in stops)}")
print(f"distance {distance} + {len(dropped_nodes)} x {penalty} = {distance + penalty * len(dropped_nodes)}")
