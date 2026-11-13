"""Count the nodes of a depth-first search over yes/no choices, with and without an LP bound to prune.

Lesson 3.1.3 counts; module 09 builds this search properly as branch-and-bound.
"""

import sys

from gridcap import generate

sys.setrecursionlimit(5000)


def lp_bound(items: list[tuple[int, int]], room: int) -> float:
    """The best value of the rest with fractions allowed: items are sorted best value per dollar first."""
    total = 0.0
    for cost, value in items:
        if cost <= room:
            room -= cost
            total += value
        else:
            return total + value * room / cost
    return total


def search(items: list[tuple[int, int]], budget: int, prune: bool) -> tuple[int, int]:
    """Best value and nodes visited. Each node decides one item: fund it (if it fits), then skip it."""
    items = sorted(items, key=lambda cv: cv[1] / cv[0], reverse=True)
    best, nodes = 0, 0

    def visit(k: int, room: int, value: int) -> None:
        nonlocal best, nodes
        nodes += 1
        if k == len(items):
            best = max(best, value)
            return
        if prune and value + lp_bound(items[k:], room) <= best:
            return                                       # nothing below this node can beat the best plan
        cost, worth = items[k]
        if cost <= room:
            visit(k + 1, room - cost, value + worth)
        visit(k + 1, room, value)

    visit(0, budget, 0)
    return best, nodes


def half_budget(items: list[tuple[int, int]]) -> int:
    return sum(c for c, _ in items) // 2


if __name__ == "__main__":
    medium = generate("medium")
    print("nodes visited, first n projects of GridCap medium, budget half their cost:")
    print(f"{'n':>4}{'full tree':>11}{'budget only':>13}{'with bound':>12}")
    for n in (10, 15, 20, 25):
        items = [(p.capex, p.value) for p in medium.projects[:n]]
        _, plain = search(items, half_budget(items), prune=False)
        best, pruned = search(items, half_budget(items), prune=True)
        print(f"{n:>4}{2 ** (n + 1) - 1:>11,}{plain:>13,}{pruned:>12,}")
    for n in (100, 400):
        items = [(p.capex, p.value) for p in medium.projects[:n]]
        best, pruned = search(items, half_budget(items), prune=True)
        print(f"{n:>4}{2 ** (n + 1) - 1:>11.1e}{'-':>13}{pruned:>12,}")
    print("same costs, every item worth exactly its cost:")
    for n in (10, 15, 20, 25):
        items = [(p.capex, p.capex) for p in medium.projects[:n]]
        best, pruned = search(items, half_budget(items) // 10 * 10 + 5, prune=True)   # no plan spends it all
        print(f"{n:>4}{2 ** (n + 1) - 1:>11,}{'':>13}{pruned:>12,}")
