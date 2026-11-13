# Adapted from the OR-Tools example vrp_pickup_delivery.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_pickup_delivery.py
# (Apache-2.0). Same data, calls and search; the printing is shortened.
"""Eight items, each picked up at one location and delivered to another by the same vehicle."""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from guide_data import depot, distance_matrix, num_vehicles, pickups_deliveries

manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)


def distance_callback(from_index, to_index):
    return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
routing.AddDimension(transit_callback_index, 0, 3000, True, "Distance")
distance_dimension = routing.GetDimensionOrDie("Distance")
distance_dimension.SetGlobalSpanCostCoefficient(100)

for pickup_node, delivery_node in pickups_deliveries:
    pickup_index = manager.NodeToIndex(pickup_node)
    delivery_index = manager.NodeToIndex(delivery_node)
    routing.AddPickupAndDelivery(pickup_index, delivery_index)
    # The same vehicle does both stops ...
    routing.solver().Add(routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
    # ... and reaches the pickup first (the distance driven so far is smaller there).
    routing.solver().Add(distance_dimension.CumulVar(pickup_index) <= distance_dimension.CumulVar(delivery_index))

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
solution = routing.SolveWithParameters(search_parameters)

print(f"Objective: {solution.ObjectiveValue()}")
total = longest = 0
for vehicle_id in range(num_vehicles):
    index, stops = routing.Start(vehicle_id), []
    while not routing.IsEnd(index):
        stops.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    meters = solution.Value(distance_dimension.CumulVar(index))
    total, longest = total + meters, max(longest, meters)
    print(f"vehicle {vehicle_id}: {' -> '.join(map(str, stops + [depot]))}  ({meters} m)")
print(f"total {total} m, longest {longest} m, 100 x {longest} + {total} = {100 * longest + total}")
