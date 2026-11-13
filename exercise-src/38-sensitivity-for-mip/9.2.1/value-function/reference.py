from __future__ import annotations


def value_function(days: list[int], worth: list[int], limits: list[int], capacity: int) -> list[int]:
    """z(d) for d = 0..capacity: the best worth of lots that fit in d crew-days, each type within its limit."""
    z = [0] * (capacity + 1)                     # z[d] = 0: buying nothing always fits
    for a, c, u in zip(days, worth, limits):
        for _ in range(u):                       # each copy of the type is one more item, taken or left
            for d in range(capacity, a - 1, -1):     # downwards, so this copy is used at most once
                z[d] = max(z[d], z[d - a] + c)
    return z


if __name__ == "__main__":
    print(value_function([3, 5], [4, 7], [2, 1], 12))
