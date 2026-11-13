from __future__ import annotations


def value_function(days: list[int], worth: list[int], limits: list[int], capacity: int) -> list[int]:
    """z(d) for d = 0..capacity: the best worth of lots that fit in d crew-days, each type within its limit."""
    # TODO: write the recurrence, then fill the table.
    return [0] * (capacity + 1)


if __name__ == "__main__":
    print(value_function([3, 5], [4, 7], [2, 1], 12))
