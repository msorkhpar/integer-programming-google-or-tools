from __future__ import annotations

import math


def children(bounds: dict[str, tuple[int, int]], name: str, value: float):
    """The down and up children of a node, split on `name` at its fractional LP value."""
    # TODO: the down child caps `name` at floor(value); the up child starts it at ceil(value).
    # Each child keeps the other end of the node's range, and every other variable's bounds.
    return dict(bounds), dict(bounds)


if __name__ == "__main__":
    node = {"trucks_north": (0, 8), "open_south": (0, 1)}
    print(children(node, "trucks_north", 2.75))
