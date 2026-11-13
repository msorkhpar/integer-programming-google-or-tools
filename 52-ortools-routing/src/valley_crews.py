"""Three crews, all 18 Valley sites: each truck carries 12 oil-sample kits and drives at most 150 minutes.

Adapted onto GridCap from the OR-Tools examples vrp_capacity.py and vrp_global_span.py,
https://github.com/google/or-tools/tree/v9.15/ortools/constraint_solver/samples
The drive times are fictional (valley.py invents the map from a seed).
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import drive_minutes, sites

places = sites()
minutes = drive_minutes(places)
CREWS, KITS_PER_TRUCK, MAX_DRIVE, YARD = 3, 12, 150, 0


def solve(span_coefficient: int):
    manager = pywrapcp.RoutingIndexManager(len(places), CREWS, YARD)
    routing = pywrapcp.RoutingModel(manager)

    def drive(from_index, to_index):
        return minutes[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    drive_index = routing.RegisterTransitCallback(drive)
    routing.SetArcCostEvaluatorOfAllVehicles(drive_index)
    # Drive: cumulative minutes behind the wheel, at most MAX_DRIVE for each crew.
    routing.AddDimension(drive_index, 0, MAX_DRIVE, True, "Drive")
    routing.GetDimensionOrDie("Drive").SetGlobalSpanCostCoefficient(span_coefficient)

    def kits(from_index):
        return places[manager.IndexToNode(from_index)].kits

    kits_index = routing.RegisterUnaryTransitCallback(kits)
    # Kits: cumulative kits used, at most KITS_PER_TRUCK for each crew.
    routing.AddDimensionWithVehicleCapacity(kits_index, 0, [KITS_PER_TRUCK] * CREWS, True, "Kits")

    parameters = pywrapcp.DefaultRoutingSearchParameters()
    parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    return manager, routing, routing.SolveWithParameters(parameters)


def report(manager, routing, solution) -> None:
    drive_dim, kits_dim = routing.GetDimensionOrDie("Drive"), routing.GetDimensionOrDie("Kits")
    print(f"objective {solution.ObjectiveValue()}")
    for crew in range(CREWS):
        index, names = routing.Start(crew), []
        while not routing.IsEnd(index):
            names.append(places[manager.IndexToNode(index)].name)
            index = solution.Value(routing.NextVar(index))
        print(f"  crew {crew}: {' -> '.join(names[1:])}  drive {solution.Value(drive_dim.CumulVar(index))} min, "
              f"kits {solution.Value(kits_dim.CumulVar(index))}")


print(f"kits needed {sum(s.kits for s in places)}, kits carried {CREWS * KITS_PER_TRUCK}")
print("total drive only (span coefficient 0):")
report(*solve(0))
print("longest drive weighted 100 (span coefficient 100):")
manager, routing, solution = solve(100)
report(manager, routing, solution)

# The cumul and transit of each stop on crew 0's route: cumul(next) = cumul + transit (+ slack, here 0).
drive_dim = routing.GetDimensionOrDie("Drive")
index = routing.Start(0)
print("crew 0, stop by stop:")
while not routing.IsEnd(index):
    following = solution.Value(routing.NextVar(index))
    print(f"  {places[manager.IndexToNode(index)].name:5} drive cumul {solution.Value(drive_dim.CumulVar(index)):3}"
          f"  transit to next {routing.GetArcCostForVehicle(index, following, 0):3}")
    index = following
print(f"  YARD  drive cumul {solution.Value(drive_dim.CumulVar(index)):3}  (route end)")
