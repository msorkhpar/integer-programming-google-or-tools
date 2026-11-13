from __future__ import annotations


def count_within(costs: list[int], budget: int) -> int:
    """How many subsets of the projects cost at most `budget`, with a table over budget amounts."""
    # TODO: ways[b] = how many subsets of the projects seen so far cost exactly b.
    return 0


if __name__ == "__main__":
    print(count_within([60, 70, 80], 100))
    print(count_within([30, 40], 70))
