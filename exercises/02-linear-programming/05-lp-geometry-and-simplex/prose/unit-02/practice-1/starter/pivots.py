from __future__ import annotations

EPS = 1e-9


def choose_pivot(T: list[list[float]]) -> tuple[int, int] | None:
    """The (row, column) of the next pivot by Dantzig's rule and the ratio test, or None at an optimum."""
    # TODO: the entering column is the most negative objective-row entry (None if none is below -EPS);
    # the leaving row has the smallest rhs / entry over entries above EPS, the lowest row on a tie.
    return 0, 0


if __name__ == "__main__":
    T = [[1, 1, 1, 0, 5],
         [2, 1, 0, 1, 8],
         [-3, -2, 0, 0, 0]]
    print(choose_pivot(T))
