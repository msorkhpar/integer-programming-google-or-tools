from __future__ import annotations


def value_change(segments: list[tuple[float, float, float]], rhs: float, delta: float) -> float | None:
    """The exact change in the optimal value when the right-hand side moves from rhs to rhs + delta."""
    target = rhs + delta
    if target < segments[0][0] or target > segments[-1][1]:
        return None
    lo, hi = min(rhs, target), max(rhs, target)
    total = 0.0
    for start, end, price in segments:
        overlap = min(end, hi) - max(start, lo)
        if overlap > 0:
            total += overlap * price
    return total if delta >= 0 else -total


if __name__ == "__main__":
    sweep = [(0, 40, 3.0), (40, 70, 2.0), (70, 100, 0.0)]
    print(value_change(sweep, 50, 10), value_change(sweep, 50, 30))
