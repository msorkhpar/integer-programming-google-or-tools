from __future__ import annotations


def bound(items: list[tuple[str, int, int]], budget: float, fixed: dict[str, int]):
    """(LP value, split item or None) at a node, or None when the fixings are over budget."""
    # TODO: pay for the items fixed at 1 (None if that is over budget), skip those fixed at 0,
    # then fill the free items by value / cost, highest first, and take part of the first misfit.
    return 0.0, None


if __name__ == "__main__":
    spares = [("T1", 120, 40), ("T2", 100, 50), ("T3", 45, 45), ("T4", 30, 60)]
    print(bound(spares, 70, {}))
    print(bound(spares, 70, {"T2": 1}))
