"""One random stream for a whole portfolio, or one stream per project: what a new draw does to each.

A toy generator of (cost, earliest start) pairs, written two ways. Version 2 adds one draw, a crew
size, for distribution projects only. With one shared stream, that draw shifts every later
project; with a stream per project, only the projects that take the new draw change. The toy's
numbers are invented, like GridCap's.
"""

from __future__ import annotations

import random

KINDS = ("transmission", "distribution", "vegetation")


def shared_stream(n: int, seed: int, version: int = 1) -> list[tuple]:
    draw = random.Random(seed)
    out = []
    for _ in range(n):
        kind = KINDS[min(int(draw.random() * 3), 2)]
        cost = 100 + int(draw.random() * 900)
        start = 2027 + int(draw.random() * 5)
        if version == 2 and kind == "distribution":
            draw.random()                       # the new draw: a crew size, unused here
        out.append((kind, cost, start))
    return out


def stream_per_project(n: int, seed: int, version: int = 1) -> list[tuple]:
    out = []
    for i in range(n):
        draw = random.Random(seed * 1_000_000 + i)   # project i's own stream: below a million projects, no two share one
        kind = KINDS[min(int(draw.random() * 3), 2)]
        cost = 100 + int(draw.random() * 900)
        start = 2027 + int(draw.random() * 5)
        if version == 2 and kind == "distribution":
            draw.random()
        out.append((kind, cost, start))
    return out


def changed(a: list[tuple], b: list[tuple]) -> list[int]:
    return [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y]


if __name__ == "__main__":
    for name, gen in (("one shared stream", shared_stream), ("a stream per project", stream_per_project)):
        v1, v2 = gen(8, seed=7), gen(8, seed=7, version=2)
        print(f"{name}:")
        print("  version 1:", " ".join(f"{k[0][0]}{c}/{s}" for k, c, s in v1))
        print("  version 2:", " ".join(f"{k[0][0]}{c}/{s}" for k, c, s in v2))
        print("  projects that changed:", changed(v1, v2))
        print("  first 8 of 10,000 equal the 8:", gen(10_000, seed=7)[:8] == v1)
