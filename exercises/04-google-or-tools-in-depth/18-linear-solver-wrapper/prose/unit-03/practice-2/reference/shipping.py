from __future__ import annotations

from ortools.graph.python import min_cost_flow


def ship(stock: dict, needs: dict, routes: dict):
    """The cheapest shipment meeting every town's need from the yards' stock.

    routes: {(from, to): (cost per unit, capacity)}. Returns (cost, {(from, to): units}) listing the
    routes that carry something, or None if the needs cannot all be met. Stock may exceed needs.
    """
    names = sorted({n for route in routes for n in route} | set(stock) | set(needs))
    node = {name: i for i, name in enumerate(names)}
    smcf = min_cost_flow.SimpleMinCostFlow()
    arcs = {}
    for (i, j), (cost, capacity) in routes.items():
        arcs[i, j] = smcf.add_arc_with_capacity_and_unit_cost(node[i], node[j], capacity, cost)
    for yard, units in stock.items():
        smcf.set_node_supply(node[yard], units)
    for town, units in needs.items():
        smcf.set_node_supply(node[town], -units)
    if smcf.solve_max_flow_with_min_cost() != smcf.OPTIMAL:
        return None
    if smcf.maximum_flow() < sum(needs.values()):
        return None
    return smcf.optimal_cost(), {route: smcf.flow(arc) for route, arc in arcs.items() if smcf.flow(arc) > 0}


if __name__ == "__main__":
    print(ship({"North yard": 5}, {"Elm": 3}, {("North yard", "Elm"): (2, 4)}))
