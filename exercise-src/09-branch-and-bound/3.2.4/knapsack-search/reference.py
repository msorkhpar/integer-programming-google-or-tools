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
    must_cost = sum(c for n, _, c in items if n in must)
    must_value = sum(v for n, v, _ in items if n in must)
    if must_cost > budget:
        return None
    order = by_ratio([it for it in items if it[0] not in must])
    best_value, best = -1, []
    stack: list[dict[str, int]] = [{}]
    while stack:
        fixed = stack.pop()
        node = bound(order, budget - must_cost, fixed)
        if node is None:
            continue
        value, split, taken = node
        if math.floor(value + 1e-9) <= best_value:
            continue
        if split is None:
            best_value, best = round(value), taken
            continue
        stack.append({**fixed, split: 0})
        stack.append({**fixed, split: 1})
    return best_value + must_value, sorted(best + list(must))


if __name__ == "__main__":
    spares = [("T1", 120, 40), ("T2", 100, 50), ("T3", 45, 45), ("T4", 30, 60), ("R1", 10, 25)]
    print(best_plan(spares, 120, {"R1"}))
