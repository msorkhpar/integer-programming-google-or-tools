# Adapted from the OR-Tools example vrp_global_span.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_global_span.py
# (Apache-2.0). Same data, calls and search; the printing is shortened.
"""Four vehicles, 16 locations: a distance dimension caps each route and the global span balances them."""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from guide_data import depot, distance_matrix, num_vehicles

manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)


def distance_callback(from_index, to_index):
    return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# A dimension named "Distance": no slack, at most 3000 m per vehicle, every route starts at 0.
routing.AddDimension(transit_callback_index, 0, 3000, True, "Distance")
distance_dimension = routing.GetDimensionOrDie("Distance")
# Add 100 x (longest route - shortest start) to the objective, so the longest route dominates.
distance_dimension.SetGlobalSpanCostCoefficient(100)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
solution = routing.SolveWithParameters(search_parameters)

print(f"Objective: {solution.ObjectiveValue()}")
total = longest = 0
for vehicle_id in range(num_vehicles):
    if not routing.IsVehicleUsed(solution, vehicle_id):
        continue
    index, stops = routing.Start(vehicle_id), []
    while not routing.IsEnd(index):
        stops.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    meters = solution.Value(distance_dimension.CumulVar(index))   # the cumul at the route's end
    total, longest = total + meters, max(longest, meters)
    print(f"vehicle {vehicle_id}: {' -> '.join(map(str, stops + [depot]))}  ({meters} m)")
print(f"total {total} m, longest {longest} m, 100 x {longest} + {total} = {100 * longest + total}")
