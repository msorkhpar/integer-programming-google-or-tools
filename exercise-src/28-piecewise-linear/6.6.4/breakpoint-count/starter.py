from __future__ import annotations

from typing import Callable


def fewest_breakpoints(f: Callable[[float], float], lo: float, hi: float, tol: float,
                       max_n: int = 65) -> int | None:
    """The fewest equally spaced breakpoints whose curve stays within `tol` of f on [lo, hi]."""
    # TODO: build the curve for n = 2, 3, ... and measure its gap on the 1,001 points.
    return max_n


if __name__ == "__main__":
    print(fewest_breakpoints(lambda x: x * x, 0.0, 1.0, 0.011))
