from __future__ import annotations

import math


def verdict(primal: float, dual: float, tolerance: float, sense: str, integral: bool) -> tuple[float, bool]:
    """The relative gap between incumbent and bound, and whether it is within the tolerance."""
    if integral:
        dual = math.floor(dual + 1e-9) if sense == "max" else math.ceil(dual - 1e-9)
    gap = abs(dual - primal) / abs(primal)
    return gap, gap <= tolerance


if __name__ == "__main__":
    print(verdict(41000, 41004.6, 1e-4, "max", True))
