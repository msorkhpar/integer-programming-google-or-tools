from __future__ import annotations

import math


def verdict(primal: float, dual: float, tolerance: float, sense: str, integral: bool) -> tuple[float, bool]:
    """The relative gap between incumbent and bound, and whether it is within the tolerance."""
    # TODO: with an integral objective, round the bound toward the incumbent (floor for max, ceil
    # for min); then compute |dual - primal| / |primal| and compare it with the tolerance.
    return 0.0, False


if __name__ == "__main__":
    print(verdict(41000, 41004.6, 1e-4, "max", True))
