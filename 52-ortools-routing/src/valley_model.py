"""The whole Valley inspection model in one builder, for the programs of lessons 4.8.3 to 4.8.5.

Every piece is one the lessons teach: drive minutes as the arc cost (4.8.1), a kits dimension (4.8.2),
a time dimension with inspection time, waiting and windows (4.8.3), a soft finish time (4.8.3) and
optional low-priority visits (4.8.4). The drive times are fictional (valley.py invents the map).
"""

from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import SHIFT, Site, clock, drive_minutes

MAX_WAIT = 120


def build(places: list[Site], crews: int, kits_per_truck: int, *, finish_by: int | None = None,
          late_cost: int = 0, penalty=None):
    """The manager and routing model. `penalty(site)` gives a low-priority site's drop penalty;
    with no `penalty`, every site must be visited."""
    manager = pywrapcp.RoutingIndexManager(len(places), crews, 0)
    routing = pywrapcp.RoutingModel(manager)
    minutes = drive_minutes(places)

    def drive(from_index, to_index):
        return minutes[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    def busy(from_index, to_index):
        here = manager.IndexToNode(from_index)
        return places[here].service + minutes[here][manager.IndexToNode(to_index)]

    def kits(from_index):
        return places[manager.IndexToNode(from_index)].kits

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(drive))
    routing.AddDimension(routing.RegisterTransitCallback(busy), MAX_WAIT, SHIFT, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for node in range(1, len(places)):
        time_dim.CumulVar(manager.NodeToIndex(node)).SetRange(*places[node].window)
    for crew in range(crews):
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(routing.Start(crew)))
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(routing.End(crew)))
        if finish_by is not None:
            time_dim.SetCumulVarSoftUpperBound(routing.End(crew), finish_by, late_cost)
    routing.AddDimensionWithVehicleCapacity(
        routing.RegisterUnaryTransitCallback(kits), 0, [kits_per_truck] * crews, True, "Kits")

    if penalty is not None:
        for node in range(1, len(places)):
            if not places[node].urgent:                       # urgent sites stay mandatory
                routing.AddDisjunction([manager.NodeToIndex(node)], penalty(places[node]))
    return manager, routing


def parameters(strategy: str = "PATH_CHEAPEST_ARC", metaheuristic: str | None = None,
               solution_limit: int | None = None):
    """Search parameters by name. A metaheuristic gets a solution limit, never a time limit, so runs repeat."""
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = getattr(routing_enums_pb2.FirstSolutionStrategy, strategy)
    if metaheuristic:
        params.local_search_metaheuristic = getattr(routing_enums_pb2.LocalSearchMetaheuristic, metaheuristic)
    if solution_limit:
        params.solution_limit = solution_limit
    return params


def routes(manager, routing, solution) -> list[list[int]]:
    """Each crew's visited nodes, yard excluded (the shape ReadAssignmentFromRoutes takes back)."""
    out = []
    for crew in range(routing.vehicles()):
        index, nodes = solution.Value(routing.NextVar(routing.Start(crew))), []
        while not routing.IsEnd(index):
            nodes.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        out.append(nodes)
    return out


def dropped(manager, routing, solution) -> list[int]:
    """Nodes on no route: a dropped visit's next variable points back to itself."""
    return [manager.IndexToNode(index) for index in range(routing.Size())
            if not routing.IsStart(index) and not routing.IsEnd(index)
            and solution.Value(routing.NextVar(index)) == index]


def show(places: list[Site], manager, routing, solution) -> None:
    time_dim = routing.GetDimensionOrDie("Time")
    for crew, nodes in enumerate(routes(manager, routing, solution)):
        back = solution.Min(time_dim.CumulVar(routing.End(crew)))
        print(f"  crew {crew}: {' > '.join(places[n].name for n in nodes) or '(stays at the yard)'}"
              f"  back {clock(back)}")
