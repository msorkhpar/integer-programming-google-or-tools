from __future__ import annotations


def plan_trims(circuits: dict[str, tuple[int, int]], cycle: int, capacity: int,
               years: list[int]) -> dict[int, tuple[list[str], int]]:
    """Year -> (circuits trimmed that year, sorted; miles due but left untrimmed at year end)."""
    # TODO: year by year, find the circuits due, trim what the crews can, and carry the rest.
    # Every entry below is a placeholder.
    return {y: ([], 0) for y in years}


if __name__ == "__main__":
    print(plan_trims({"A": (50, 2018), "B": (10, 2019), "C": (10, 2020)}, 3, 25, [2024, 2025]))
