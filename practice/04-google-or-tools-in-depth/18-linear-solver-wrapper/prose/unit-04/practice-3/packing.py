from __future__ import annotations

from ortools.math_opt.python import mathopt


def fewest_crews(sizes: list[int], season: int):
    """Pack every job (size in crew-months) into seasons of `season` crew-months, using as few as possible.

    Returns (number of seasons, [[job indices] for each season used]), or None if no packing exists.
    """
    # TODO: the bin-packing model in MathOpt, solved, and the seasons read back.
    return 0, []


if __name__ == "__main__":
    print(fewest_crews([3, 3, 2, 2, 2, 2], 7))
