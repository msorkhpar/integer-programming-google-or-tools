"""Four crews, all 18 Valley sites, an 08:00-16:00 shift, on-site inspection time and access windows.

Adapted onto GridCap from the OR-Tools example vrp_time_windows.py,
https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_time_windows.py
The drive times are fictional (valley.py invents the map from a seed).
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import SHIFT, clock, drive_minutes, sites

places = sites()
minutes = drive_minutes(places)
CREWS, KITS_PER_TRUCK, MAX_WAIT, YARD = 4, 9, 120, 0


def build(count_service: bool):
    manager = pywrapcp.RoutingIndexManager(len(places), CREWS, YARD)
    routing = pywrapcp.RoutingModel(manager)

    def drive(from_index, to_index):
        return minutes[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    drive_index = routing.RegisterTransitCallback(drive)
    routing.SetArcCostEvaluatorOfAllVehicles(drive_index)       # the objective: total drive minutes

    def busy(from_index, to_index):
        """Time from arriving at one stop to arriving at the next: inspect it, then drive."""
        here = manager.IndexToNode(from_index)
        service = places[here].service if count_service else 0
        return service + minutes[here][manager.IndexToNode(to_index)]

    busy_index = routing.RegisterTransitCallback(busy)
    # Time: the clock in minutes after 08:00. Up to MAX_WAIT minutes of waiting (slack) at a stop,
    # no clock value past the end of the shift, and the crews' departure time left free.
    routing.AddDimension(busy_index, MAX_WAIT, SHIFT, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for node in range(1, len(places)):
        time_dim.CumulVar(manager.NodeToIndex(node)).SetRange(*places[node].window)
    for crew in range(CREWS):
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(routing.Start(crew)))
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(routing.End(crew)))

    kits_index = routing.RegisterUnaryTransitCallback(lambda i: places[manager.IndexToNode(i)].kits)
    routing.AddDimensionWithVehicleCapacity(kits_index, 0, [KITS_PER_TRUCK] * CREWS, True, "Kits")

    parameters = pywrapcp.DefaultRoutingSearchParameters()
    parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    return manager, routing, routing.SolveWithParameters(parameters)


def schedule(manager, routing, solution, count_service: bool) -> None:
    time_dim = routing.GetDimensionOrDie("Time")
    print(f"objective (drive minutes) {solution.ObjectiveValue()}")
    for crew in range(CREWS):
        index, legs, waited = routing.Start(crew), [], 0
        while True:
            arrive = time_dim.CumulVar(index)
            site = places[manager.IndexToNode(index)]
            legs.append(f"{site.name} {clock(solution.Min(arrive))}-{clock(solution.Max(arrive))}")
            if routing.IsEnd(index):
                break
            following = solution.Value(routing.NextVar(index))
            here, after = manager.IndexToNode(index), manager.IndexToNode(following)
            transit = (site.service if count_service else 0) + minutes[here][after]
            waited += solution.Min(time_dim.CumulVar(following)) - solution.Min(arrive) - transit
            index = following
        print(f"  crew {crew}: {' > '.join(legs)}  (waits {waited} min)")
        if not count_service:
            replay(manager, routing, solution, crew)


def replay(manager, routing, solution, crew: int) -> None:
    """Drive the crew's route with the real inspection times: when is it back, which windows does it miss?"""
    index, clock_now, missed = routing.Start(crew), 0, []
    while not routing.IsEnd(index):
        here = manager.IndexToNode(index)
        following = solution.Value(routing.NextVar(index))
        clock_now += places[here].service + minutes[here][manager.IndexToNode(following)]
        site = places[manager.IndexToNode(following)]
        clock_now = max(clock_now, site.window[0])          # wait if the site is not open yet
        if clock_now > site.window[1]:
            missed.append(site.name)
        index = following
    print(f"           with real inspection times: back at {clock(clock_now)}, windows missed: {missed or 'none'}")


if __name__ == "__main__":
    print("with inspection time in the time callback:")
    schedule(*build(count_service=True), count_service=True)
    print("travel only, inspection time forgotten:")
    schedule(*build(count_service=False), count_service=False)
