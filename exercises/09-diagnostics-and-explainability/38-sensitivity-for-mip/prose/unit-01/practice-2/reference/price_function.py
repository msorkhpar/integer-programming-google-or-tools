from __future__ import annotations

TOL = 1e-9


def is_dual_feasible(F: list[float], hours: list[int], silt: list[float]) -> bool:
    """True when F bounds every schedule: the subadditive dual's conditions for one <= row, maximized."""
    D = len(F) - 1
    if abs(F[0]) > TOL:
        return False                                            # F(0) = 0
    if D >= 1 and F[1] < -TOL:
        return False                                            # one unused hour: F(1) >= 0
    for d in range(D + 1):
        for e in range(D + 1 - d):
            if F[d] + F[e] > F[d + e] + TOL:
                return False                                    # superadditive: F(d) + F(e) <= F(d + e)
    return all(F[a] >= c - TOL for a, c in zip(hours, silt))      # every column: F(a_j) >= c_j


if __name__ == "__main__":
    print(is_dual_feasible([0, 0, 3, 3, 6], [2], [3]))
