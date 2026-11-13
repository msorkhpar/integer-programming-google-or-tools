from __future__ import annotations

from ortools.graph.python import min_cost_flow


def ship(stock: dict, needs: dict, routes: dict):
    """The cheapest shipment meeting every town's need from the yards' stock.

    routes: {(from, to): (cost per unit, capacity)}. Returns (cost, {(from, to): units}) listing the
    routes that carry something, or None if the needs cannot all be met. Stock may exceed needs.
    """
    # TODO: number the places, add the routes and supplies, solve, and check every need is met.
    return 0, {route: 0 for route in routes}


if __name__ == "__main__":
    print(ship({"North yard": 5}, {"Elm": 3}, {("North yard", "Elm"): (2, 4)}))
