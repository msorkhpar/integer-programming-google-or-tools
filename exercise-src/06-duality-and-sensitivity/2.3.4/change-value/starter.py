from __future__ import annotations


def value_change(segments: list[tuple[float, float, float]], rhs: float, delta: float) -> float | None:
    """The exact change in the optimal value when the right-hand side moves from rhs to rhs + delta."""
    # TODO: add up price x length over the part of each segment the move passes through.
    return 0.0


if __name__ == "__main__":
    sweep = [(0, 40, 3.0), (40, 70, 2.0), (70, 100, 0.0)]
    print(value_change(sweep, 50, 10), value_change(sweep, 50, 30))
