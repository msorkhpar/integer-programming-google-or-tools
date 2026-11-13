from __future__ import annotations

TOL = 1e-9


def best_corners(corners: list[tuple[float, float]], c: tuple[float, float],
                 sense: str = "max") -> tuple[float | None, list[tuple[float, float]]]:
    """The best value of c[0]*x + c[1]*y over the corners, and every corner that reaches it, sorted."""
    # TODO: value every corner, take the max (or the min when sense is "min"), and return it with
    # every corner within TOL of it. No corners means no region: (None, []).
    return 0.0, []


if __name__ == "__main__":
    square = [(0.0, 0.0), (0.0, 2.0), (2.0, 0.0), (2.0, 2.0)]
    print(best_corners(square, (1, 2)))
    print(best_corners(square, (1, 0), "min"))
