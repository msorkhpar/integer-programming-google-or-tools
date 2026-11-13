from __future__ import annotations


def optimum_range(incumbent: float | None, waiting: list[float], tol: float = 1e-6):
    """(low, high, proven): the optimum lies in [low, high]; proven when the two ends meet."""
    # TODO: low is the incumbent; high is the largest of the incumbent and the waiting bounds.
    return 0.0, 0.0, False


if __name__ == "__main__":
    print(optimum_range(None, [812.5]))
    print(optimum_range(780.0, [812.5, 790.25]))
    print(optimum_range(805.0, [800.0]))
