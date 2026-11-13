# Adapted from the OR-Tools example vrp_time_windows.py,
# https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_time_windows.py
# (Apache-2.0). Same data, calls and search; the printing is shortened.
"""VRP with time windows: four vehicles, 16 locations, travel times in minutes, one window per location."""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

time_matrix = [
    [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
    [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
    [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
    [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
    [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
    [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
    [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
    [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
    [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
    [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
    [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
    [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
    [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
    [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
    [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
    [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
    [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
]
time_windows = [
    (0, 5),  # depot
    (7, 12),  # 1
    (10, 15),  # 2
    (16, 18),  # 3
    (10, 13),  # 4
    (0, 5),  # 5
    (5, 10),  # 6
    (0, 4),  # 7
    (5, 10),  # 8
    (0, 3),  # 9
    (10, 16),  # 10
    (10, 15),  # 11
    (0, 5),  # 12
    (5, 10),  # 13
    (7, 8),  # 14
    (10, 15),  # 15
    (11, 15),  # 16
]
num_vehicles, depot = 4, 0

manager = pywrapcp.RoutingIndexManager(len(time_matrix), num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)


def time_callback(from_index, to_index):
    return time_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


transit_callback_index = routing.RegisterTransitCallback(time_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

routing.AddDimension(
    transit_callback_index,
    30,     # slack: up to 30 minutes of waiting at each location
    30,     # capacity: no cumul (clock time) above 30
    False,  # don't force the start cumul to zero: a vehicle may leave the depot later
    "Time",
)
time_dimension = routing.GetDimensionOrDie("Time")
for location_idx, (open_, close) in enumerate(time_windows):
    if location_idx == depot:
        continue
    time_dimension.CumulVar(manager.NodeToIndex(location_idx)).SetRange(open_, close)
for vehicle_id in range(num_vehicles):   # the depot's window applies to each vehicle's start
    time_dimension.CumulVar(routing.Start(vehicle_id)).SetRange(*time_windows[depot])
for i in range(num_vehicles):            # pick the earliest feasible start and end times
    routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(i)))
    routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
solution = routing.SolveWithParameters(search_parameters)

print(f"Objective: {solution.ObjectiveValue()}")
total_time = 0
for vehicle_id in range(num_vehicles):
    index, legs = routing.Start(vehicle_id), []
    while True:
        time_var = time_dimension.CumulVar(index)
        legs.append(f"{manager.IndexToNode(index)} Time({solution.Min(time_var)},{solution.Max(time_var)})")
        if routing.IsEnd(index):
            break
        index = solution.Value(routing.NextVar(index))
    total_time += solution.Min(time_var)
    print(f"vehicle {vehicle_id}: {' -> '.join(legs)}")
print(f"Total time of all routes: {total_time}min")
