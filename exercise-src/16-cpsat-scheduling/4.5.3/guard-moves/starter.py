from __future__ import annotations

from ortools.sat.python import cp_model


def plan_nights(guards: list[str], need: list[dict[int, int]], cost: list[list[int]],
                forbidden: list[tuple[int, int]]) -> tuple[int, dict[tuple[str, int], int]]:
    """(total move cost, (guard, night) -> place) of the cheapest roster."""
    # TODO: one Boolean per guard, night and place, the place number, the need rows, the forbidden
    # moves and each move's cost read from the flattened table. Placeholders below.
    return -1, {(g, d): -1 for g in guards for d in range(len(need))}


if __name__ == "__main__":
    print(plan_nights(["ana", "ben"], [{0: 1, 1: 1}, {0: 1}, {1: 2}],
                      [[0, 3, 1], [3, 0, 1], [1, 1, 0]], [(0, 1)]))
