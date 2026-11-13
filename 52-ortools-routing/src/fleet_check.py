"""Two crews cannot carry the 33 kits the Valley needs. What the routing solver says about it.

The drive times are fictional (valley.py invents the map from a seed).
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import drive_minutes, sites

places = sites()
minutes = drive_minutes(places)
CREWS, KITS_PER_TRUCK = 2, 12

needed, carried = sum(s.kits for s in places), CREWS * KITS_PER_TRUCK
print(f"kits needed {needed}, kits carried {carried}: {'cannot fit' if needed > carried else 'may fit'}")

manager = pywrapcp.RoutingIndexManager(len(places), CREWS, 0)
routing = pywrapcp.RoutingModel(manager)
drive_index = routing.RegisterTransitCallback(
    lambda i, j: minutes[manager.IndexToNode(i)][manager.IndexToNode(j)])
routing.SetArcCostEvaluatorOfAllVehicles(drive_index)
kits_index = routing.RegisterUnaryTransitCallback(lambda i: places[manager.IndexToNode(i)].kits)
routing.AddDimensionWithVehicleCapacity(kits_index, 0, [KITS_PER_TRUCK] * CREWS, True, "Kits")

parameters = pywrapcp.DefaultRoutingSearchParameters()
parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
parameters.time_limit.FromSeconds(2)    # the CVRP guide's advice: an unsolvable search can run for a long time
solution = routing.SolveWithParameters(parameters)
status = routing_enums_pb2.RoutingSearchStatus.Value.Name(routing.status())
print(f"solution: {solution}, status: {status}")
