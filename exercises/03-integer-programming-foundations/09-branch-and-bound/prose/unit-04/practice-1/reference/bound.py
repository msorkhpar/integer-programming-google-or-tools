from __future__ import annotations


def bound(items: list[tuple[str, int, int]], budget: float, fixed: dict[str, int]):
    """(LP value, split item or None) at a node, or None when the fixings are over budget."""
    left = budget - sum(cost for name, _, cost in items if fixed.get(name) == 1)
    if left < 0:
        return None
    value = float(sum(v for name, v, _ in items if fixed.get(name) == 1))
    free = [it for it in items if it[0] not in fixed]
    for name, v, cost in sorted(free, key=lambda it: (-it[1] / it[2], it[0])):
        if cost <= left:
            left -= cost
            value += v
        else:
            if left > 0:
                return value + v * left / cost, name
            return value, None
    return value, None


if __name__ == "__main__":
    spares = [("T1", 120, 40), ("T2", 100, 50), ("T3", 45, 45), ("T4", 30, 60)]
    print(bound(spares, 70, {}))
    print(bound(spares, 70, {"T2": 1}))
