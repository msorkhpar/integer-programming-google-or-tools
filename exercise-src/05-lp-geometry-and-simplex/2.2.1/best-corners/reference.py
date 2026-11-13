from __future__ import annotations

TOL = 1e-9


def best_corners(corners: list[tuple[float, float]], c: tuple[float, float],
                 sense: str = "max") -> tuple[float | None, list[tuple[float, float]]]:
    """The best value of c[0]*x + c[1]*y over the corners, and every corner that reaches it, sorted."""
    if not corners:
        return None, []
    value = {p: c[0] * p[0] + c[1] * p[1] for p in corners}
    best = max(value.values()) if sense == "max" else min(value.values())
    return best, sorted(p for p in corners if abs(value[p] - best) <= TOL)


if __name__ == "__main__":
    square = [(0.0, 0.0), (0.0, 2.0), (2.0, 0.0), (2.0, 2.0)]
    print(best_corners(square, (1, 2)))
    print(best_corners(square, (1, 0), "min"))
