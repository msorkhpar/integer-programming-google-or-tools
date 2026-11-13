from __future__ import annotations

import math
from fractions import Fraction


def scale_row(coefficients: list[str], rhs: str, sense: str) -> tuple[list[int], int | None]:
    """A row with decimal data -> whole coefficients and a whole bound that allow the same integer points.

    sense is "<=", ">=" or "==". For "==", the bound is None when no integer point can meet it.
    """
    exact = [Fraction(c) for c in coefficients]
    multiplier = math.lcm(*(f.denominator for f in exact))
    whole = [int(f * multiplier) for f in exact]
    bound = Fraction(rhs) * multiplier
    if sense == "<=":
        return whole, math.floor(bound)
    if sense == ">=":
        return whole, math.ceil(bound)
    return whole, int(bound) if bound.denominator == 1 else None


if __name__ == "__main__":
    print(scale_row(["1.5", "0.25", "2"], "4.6", "<="))
