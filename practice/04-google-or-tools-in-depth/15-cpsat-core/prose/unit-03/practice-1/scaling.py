from __future__ import annotations

import math
from fractions import Fraction


def scale_row(coefficients: list[str], rhs: str, sense: str) -> tuple[list[int], int | None]:
    """A row with decimal data -> whole coefficients and a whole bound that allow the same integer points.

    sense is "<=", ">=" or "==". For "==", the bound is None when no integer point can meet it.
    """
    # TODO: one multiplier for the whole row, then the bound for the row's sense.
    return [], None

if __name__ == "__main__":
    print(scale_row(["1.5", "0.25", "2"], "4.6", "<="))
