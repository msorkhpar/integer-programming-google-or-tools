from __future__ import annotations


def optimum_range(incumbent: float | None, waiting: list[float], tol: float = 1e-6):
    """(low, high, proven): the optimum lies in [low, high]; proven when the two ends meet."""
    candidates = list(waiting)
    if incumbent is not None:
        candidates.append(incumbent)
    high = max(candidates) if candidates else None
    if incumbent is None:
        return None, high, False
    return incumbent, high, high - incumbent <= tol


if __name__ == "__main__":
    print(optimum_range(None, [812.5]))
    print(optimum_range(780.0, [812.5, 790.25]))
    print(optimum_range(805.0, [800.0]))
