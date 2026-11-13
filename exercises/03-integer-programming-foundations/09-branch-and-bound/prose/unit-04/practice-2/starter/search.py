from __future__ import annotations

import math


def by_ratio(items: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    """Best value per cost first; ties by name."""
    return sorted(items, key=lambda it: (-it[1] / it[2], it[0]))


def bound(order, budget: float, fixed: dict[str, int]):
    """Dantzig's bound at a node: (value, split or None, names whole in the LP), or None if infeasible.

    `order` is the free items in ratio order.
    """
    left = budget - sum(c for n, _, c in order if fixed.get(n) == 1)
    if left < 0:
        return None
    value = float(sum(v for n, v, _ in order if fixed.get(n) == 1))
    taken = [n for n, _, _ in order if fixed.get(n) == 1]
    for n, v, c in order:
        if n in fixed:
            continue
        if c <= left:
            left -= c
            value += v
            taken.append(n)
        elif left > 0:
            return value + v * left / c, n, taken
        else:
            break
    return value, None, taken


def best_plan(items: list[tuple[str, int, int]], budget: int, must: set[str]):
    """(total value, sorted names) of the best plan that stocks every item in `must`; None if impossible."""
    # TODO: pay for the must-stock items first (None if they do not fit), sort the rest once with
    # by_ratio, then run the depth-first search over a stack of fixings using bound(). Add the
    # must-stock items back into the value and the names at the end.
    return -1, []


if __name__ == "__main__":
    spares = [("T1", 120, 40), ("T2", 100, 50), ("T3", 45, 45), ("T4", 30, 60), ("R1", 10, 25)]
    print(best_plan(spares, 120, {"R1"}))
