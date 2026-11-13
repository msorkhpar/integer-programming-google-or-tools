from __future__ import annotations

from ortools.constraint_solver import pywrapcp


def add_drive_limits(routing, drive_index: int, shifts: list[int]) -> None:
    """Each crew v drives at most shifts[v] minutes, the drive back to the yard included."""
    # TODO: one dimension that adds up each crew's drive minutes, capped per crew.
    return None


def build(drive: list[list[int]], shifts: list[int]):
    """Given: one route per crew from the yard (node 0), priced in drive minutes."""
    manager = pywrapcp.RoutingIndexManager(len(drive), len(shifts), 0)
    routing = pywrapcp.RoutingModel(manager)

    def minutes(from_index, to_index):
        return drive[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    drive_index = routing.RegisterTransitCallback(minutes)
    routing.SetArcCostEvaluatorOfAllVehicles(drive_index)
    add_drive_limits(routing, drive_index, shifts)
    return manager, routing


if __name__ == "__main__":
    manager, routing = build([[0, 20, 30], [20, 0, 15], [30, 15, 0]], [60, 40])
    print(routing.ReadAssignmentFromRoutes([[1, 2], []], True) is not None)
