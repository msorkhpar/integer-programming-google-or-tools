from __future__ import annotations

from itertools import product


def smallest_raise(years: dict[str, list[int]], cost: dict[str, int], caps: dict[int, int]) -> tuple[int, dict[str, int]]:
    """The least total budget increase that lets every job in the conflict be done, and the years that achieve it."""
    # TODO: try every combination of years, and keep the one that needs the least extra money.
    return 0, {job: options[0] for job, options in years.items()}


if __name__ == "__main__":
    print(smallest_raise({"R12": [2027, 2028], "R31": [2027]}, {"R12": 700, "R31": 600}, {2027: 1000, 2028: 500}))
