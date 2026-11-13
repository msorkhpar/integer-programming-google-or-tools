from __future__ import annotations

from ortools.graph.python import min_cost_flow


def ship(lanes: list[tuple[int, int, int, int]], supply: dict[int, int]) -> int | str:
    """The least total cost, or the status name when the solver's status is not OPTIMAL."""
    flow = min_cost_flow.SimpleMinCostFlow()
    for tail, head, capacity, cost in lanes:
        flow.add_arc_with_capacity_and_unit_cost(tail, head, capacity, cost)
    for node, amount in supply.items():
        flow.set_node_supply(node, amount)
    status = flow.solve()
    if status != flow.OPTIMAL:
        return status.name
    return flow.optimal_cost()


if __name__ == "__main__":
    print(ship([(0, 1, 5, 2), (0, 2, 5, 4), (2, 1, 5, 1)], {0: 7, 1: -7}))
