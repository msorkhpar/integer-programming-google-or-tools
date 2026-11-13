from __future__ import annotations


def is_dual_feasible(F: list[float], hours: list[int], silt: list[float]) -> bool:
    """True when F bounds every schedule: the subadditive dual's conditions for one <= row, maximized."""
    # TODO: write the conditions in symbols first, then check each one.
    return False


if __name__ == "__main__":
    print(is_dual_feasible([0, 0, 3, 3, 6], [2], [3]))
