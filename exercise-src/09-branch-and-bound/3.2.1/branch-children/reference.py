from __future__ import annotations

import math


def children(bounds: dict[str, tuple[int, int]], name: str, value: float):
    """The down and up children of a node, split on `name` at its fractional LP value."""
    lo, hi = bounds[name]
    down = dict(bounds)
    down[name] = (lo, math.floor(value))
    up = dict(bounds)
    up[name] = (math.ceil(value), hi)
    return down, up


if __name__ == "__main__":
    node = {"trucks_north": (0, 8), "open_south": (0, 1)}
    print(children(node, "trucks_north", 2.75))
