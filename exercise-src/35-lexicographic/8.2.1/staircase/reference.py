from __future__ import annotations


def steps(best: float, sweep: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    """One (allowed, taken, gain) per step of the sweep, smallest allowance first."""
    found: list[tuple[float, float, float]] = []
    base = top = None
    for allowed, first, second in sorted(sweep, key=lambda row: row[0]):
        if base is None:
            base = top = second
        elif second <= top:
            continue
        found.append((allowed, best - first, second - base))
        top = second
    return found


if __name__ == "__main__":
    sweep = [(0, 500, 40), (5, 496, 52), (10, 496, 52), (20, 482, 61)]
    for step in steps(500, sweep):
        print(step)
