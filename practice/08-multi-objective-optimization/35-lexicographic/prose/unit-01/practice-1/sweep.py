from __future__ import annotations


def steps(best: float, sweep: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    """One (allowed, taken, gain) per step of the sweep, smallest allowance first."""
    # TODO: sort by allowance, keep the rows that improve on `second`, and measure each one.
    return []


if __name__ == "__main__":
    sweep = [(0, 500, 40), (5, 496, 52), (10, 496, 52), (20, 482, 61)]
    for step in steps(500, sweep):
        print(step)
