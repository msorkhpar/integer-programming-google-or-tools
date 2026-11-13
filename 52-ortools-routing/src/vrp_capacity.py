# Adapted from the OR-Tools example vrp_capacity.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_capacity.py
# (Apache-2.0). Same data and model. One change: the example stops guided local search after
# 1 second; this copy stops it after 100 solutions, so every run prints the same routes.
"""Capacitated VRP: four vehicles of capacity 15 pick up demands that sum to exactly 60."""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from guide_data import capacity_demands as demands
from guide_data import depot, distance_matrix, num_vehicles, vehicle_capacities

manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)


def distance_callback(from_index, to_index):
    return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


def demand_callback(from_index):
    """A unary callback: the load picked up at one node, whatever comes next."""
    return demands[manager.IndexToNode(from_index)]


demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,                    # null capacity slack
    vehicle_capacities,   # one maximum load per vehicle
    True,                 # start cumul to zero: every vehicle leaves the depot empty
    "Capacity",
)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
search_parameters.solution_limit = 100
solution = routing.SolveWithParameters(search_parameters)

capacity_dimension = routing.GetDimensionOrDie("Capacity")
print(f"Objective: {solution.ObjectiveValue()}")
for vehicle_id in range(num_vehicles):
    index, legs = routing.Start(vehicle_id), []
    while not routing.IsEnd(index):
        load = solution.Value(capacity_dimension.CumulVar(index))
        legs.append(f"{manager.IndexToNode(index)} Load({load})")
        index = solution.Value(routing.NextVar(index))
    legs.append(f"{depot} Load({solution.Value(capacity_dimension.CumulVar(index))})")
    print(f"vehicle {vehicle_id}: {' -> '.join(legs)}")
