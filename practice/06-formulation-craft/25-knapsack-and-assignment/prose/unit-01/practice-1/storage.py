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
    # TODO: a table over MWh amounts, then read one cheapest set back from it.
    return 0, []

if __name__ == "__main__":
    print(cheapest_cover([Site("North", 4, 30), Site("Quarry", 6, 40), Site("Depot", 3, 25)], 7))
