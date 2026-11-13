from __future__ import annotations

from ortools.graph.python import max_flow


def most_delivered(stock: dict, needs: dict, routes: dict) -> int:
    """The most units that can reach the towns: from yards holding `stock`, along `routes`
    {(from, to): capacity}, to towns that take at most `needs`."""
    # TODO: number the places, add a super source and a super sink, and solve one max flow.
    return 0


if __name__ == "__main__":
    print(most_delivered({"North yard": 6}, {"Elm": 4}, {("North yard", "Elm"): 5}))
