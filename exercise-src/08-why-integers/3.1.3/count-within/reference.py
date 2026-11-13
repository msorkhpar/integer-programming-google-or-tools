from __future__ import annotations


def count_within(costs: list[int], budget: int) -> int:
    """How many subsets of the projects cost at most `budget`, with a table over budget amounts."""
    ways = [1] + [0] * budget
    for c in costs:
        for b in range(budget, c - 1, -1):
            ways[b] += ways[b - c]
    return sum(ways)


if __name__ == "__main__":
    print(count_within([60, 70, 80], 100))
    print(count_within([30, 40], 70))
