from __future__ import annotations

from ortools.math_opt.python import mathopt


def separate_floor(km: dict[str, int], floor: int, xstar: dict[str, float]) -> list[str] | None:
    """A set of lines the LP point under-uses although every plan meeting the floor needs one of them.

    A set C is needed when the lines outside it add up to less than the floor: then every plan that
    inspects at least `floor` km includes a line of C, so sum over C of x >= 1 holds for whole plans.
    Returns the needed set with the smallest LP sum when that sum is below 1, else None.
    """
    # TODO: find the needed set the LP point under-uses most.
    return None

if __name__ == "__main__":
    print(separate_floor({"L1": 10, "L2": 3, "L3": 2}, 8, {"L1": 0.5, "L2": 1.0, "L3": 1.0}))
