from __future__ import annotations

from ortools.constraint_solver import pywrapcp


def add_time(routing, manager, travel: list[list[int]], service: list[int],
             windows: dict[int, tuple[int, int]], shift_end: int, max_wait: int) -> None:
    """A "Time" dimension: arrival times, with service at each stop, waiting of at most max_wait
    minutes per stop, an arrival window per node in `windows`, and everyone back by shift_end."""
    def busy(from_index, to_index):
        here = manager.IndexToNode(from_index)
        return service[here] + travel[here][manager.IndexToNode(to_index)]

    routing.AddDimension(routing.RegisterTransitCallback(busy), max_wait, shift_end, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for node, (opens, closes) in windows.items():
        time_dim.CumulVar(manager.NodeToIndex(node)).SetRange(opens, closes)


def build(travel, service, windows, shift_end, max_wait, vehicles=1):
    """Given: routes from the depot (node 0), priced in travel minutes, with the time rules added."""
    manager = pywrapcp.RoutingIndexManager(len(travel), vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def drive(from_index, to_index):
        return travel[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(drive))
    add_time(routing, manager, travel, service, windows, shift_end, max_wait)
    return manager, routing


if __name__ == "__main__":
    manager, routing = build([[0, 5, 9], [5, 0, 6], [9, 6, 0]], [0, 20, 20], {1: (0, 30), 2: (40, 90)}, 120, 30)
    print(routing.ReadAssignmentFromRoutes([[1, 2]], True) is not None)
