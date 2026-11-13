from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Site:
    name: str
    mwh: int          # storage the site adds, whole MWh (at least 1)
    cost: int         # $k


def cheapest_cover(sites: list[Site], need: int) -> tuple[int, list[str]] | None:
    """The least total cost of a set of sites adding at least `need` MWh, and one such set.

    None when even every site together adds less than `need`.
    """
    inf = float("inf")
    cost = [0] + [inf] * need          # cost[c]: least cost of sites seen so far giving at least c MWh
    took = []
    for s in sites:
        row = [False] * (need + 1)
        for c in range(need, 0, -1):                    # downward: each site is bought at most once
            src = max(0, c - s.mwh)                     # overshooting the need is fine
            if cost[src] + s.cost < cost[c]:
                cost[c] = cost[src] + s.cost
                row[c] = True
        took.append(row)
    if cost[need] == inf:
        return None
    chosen, c = [], need
    for s, row in zip(reversed(sites), reversed(took)):
        if row[c]:
            chosen.append(s.name)
            c = max(0, c - s.mwh)
    return int(cost[need]), chosen[::-1]


if __name__ == "__main__":
    print(cheapest_cover([Site("North", 4, 30), Site("Quarry", 6, 40), Site("Depot", 3, 25)], 7))
