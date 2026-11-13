from __future__ import annotations

from ortools.graph.python import max_flow


def most_delivered(stock: dict, needs: dict, routes: dict) -> int:
    """The most units that can reach the towns: from yards holding `stock`, along `routes`
    {(from, to): capacity}, to towns that take at most `needs`."""
    names = sorted({n for route in routes for n in route} | set(stock) | set(needs))
    node = {name: i for i, name in enumerate(names)}
    source, sink = len(names), len(names) + 1
    smf = max_flow.SimpleMaxFlow()
    for yard, units in stock.items():
        smf.add_arc_with_capacity(source, node[yard], units)
    for (i, j), capacity in routes.items():
        smf.add_arc_with_capacity(node[i], node[j], capacity)
    for town, units in needs.items():
        smf.add_arc_with_capacity(node[town], sink, units)
    if smf.solve(source, sink) != smf.OPTIMAL:
        raise RuntimeError("max flow failed")
    return smf.optimal_flow()


if __name__ == "__main__":
    print(most_delivered({"North yard": 6}, {"Elm": 4}, {("North yard", "Elm"): 5}))
